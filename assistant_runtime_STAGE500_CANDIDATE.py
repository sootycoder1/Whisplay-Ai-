# ============================================================
# WHISPLAY ASSISTANT RUNTIME
# STAGE 500 — MULTI-ACTOR RUNTIME FACADE CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_session_STAGE460_LOCKED as session
import assistant_turn_STAGE490_LOCKED as turn


ENGINE_NAME = "assistant_runtime"
ENGINE_STAGE = 500
ENGINE_VERSION = "500.0-candidate"


STATE = {
    "requests": 0,
    "switches": 0,
    "turns": 0,
    "failures": 0,
    "last_operation": "",
    "last_profile": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def active():
    STATE["requests"] += 1
    STATE["last_operation"] = "active"
    STATE["updated"] = now()

    result = session.active_session()

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = result.get(
            "error",
            "session_read_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "state": snapshot(),
        }

    profile = result["profile"]

    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "active_session_read"

    return {
        "ok": True,
        "profile": profile,
        "context": result["context"],
        "state": snapshot(),
    }


def switch_actor(text):
    STATE["requests"] += 1
    STATE["last_operation"] = "switch_actor"
    STATE["updated"] = now()

    result = session.switch_actor(text)

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

    STATE["switches"] += 1
    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "actor_switched"

    return {
        "ok": True,
        "input": str(text or ""),
        "previous_profile": result["previous_profile"],
        "active_profile": profile,
        "context": result["context"],
        "response": result["response"],
        "state": snapshot(),
    }


def process(payload):
    STATE["requests"] += 1
    STATE["last_operation"] = "process_turn"
    STATE["updated"] = now()

    source = deepcopy(payload) if isinstance(payload, dict) else {}

    result = turn.process_turn(source)

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_profile"] = (
            result.get("profile") or {}
        ).get("id", "")
        STATE["last_result"] = result.get(
            "error",
            "turn_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "route": result.get("route"),
            "profile": result.get("profile"),
            "result": result,
            "state": snapshot(),
        }

    profile = result["profile"]

    STATE["turns"] += 1
    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "turn_completed"

    output = deepcopy(result)
    output["runtime_state"] = snapshot()

    return output


def clear_active_context():
    STATE["requests"] += 1
    STATE["last_operation"] = "clear_active_context"
    STATE["updated"] = now()

    result = session.clear_active_context()

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = result.get(
            "error",
            "context_clear_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "state": snapshot(),
        }

    profile = result["profile"]

    STATE["last_profile"] = profile["id"]
    STATE["last_result"] = "active_context_cleared"

    return {
        "ok": True,
        "profile": profile,
        "context": result["context"],
        "state": snapshot(),
    }


def status():
    active_result = session.active_session()
    turn_status = turn.status()

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "active_session": active_result,
        "turn_coordinator": turn_status,
        "state": snapshot(),
    }
