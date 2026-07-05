# ============================================================
# WHISPLAY ASSISTANT CONTEXT
# STAGE 450 — PER-ACTOR CONTEXT CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_profile_registry_STAGE430_LOCKED as registry


ENGINE_NAME = "assistant_context"
ENGINE_STAGE = 450
ENGINE_VERSION = "450.0-candidate"

MAX_HISTORY = 12


CONTEXTS = {
    profile_id: {
        "turns": 0,
        "last_input": "",
        "last_response": "",
        "history": [],
        "updated": 0.0,
    }
    for profile_id in registry.list_profiles()
}


STATE = {
    "writes": 0,
    "reads": 0,
    "clears": 0,
    "failures": 0,
    "last_profile": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def valid_profile(profile_id):
    return profile_id in CONTEXTS


def get_context(profile_id=None):
    STATE["reads"] += 1
    STATE["updated"] = now()

    selected = profile_id or registry.get_profile()["id"]
    STATE["last_profile"] = selected

    if not valid_profile(selected):
        STATE["failures"] += 1
        STATE["last_result"] = "unknown_profile"

        return {
            "ok": False,
            "error": "unknown_profile",
            "profile_id": selected,
            "state": snapshot(),
        }

    STATE["last_result"] = "context_read"

    return {
        "ok": True,
        "profile_id": selected,
        "context": deepcopy(CONTEXTS[selected]),
        "state": snapshot(),
    }


def record_turn(user_input, response, profile_id=None):
    selected = profile_id or registry.get_profile()["id"]
    STATE["last_profile"] = selected
    STATE["updated"] = now()

    if not valid_profile(selected):
        STATE["failures"] += 1
        STATE["last_result"] = "unknown_profile"

        return {
            "ok": False,
            "error": "unknown_profile",
            "profile_id": selected,
            "state": snapshot(),
        }

    context = CONTEXTS[selected]
    timestamp = now()

    turn = {
        "turn": context["turns"] + 1,
        "input": str(user_input or ""),
        "response": str(response or ""),
        "timestamp": timestamp,
    }

    context["turns"] += 1
    context["last_input"] = turn["input"]
    context["last_response"] = turn["response"]
    context["history"].append(turn)
    context["history"] = context["history"][-MAX_HISTORY:]
    context["updated"] = timestamp

    STATE["writes"] += 1
    STATE["last_result"] = "turn_recorded"

    return {
        "ok": True,
        "profile_id": selected,
        "turn": deepcopy(turn),
        "context": deepcopy(context),
        "state": snapshot(),
    }


def clear_context(profile_id=None):
    selected = profile_id or registry.get_profile()["id"]
    STATE["last_profile"] = selected
    STATE["updated"] = now()

    if not valid_profile(selected):
        STATE["failures"] += 1
        STATE["last_result"] = "unknown_profile"

        return {
            "ok": False,
            "error": "unknown_profile",
            "profile_id": selected,
            "state": snapshot(),
        }

    CONTEXTS[selected] = {
        "turns": 0,
        "last_input": "",
        "last_response": "",
        "history": [],
        "updated": now(),
    }

    STATE["clears"] += 1
    STATE["last_result"] = "context_cleared"

    return {
        "ok": True,
        "profile_id": selected,
        "context": deepcopy(CONTEXTS[selected]),
        "state": snapshot(),
    }


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "max_history": MAX_HISTORY,
        "profiles": list(CONTEXTS.keys()),
        "contexts": deepcopy(CONTEXTS),
        "state": snapshot(),
    }
