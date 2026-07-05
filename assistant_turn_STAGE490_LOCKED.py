# ============================================================
# WHISPLAY ASSISTANT TURN COORDINATOR
# STAGE 490 — ACTOR TURN ROUTING CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_session_STAGE460_LOCKED as session
import assistant_response_STAGE470_LOCKED as response_layer
import assistant_action_gate_STAGE480_LOCKED as action_gate


ENGINE_NAME = "assistant_turn"
ENGINE_STAGE = 490
ENGINE_VERSION = "490.0-candidate"


STATE = {
    "requests": 0,
    "response_turns": 0,
    "action_turns": 0,
    "denied_actions": 0,
    "failures": 0,
    "last_profile": "",
    "last_route": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def normalize_route(route):
    cleaned = str(route or "").strip().lower()

    if cleaned in {"action", "command", "safe_action"}:
        return "action"

    return "response"


def process_turn(payload):
    STATE["requests"] += 1
    STATE["updated"] = now()

    source = deepcopy(payload) if isinstance(payload, dict) else {}
    route = normalize_route(source.get("route"))

    active = session.active_session()

    if not active.get("ok"):
        STATE["failures"] += 1
        STATE["last_route"] = route
        STATE["last_result"] = active.get(
            "error",
            "session_read_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "route": route,
            "state": snapshot(),
        }

    profile = active["profile"]

    STATE["last_profile"] = profile["id"]
    STATE["last_route"] = route

    if route == "action":
        action_name = source.get("action")

        result = action_gate.execute_action(action_name)

        if not result.get("ok"):
            if result.get("allowed") is False:
                STATE["denied_actions"] += 1
            else:
                STATE["failures"] += 1

            STATE["last_result"] = result.get(
                "error",
                "action_failed",
            )

            return {
                "ok": False,
                "route": "action",
                "error": STATE["last_result"],
                "profile": profile,
                "action": result,
                "state": snapshot(),
            }

        STATE["action_turns"] += 1
        STATE["last_result"] = "action_completed"

        return {
            "ok": True,
            "route": "action",
            "profile": profile,
            "action": result,
            "response": result["result"]["message"],
            "state": snapshot(),
        }

    result = response_layer.build_response(source)

    if not result.get("ok"):
        STATE["failures"] += 1
        STATE["last_result"] = result.get(
            "error",
            "response_failed",
        )

        return {
            "ok": False,
            "route": "response",
            "error": STATE["last_result"],
            "profile": profile,
            "response_result": result,
            "state": snapshot(),
        }

    STATE["response_turns"] += 1
    STATE["last_result"] = "response_completed"

    return {
        "ok": True,
        "route": "response",
        "profile": result["profile"],
        "actor": result["actor"],
        "response": result["response"],
        "mood": result["mood"],
        "energy": result["energy"],
        "mode": result["mode"],
        "context": result["context"],
        "turn": result["turn"],
        "state": snapshot(),
    }


def status():
    active = session.active_session()

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "active_session": active,
        "state": snapshot(),
    }
