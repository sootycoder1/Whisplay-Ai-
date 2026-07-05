# ============================================================
# WHISPLAY ASSISTANT SESSION
# STAGE 460 — ACTOR SESSION CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_profile_registry_STAGE430_LOCKED as registry
import assistant_selector_STAGE440_LOCKED as selector
import assistant_context_STAGE450_LOCKED as context


ENGINE_NAME = "assistant_session"
ENGINE_STAGE = 460
ENGINE_VERSION = "460.0-candidate"


STATE = {
    "switch_requests": 0,
    "turns_recorded": 0,
    "failures": 0,
    "last_profile": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def active_session():
    profile = registry.get_profile()

    if profile is None:
        STATE["failures"] += 1
        STATE["last_result"] = "missing_active_profile"
        STATE["updated"] = now()

        return {
            "ok": False,
            "error": "missing_active_profile",
            "state": snapshot(),
        }

    context_result = context.get_context(profile["id"])

    if not context_result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = context_result.get(
            "error",
            "context_read_failed",
        )
        STATE["updated"] = now()

        return {
            "ok": False,
            "error": STATE["last_result"],
            "profile": profile,
            "state": snapshot(),
        }

    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "session_read"
    STATE["updated"] = now()

    return {
        "ok": True,
        "profile": profile,
        "context": context_result["context"],
        "state": snapshot(),
    }


def switch_actor(text):
    STATE["switch_requests"] += 1
    STATE["updated"] = now()

    result = selector.select_profile(text)

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = result.get(
            "error",
            "switch_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "input": str(text or ""),
            "active_profile": result.get("active_profile"),
            "state": snapshot(),
        }

    profile = result["active_profile"]
    context_result = context.get_context(profile["id"])

    if not context_result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = context_result.get(
            "error",
            "context_read_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "active_profile": profile,
            "state": snapshot(),
        }

    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "actor_switched"

    return {
        "ok": True,
        "input": str(text or ""),
        "previous_profile": result["previous_profile"],
        "active_profile": profile,
        "context": context_result["context"],
        "response": result["response"],
        "state": snapshot(),
    }


def record_active_turn(user_input, response):
    profile = registry.get_profile()

    if profile is None:
        STATE["failures"] += 1
        STATE["last_result"] = "missing_active_profile"
        STATE["updated"] = now()

        return {
            "ok": False,
            "error": "missing_active_profile",
            "state": snapshot(),
        }

    result = context.record_turn(
        user_input,
        response,
        profile_id=profile["id"],
    )

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = result.get(
            "error",
            "turn_record_failed",
        )
        STATE["updated"] = now()

        return {
            "ok": False,
            "error": STATE["last_result"],
            "profile": profile,
            "state": snapshot(),
        }

    STATE["turns_recorded"] += 1
    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "turn_recorded"
    STATE["updated"] = now()

    return {
        "ok": True,
        "profile": profile,
        "turn": result["turn"],
        "context": result["context"],
        "state": snapshot(),
    }


def clear_active_context():
    profile = registry.get_profile()

    if profile is None:
        STATE["failures"] += 1
        STATE["last_result"] = "missing_active_profile"
        STATE["updated"] = now()

        return {
            "ok": False,
            "error": "missing_active_profile",
            "state": snapshot(),
        }

    result = context.clear_context(profile["id"])

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = result.get(
            "error",
            "context_clear_failed",
        )
        STATE["updated"] = now()

        return {
            "ok": False,
            "error": STATE["last_result"],
            "profile": profile,
            "state": snapshot(),
        }

    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "active_context_cleared"
    STATE["updated"] = now()

    return {
        "ok": True,
        "profile": profile,
        "context": result["context"],
        "state": snapshot(),
    }


def status():
    session = active_session()

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "session": session,
        "state": snapshot(),
    }
