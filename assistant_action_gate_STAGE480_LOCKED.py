# ============================================================
# WHISPLAY ASSISTANT ACTION GATE
# STAGE 480 — ACTOR-AWARE ACTION PERMISSION CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_session_STAGE460_LOCKED as session
import safe_actions_STAGE380_CANDIDATE as safe_actions


ENGINE_NAME = "assistant_action_gate"
ENGINE_STAGE = 480
ENGINE_VERSION = "480.0-candidate"


ACTION_HANDLERS = {
    "system_status": safe_actions.system_status,
    "audio_status": safe_actions.audio_status,
    "display_status": safe_actions.display_status,
}


STATE = {
    "requests": 0,
    "allowed": 0,
    "denied": 0,
    "failures": 0,
    "last_profile": "",
    "last_action": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def normalize_action(action):
    return "_".join(
        str(action or "")
        .strip()
        .lower()
        .replace("-", " ")
        .split()
    )


def check_permission(action):
    STATE["requests"] += 1
    STATE["updated"] = now()

    active = session.active_session()

    if not active.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = active.get(
            "error",
            "session_read_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "state": snapshot(),
        }

    profile = active["profile"]
    action_name = normalize_action(action)

    STATE["last_profile"] = profile["id"]
    STATE["last_action"] = action_name

    if action_name not in ACTION_HANDLERS:
        STATE["denied"] += 1
        STATE["last_result"] = "unknown_action"

        return {
            "ok": False,
            "allowed": False,
            "error": "unknown_action",
            "action": action_name,
            "profile": profile,
            "state": snapshot(),
        }

    if profile.get("hardware_access") is True:
        STATE["denied"] += 1
        STATE["last_result"] = "hardware_access_blocked"

        return {
            "ok": False,
            "allowed": False,
            "error": "hardware_access_blocked",
            "action": action_name,
            "profile": profile,
            "state": snapshot(),
        }

    allowed_actions = profile.get("allowed_actions", [])

    if action_name not in allowed_actions:
        STATE["denied"] += 1
        STATE["last_result"] = "action_not_allowed"

        return {
            "ok": False,
            "allowed": False,
            "error": "action_not_allowed",
            "action": action_name,
            "profile": profile,
            "allowed_actions": deepcopy(allowed_actions),
            "state": snapshot(),
        }

    STATE["allowed"] += 1
    STATE["last_result"] = "action_allowed"

    return {
        "ok": True,
        "allowed": True,
        "action": action_name,
        "profile": profile,
        "handler": ACTION_HANDLERS[action_name],
        "state": snapshot(),
    }


def execute_action(action):
    permission = check_permission(action)

    if not permission.get("ok"):
        return permission

    handler = permission["handler"]
    result = handler()

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = "action_failed"
        STATE["updated"] = now()

        return {
            "ok": False,
            "allowed": True,
            "error": "action_failed",
            "action": permission["action"],
            "profile": permission["profile"],
            "result": result,
            "state": snapshot(),
        }

    STATE["last_result"] = "action_executed"
    STATE["updated"] = now()

    return {
        "ok": True,
        "allowed": True,
        "action": permission["action"],
        "profile": permission["profile"],
        "result": result,
        "state": snapshot(),
    }


def status():
    active = session.active_session()

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "safe_actions": list(ACTION_HANDLERS.keys()),
        "active_session": active,
        "state": snapshot(),
    }
