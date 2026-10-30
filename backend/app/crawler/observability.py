"""
Langfuse Observability & Telemetry Integration for JanSahayak AI.
Instruments the 5-stage agentic pipeline:
  Stage 0: Domain & Security Guardrails
  Tool 1: RouterTool (intent, scope, criteria)
  Tool 2: CrawlerTool (autonomous search & decision gate)
  Tool 3: QuestionnaireTool (dynamic gap analysis)
  Tool 4: ResponseGeneratorTool (synthesis)
"""

import os
import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger("gov_scheme.observability")

# Check if Langfuse credentials are configured
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

_langfuse_client = None
_is_available = False

try:
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        from langfuse import Langfuse, observe as _langfuse_observe
        _langfuse_client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
        )
        _is_available = _langfuse_client.auth_check()
        if _is_available:
            logger.info("Langfuse Observability connected to host: %s", LANGFUSE_HOST)
        else:
            logger.warning("Langfuse credentials failed auth_check; telemetry disabled.")
    else:
        logger.info("Langfuse credentials not set; running in local logging mode.")
except Exception as e:
    logger.warning("Could not initialize Langfuse: %s; running in safe bypass mode.", e)
    _is_available = False


def is_telemetry_enabled() -> bool:
    """Returns True if Langfuse is active and authenticated."""
    return _is_available and _langfuse_client is not None


def observe(name: Optional[str] = None, as_type: Optional[str] = None):
    """
    Decorator for tracing pipeline functions and agent tool calls.
    Fails safely without raising exceptions if telemetry is down.
    """
    def decorator(fn: Callable):
        if not is_telemetry_enabled():
            return fn

        try:
            from langfuse import observe as lf_observe
            return lf_observe(name=name, as_type=as_type)(fn)
        except Exception as e:
            logger.warning("Failed to wrap %s with Langfuse observe: %s", fn.__name__, e)
            return fn

    return decorator


def flush_telemetry():
    """Flushes any batched telemetry spans asynchronously."""
    if is_telemetry_enabled():
        try:
            _langfuse_client.flush()
        except Exception as e:
            logger.debug("Telemetry flush exception: %s", e)
