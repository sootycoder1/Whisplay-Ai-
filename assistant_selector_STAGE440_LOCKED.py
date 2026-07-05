# ============================================================
# WHISPLAY ASSISTANT SELECTOR
# STAGE 440 — MULTI-ACTOR SELECTOR CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_profile_registry_STAGE430_LOCKED as registry


ENGINE_NAME = "assistant_selector"
ENGINE_STAGE = 440
ENGINE_VERSION = "440.0-candidate"

ALIASES = {
    "assistant_1": {
        "assistant_1",
        "assistant 1",
        "whisplay",
        "system",
        "system operator",
        "main assistant",
    },
    "chatbot_2": {
        "chatbot_2",
        "chatbot 2",
        "mate",
        "companion",
        "casual",
    },
    "chatbot_3": {
        "chatbot_3",
        "chatbot 3",
        "tech",
        "technical",
        "technical specialist",
    },
}


STATE = {
    "requests": 0,
    "successful_switches": 0,
    "failed_switches": 0,
    "last_input": "",
    "last_requested_profile": "",
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def normalize_text(text):
    if text is None:
        return ""

    return " ".join(
        str(text)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
        .split()
    )


def resolve_profile(text):
    cleaned = normalize_text(text)

    if not cleaned:
        return None

    for profile_id, aliases in ALIASES.items():
        normalized_aliases = {
            normalize_text(alias)
            for alias in aliases
        }

        if cleaned in normalized_aliases:
            return profile_id

    switch_prefixes = (
        "switch to ",
        "change to ",
        "use ",
        "activate ",
        "select ",
        "talk to ",
    )

    for prefix in switch_prefixes:
        if cleaned.startswith(prefix):
            target = cleaned[len(prefix):].strip()

            for profile_id, aliases in ALIASES.items():
                normalized_aliases = {
                    normalize_text(alias)
                    for alias in aliases
                }

                if target in normalized_aliases:
                    return profile_id

    return None




def select_profile(text):
    STATE["requests"] += 1
    STATE["last_input"] = str(text or "")
    STATE["updated"] = now()

    profile_id = resolve_profile(text)
    STATE["last_requested_profile"] = profile_id or ""

    if profile_id is None:
        STATE["failed_switches"] += 1
        STATE["last_result"] = "unknown_profile"

        return {
            "ok": False,
            "error": "unknown_profile",
            "input": str(text or ""),
            "active_profile": registry.get_profile(),
            "selector_state": snapshot(),
        }

    result = registry.set_active_profile(profile_id)

    if not result.get("ok"):
        STATE["failed_switches"] += 1
        STATE["last_result"] = result.get("error", "switch_failed")

        return {
            "ok": False,
            "error": STATE["last_result"],
            "input": str(text or ""),
            "requested_profile": profile_id,
            "active_profile": registry.get_profile(),
            "selector_state": snapshot(),
        }

    STATE["successful_switches"] += 1
    STATE["last_result"] = "switched"

    active_profile = result["active_profile"]

    return {
        "ok": True,
        "input": str(text or ""),
        "requested_profile": profile_id,
        "previous_profile": result["previous_profile"],
        "active_profile": active_profile,
        "response": f"Switched to {active_profile['name']}.",
        "selector_state": snapshot(),
    }
