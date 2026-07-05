# ============================================================
# WHISPLAY SAFE LOCAL ACTIONS
# STAGE 380 — APPROVED LOCAL ACTION SET CANDIDATE
# ============================================================

from copy import deepcopy
from time import time


ENGINE_NAME = "safe_local_actions"
ENGINE_STAGE = 380
ENGINE_VERSION = "380.0-candidate"


STATE = {
    "calls": 0,
    "last_action": None,
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def system_status():
    STATE["calls"] += 1
    STATE["last_action"] = "system_status"
    STATE["updated"] = now()

    return {
        "ok": True,
        "action": "system_status",
        "message": "Whisplay runtime status requested.",
        "state_stage380": snapshot(),
    }


def audio_status():
    STATE["calls"] += 1
    STATE["last_action"] = "audio_status"
    STATE["updated"] = now()

    return {
        "ok": True,
        "action": "audio_status",
        "message": "Whisplay audio path status requested.",
        "state_stage380": snapshot(),
    }


def display_status():
    STATE["calls"] += 1
    STATE["last_action"] = "display_status"
    STATE["updated"] = now()

    return {
        "ok": True,
        "action": "display_status",
        "message": "Whisplay display path status requested.",
        "state_stage380": snapshot(),
    }


def list_safe_actions():
    return [
        "system_status",
        "audio_status",
        "display_status",
    ]


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "actions": list_safe_actions(),
        "state": snapshot(),
    }


if __name__ == "__main__":
    print(system_status())
    print(audio_status())
    print(display_status())
