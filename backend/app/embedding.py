import hashlib
import re
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger("embedding")

def generate_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Return a fast, deterministic, normalized feature-hash vector.
    """
    return _compute_stable_feature_vector(text, dim)

def generate_embeddings_batch(texts: List[str], dim: int = 384) -> List[List[float]]:
    return [_compute_stable_feature_vector(text, dim) for text in texts]

def cosine_similarity(v1: Union[List[float], np.ndarray], v2: Union[List[float], np.ndarray]) -> float:
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def _compute_stable_feature_vector(text: str, dim: int = 384) -> List[float]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    vec = np.zeros(dim, dtype=np.float32)

    def add_feature(feature: str, weight: float) -> None:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest, "little") % dim
        vec[index] += weight

    for index, word in enumerate(words):
        add_feature(f"word:{word}", 1.0)
        if index + 1 < len(words):
            add_feature(f"pair:{word}:{words[index + 1]}", 0.5)

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()
