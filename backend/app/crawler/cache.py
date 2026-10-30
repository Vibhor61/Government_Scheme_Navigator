"""
Persistent SQLite & High-Speed Multi-Tier Cache for Crawler Agent
Provides Persistent SQLite Disk Storage + Memory LRU caching.
Ensures crawled schemes, HTML documents, and metadata permanently survive:
- Server reboots & Docker container recreations
- Cold-starts in production deployments
- Sub-5ms lookups for frequent scheme inquiries
- Live tracking of Hits, Misses, and Bandwidth savings
"""

import os
import json
import time
import hashlib
import sqlite3
from typing import Optional, Dict, Any, List
from collections import OrderedDict

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_storage")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_DB_FILE = os.path.join(CACHE_DIR, "crawler_cache.sqlite")


class CrawlerCache:
    def __init__(self, max_memory_entries: int = 500, default_ttl_seconds: int = 86400):
        self.max_memory_entries = max_memory_entries
        self.default_ttl = default_ttl_seconds
        self.memory_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        
        # Performance Counters
        self.hits: int = 0
        self.misses: int = 0
        self.saved_bandwidth_bytes: int = 0
        
        # Initialize SQLite storage
        self._init_sqlite_db()
        self._load_from_sqlite()

    def _get_db_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(CACHE_DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_db(self):
        """Initializes persistent SQLite schema for crawler cache and metrics."""
        try:
            with self._get_db_conn() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS crawler_cache_entries (
                        key_hash TEXT PRIMARY KEY,
                        url TEXT NOT NULL,
                        cached_at REAL NOT NULL,
                        last_accessed REAL NOT NULL,
                        ttl INTEGER NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        access_count INTEGER NOT NULL DEFAULT 1,
                        metadata_json TEXT,
                        data_json TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS crawler_cache_stats (
                        id INTEGER PRIMARY KEY,
                        hits INTEGER DEFAULT 0,
                        misses INTEGER DEFAULT 0,
                        saved_bandwidth_bytes INTEGER DEFAULT 0
                    );
                """)
                conn.execute("""
                    INSERT OR IGNORE INTO crawler_cache_stats (id, hits, misses, saved_bandwidth_bytes)
                    VALUES (1, 0, 0, 0);
                """)
                conn.commit()
        except Exception as e:
            print(f"[Cache SQLite] Error initializing table: {e}")

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.strip().lower().encode("utf-8")).hexdigest()

    def _load_from_sqlite(self):
        """Restores cache and counters from persistent SQLite storage upon startup."""
        try:
            with self._get_db_conn() as conn:
                # Load stats
                stat_row = conn.execute("SELECT hits, misses, saved_bandwidth_bytes FROM crawler_cache_stats WHERE id = 1;").fetchone()
                if stat_row:
                    self.hits = stat_row["hits"]
                    self.misses = stat_row["misses"]
                    self.saved_bandwidth_bytes = stat_row["saved_bandwidth_bytes"]

                # Load active unexpired entries into memory
                now = time.time()
                rows = conn.execute(
                    "SELECT * FROM crawler_cache_entries ORDER BY last_accessed ASC LIMIT ?;",
                    (self.max_memory_entries,)
                ).fetchall()

                for r in rows:
                    if now - r["cached_at"] < r["ttl"]:
                        try:
                            self.memory_cache[r["key_hash"]] = {
                                "key": r["url"],
                                "key_hash": r["key_hash"],
                                "cached_at": r["cached_at"],
                                "last_accessed": r["last_accessed"],
                                "ttl": r["ttl"],
                                "size_bytes": r["size_bytes"],
                                "access_count": r["access_count"],
                                "metadata": json.loads(r["metadata_json"]) if r["metadata_json"] else {},
                                "data": json.loads(r["data_json"])
                            }
                        except Exception:
                            pass
        except Exception as e:
            print(f"[Cache SQLite] Error loading cache from disk: {e}")

    def _persist_entry_to_sqlite(self, entry: Dict[str, Any]):
        """Persists single cache entry to SQLite disk storage."""
        try:
            with self._get_db_conn() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO crawler_cache_entries 
                    (key_hash, url, cached_at, last_accessed, ttl, size_bytes, access_count, metadata_json, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    entry["key_hash"],
                    entry["key"],
                    entry["cached_at"],
                    entry["last_accessed"],
                    entry["ttl"],
                    entry["size_bytes"],
                    entry.get("access_count", 1),
                    json.dumps(entry.get("metadata", {})),
                    json.dumps(entry["data"], default=str)
                ))
                conn.execute("""
                    UPDATE crawler_cache_stats 
                    SET hits = ?, misses = ?, saved_bandwidth_bytes = ?
                    WHERE id = 1;
                """, (self.hits, self.misses, self.saved_bandwidth_bytes))
                conn.commit()
        except Exception as e:
            print(f"[Cache SQLite] Error persisting entry: {e}")

    def get(self, url_or_key: str) -> Optional[Dict[str, Any]]:
        """Lookup key in cache. Returns cached payload if valid, else None."""
        key_hash = self._hash_key(url_or_key)
        now = time.time()
        
        # 1. Check Memory Cache
        if key_hash in self.memory_cache:
            entry = self.memory_cache[key_hash]
            if now - entry["cached_at"] < entry.get("ttl", self.default_ttl):
                self.hits += 1
                entry["last_accessed"] = now
                entry["access_count"] = entry.get("access_count", 0) + 1
                self.saved_bandwidth_bytes += entry.get("size_bytes", 1024)
                self.memory_cache.move_to_end(key_hash)
                self._update_stats_sqlite()
                return entry["data"]
            else:
                del self.memory_cache[key_hash]

        # 2. Check Persistent SQLite on Disk (in case of cold start)
        try:
            with self._get_db_conn() as conn:
                row = conn.execute(
                    "SELECT * FROM crawler_cache_entries WHERE key_hash = ?;",
                    (key_hash,)
                ).fetchone()

                if row and (now - row["cached_at"] < row["ttl"]):
                    self.hits += 1
                    self.saved_bandwidth_bytes += row["size_bytes"]
                    data = json.loads(row["data_json"])
                    
                    # Update accessed time in SQLite
                    conn.execute(
                        "UPDATE crawler_cache_entries SET last_accessed = ?, access_count = access_count + 1 WHERE key_hash = ?;",
                        (now, key_hash)
                    )
                    conn.commit()
                    
                    # Populate in memory
                    self.memory_cache[key_hash] = {
                        "key": row["url"],
                        "key_hash": key_hash,
                        "cached_at": row["cached_at"],
                        "last_accessed": now,
                        "ttl": row["ttl"],
                        "size_bytes": row["size_bytes"],
                        "access_count": row["access_count"] + 1,
                        "metadata": json.loads(row["metadata_json"]) if row["metadata_json"] else {},
                        "data": data
                    }
                    self._update_stats_sqlite()
                    return data
        except Exception as e:
            print(f"[Cache SQLite] Error checking disk cache: {e}")

        self.misses += 1
        self._update_stats_sqlite()
        return None

    def set(self, url_or_key: str, data: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """Stores entry into persistent SQLite disk storage and memory LRU."""
        key_hash = self._hash_key(url_or_key)
        now = time.time()
        ttl_val = ttl if ttl is not None else self.default_ttl
        size_bytes = len(json.dumps(data, default=str).encode("utf-8"))

        entry = {
            "key": url_or_key,
            "key_hash": key_hash,
            "cached_at": now,
            "last_accessed": now,
            "ttl": ttl_val,
            "size_bytes": size_bytes,
            "access_count": 1,
            "metadata": metadata or {},
            "data": data
        }

        # Memory LRU eviction if full
        if len(self.memory_cache) >= self.max_memory_entries:
            self.memory_cache.popitem(last=False)

        self.memory_cache[key_hash] = entry
        
        # Persist immediately to SQLite disk storage
        self._persist_entry_to_sqlite(entry)

    def _update_stats_sqlite(self):
        """Synchronizes hit/miss counters to persistent storage."""
        try:
            with self._get_db_conn() as conn:
                conn.execute("""
                    UPDATE crawler_cache_stats 
                    SET hits = ?, misses = ?, saved_bandwidth_bytes = ?
                    WHERE id = 1;
                """, (self.hits, self.misses, self.saved_bandwidth_bytes))
                conn.commit()
        except Exception:
            pass

    def clear(self):
        """Clears all cached entries and resets statistics."""
        self.memory_cache.clear()
        self.hits = 0
        self.misses = 0
        self.saved_bandwidth_bytes = 0
        try:
            with self._get_db_conn() as conn:
                conn.execute("DELETE FROM crawler_cache_entries;")
                conn.execute("UPDATE crawler_cache_stats SET hits = 0, misses = 0, saved_bandwidth_bytes = 0 WHERE id = 1;")
                conn.commit()
        except Exception as e:
            print(f"[Cache SQLite] Error clearing: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Returns real-time cache analytics."""
        total_lookups = self.hits + self.misses
        hit_ratio = round((self.hits / total_lookups * 100), 1) if total_lookups > 0 else 0.0
        saved_kb = round(self.saved_bandwidth_bytes / 1024, 2)
        
        # Count total entries in SQLite
        db_entries_count = 0
        try:
            with self._get_db_conn() as conn:
                res = conn.execute("SELECT COUNT(*) FROM crawler_cache_entries;").fetchone()
                if res:
                    db_entries_count = res[0]
        except Exception:
            db_entries_count = len(self.memory_cache)

        return {
            "total_cached_entries": db_entries_count,
            "memory_resident_entries": len(self.memory_cache),
            "storage_engine": "Persistent SQLite on Disk (Survives Reboots)",
            "storage_location": CACHE_DB_FILE,
            "hits": self.hits,
            "misses": self.misses,
            "total_lookups": total_lookups,
            "hit_ratio_percent": hit_ratio,
            "saved_bandwidth_kb": saved_kb,
            "max_memory_capacity": self.max_memory_entries,
            "default_ttl_seconds": self.default_ttl
        }

    def list_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns list of cached entries metadata for dashboard from SQLite."""
        results = []
        try:
            with self._get_db_conn() as conn:
                rows = conn.execute("""
                    SELECT key_hash, url, cached_at, ttl, size_bytes, access_count, metadata_json
                    FROM crawler_cache_entries
                    ORDER BY last_accessed DESC
                    LIMIT ?;
                """, (limit,)).fetchall()

                now = time.time()
                for r in rows:
                    meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
                    results.append({
                        "key": r["url"],
                        "cached_at": r["cached_at"],
                        "size_kb": round(r["size_bytes"] / 1024, 2),
                        "access_count": r["access_count"],
                        "ttl_remaining_sec": max(0, int(r["cached_at"] + r["ttl"] - now)),
                        "metadata": meta
                    })
        except Exception as e:
            print(f"[Cache SQLite] Error listing entries: {e}")
            for entry in list(self.memory_cache.values())[-limit:]:
                results.append({
                    "key": entry["key"],
                    "cached_at": entry["cached_at"],
                    "size_kb": round(entry["size_bytes"] / 1024, 2),
                    "access_count": entry.get("access_count", 1),
                    "ttl_remaining_sec": max(0, int(entry["cached_at"] + entry["ttl"] - time.time())),
                    "metadata": entry.get("metadata", {})
                })
        return results


# Global persistent cache instance
crawler_cache = CrawlerCache()
