# ============================================================
# WHISPLAY ASSISTANT PROFILE REGISTRY
# STAGE 430 — MULTI-ACTOR PROFILE CANDIDATE
# ============================================================

from copy import deepcopy
from time import time


ENGINE_NAME = "assistant_profile_registry"
ENGINE_STAGE = 430
ENGINE_VERSION = "430.0-candidate"


PROFILES = {
    "assistant_1": {
        "name": "Whisplay",
        "role": "system_operator",
        "style_mode": "focused",
        "permission_level": 1,
        "hardware_access": False,
        "memory_namespace": "assistant_1",
        "allowed_actions": [
            "system_status",
            "audio_status",
            "display_status",
        ],
    },
    "chatbot_2": {
        "name": "Mate",
        "role": "companion",
        "style_mode": "casual",
        "permission_level": 0,
        "hardware_access": False,
        "memory_namespace": "chatbot_2",
        "allowed_actions": [],
    },
    "chatbot_3": {
        "name": "Tech",
        "role": "technical_specialist",
        "style_mode": "sharp",
        "permission_level": 1,
        "hardware_access": False,
        "memory_namespace": "chatbot_3",
        "allowed_actions": [
            "system_status",
            "audio_status",
            "display_status",
        ],
    },
}


STATE = {
    "active_profile": "assistant_1",
    "switches": 0,
    "last_profile": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def list_profiles():
    return deepcopy(PROFILES)


def get_profile(profile_id=None):
    selected = profile_id or STATE["active_profile"]
    profile = PROFILES.get(selected)

    if profile is None:
        return None

    result = deepcopy(profile)
    result["id"] = selected
    return result


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "profiles": list(PROFILES.keys()),
        "active_profile": get_profile(),
        "state": snapshot(),
    }


def set_active_profile(profile_id):
    if profile_id not in PROFILES:
        return {
            "ok": False,
            "error": "unknown_profile",
            "requested_profile": profile_id,
        }

    previous = STATE["active_profile"]

    STATE["last_profile"] = previous
    STATE["active_profile"] = profile_id
    STATE["switches"] += 1
    STATE["updated"] = now()

    return {
        "ok": True,
        "previous_profile": previous,
        "active_profile": get_profile(),
        "state": snapshot(),
    }
