# ============================================================
# WHISPLAY BRAIN PACKAGE INIT — QUIET COMPATIBILITY CORE
# ============================================================
#
# Purpose:
# - Stop noisy optional import errors.
# - Keep old calls working:
#       from brain import think
#       from brain import process_input
#       from brain import generate_response
# - Prefer the strongest current cognition file:
#       brain_cognitive_STAGE150_MERGED.py
#
# This file should stay quiet unless something genuinely breaks.

from importlib import import_module


_MODULES = {}


def _try_import(name):
    try:
        mod = import_module(f"brain.{name}")
        _MODULES[name] = mod
        return mod
    except Exception:
        _MODULES[name] = None
        return None


# Strongest known brain/cognition modules
cognitive = _try_import("brain_cognitive_STAGE150_MERGED")
core = _try_import("brain_core_STAGE120_MERGED")
router = _try_import("brain_router")
fallback = _try_import("personality_fallback_STAGE120")


def think(text):
    """
    Main thinking entrypoint.
    """
    if cognitive and hasattr(cognitive, "think"):
        return cognitive.think(text)

    if core and hasattr(core, "think"):
        return core.think(text)

    if router and hasattr(router, "think"):
        return router.think(text)

    return {
        "action": "conversation",
        "intent": "fallback",
        "response": str(text),
        "text": text,
    }


def process_input(text):
    """
    Compatibility entrypoint for older assistant/controller code.
    """
    if cognitive and hasattr(cognitive, "process_input"):
        return cognitive.process_input(text)

    if cognitive and hasattr(cognitive, "process"):
        return cognitive.process(text)

    if core and hasattr(core, "process"):
        return core.process(text)

    result = think(text)

    if isinstance(result, dict):
        return result

    return {
        "action": "conversation",
        "intent": "fallback",
        "response": str(result),
        "text": text,
    }


def generate_response(text):
    """
    Compatibility response generator.
    """
    if cognitive and hasattr(cognitive, "generate_response"):
        return cognitive.generate_response(text)

    if core and hasattr(core, "generate_response"):
        return core.generate_response(text)

    result = process_input(text)

    if isinstance(result, dict):
        return result.get("response", str(result))

    return str(result)


def process(text):
    """
    Generic process alias.
    """
    return process_input(text)


def status():
    """
    Quiet module status for diagnostics.
    """
    return {
        "brain_cognitive_STAGE150_MERGED": cognitive is not None,
        "brain_core_STAGE120_MERGED": core is not None,
        "brain_router": router is not None,
        "personality_fallback_STAGE120": fallback is not None,
    }


__all__ = [
    "think",
    "process",
    "process_input",
    "generate_response",
    "status",
]
