# ============================================================
# WHISPLAY ASSISTANT RESPONSE
# STAGE 470 — ACTOR-AWARE RESPONSE CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_session_STAGE460_LOCKED as session
import personality_response_STAGE320_LOCKED as personality


ENGINE_NAME = "assistant_response"
ENGINE_STAGE = 470
ENGINE_VERSION = "470.0-candidate"


STATE = {
    "requests": 0,
    "successful_responses": 0,
    "failures": 0,
    "last_profile": "",
    "last_mode": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def build_response(payload):
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
    actor_context = active["context"]

    source = deepcopy(payload) if isinstance(payload, dict) else {}

    source_response = (
        source.get("response")
        or source.get("text")
        or ""
    )

    style_mode = profile.get("style_mode", "casual")

    styled = personality.apply_style(
        {
            **source,
            "response": source_response,
        },
        requested_mode=style_mode,
    )

    response_text = styled.get("response", "")

    recorded = session.record_active_turn(
        source.get("input", ""),
        response_text,
    )

    if not recorded.get("ok"):
        STATE["failures"] += 1
        STATE["last_profile"] = profile["id"]
        STATE["last_mode"] = style_mode
        STATE["last_result"] = recorded.get(
            "error",
            "turn_record_failed",
        )

        return {
            "ok": False,
            "error": STATE["last_result"],
            "profile": profile,
            "state": snapshot(),
        }

    STATE["successful_responses"] += 1
    STATE["last_profile"] = profile["id"]
    STATE["last_mode"] = style_mode
    STATE["last_result"] = "response_built"

    return {
        "ok": True,
        "profile": profile,
        "actor": {
            "id": profile["id"],
            "name": profile["name"],
            "role": profile["role"],
            "style_mode": style_mode,
            "permission_level": profile["permission_level"],
            "hardware_access": profile["hardware_access"],
            "memory_namespace": profile["memory_namespace"],
        },
        "input": str(source.get("input") or ""),
        "response": response_text,
        "mood": styled.get("mood"),
        "energy": styled.get("energy"),
        "mode": styled.get("mode"),
        "personality": styled.get("personality"),
        "previous_context": actor_context,
        "context": recorded["context"],
        "turn": recorded["turn"],
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
