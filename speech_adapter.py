# ============================================================
# SPEECH ADAPTER — STAGE 3600
# Runtime speech bridge + voice execution layer
# ============================================================

import time
import traceback


STAGE = 3600

ENGINE_NAME = "SPEECH_ADAPTER"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# SPEECH STATE
# ============================================================

SPEECH_STATE = {
    "enabled": True,
    "safe_mode": False,
    "speaking": False,
    "muted": False,
    "last_text": "",
    "last_voice": "default",
    "last_error": "",
    "calls": 0,
    "failures": 0,
    "last_speak_time": 0.0,
}


# ============================================================
# VOICE CONFIG
# ============================================================

VOICE = {
    "name": "default",
    "rate": 22050,
    "volume": 1.0,
    "energy": 1.0,
}


# ============================================================
# HANDLERS
# ============================================================

HANDLERS = {
    "speak": None,
    "stop": None,
    "prepare": None,
    "cleanup": None,
}


# ============================================================
# HISTORY
# ============================================================

SPEECH_HISTORY = []

MAX_HISTORY = 240


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[SPEECH] {message}")


def remember(event, details=None):

    SPEECH_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(SPEECH_HISTORY) > MAX_HISTORY:
        SPEECH_HISTORY.pop(0)


def clean(text):

    return " ".join(
        str(text or "").strip().split()
    )


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_handler(name, handler):

    if name not in HANDLERS:
        return False

    HANDLERS[name] = handler

    remember("handler_registered", {
        "name": name,
    })

    log(f"handler registered: {name}")

    return True


# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable():

    SPEECH_STATE["enabled"] = True

    return True


def disable():

    SPEECH_STATE["enabled"] = False

    return True


# ============================================================
# MUTE CONTROL
# ============================================================

def mute():

    SPEECH_STATE["muted"] = True

    remember("muted")

    log("muted")

    return True


def unmute():

    SPEECH_STATE["muted"] = False

    remember("unmuted")

    log("unmuted")

    return True


# ============================================================
# SAFE MODE
# ============================================================

def enable_safe_mode():

    SPEECH_STATE["safe_mode"] = True

    remember("safe_mode_enabled")

    log("safe mode enabled")

    return True


def disable_safe_mode():

    SPEECH_STATE["safe_mode"] = False

    remember("safe_mode_disabled")

    return True


# ============================================================
# CALL HANDLER SAFE
# ============================================================

def call_handler(name, *args, **kwargs):

    handler = HANDLERS.get(name)

    if not callable(handler):

        return {
            "ok": False,
            "error": "missing_handler",
            "handler": name,
        }

    try:

        result = handler(
            *args,
            **kwargs,
        )

        return {
            "ok": True,
            "handler": name,
            "result": result,
        }

    except Exception as e:

        SPEECH_STATE["failures"] += 1
        SPEECH_STATE["last_error"] = str(e)

        remember("handler_failure", {
            "handler": name,
            "error": str(e),
        })

        if DEBUG:
            print(traceback.format_exc())

        return {
            "ok": False,
            "handler": name,
            "error": str(e),
        }


# ============================================================
# VOICE CONFIG
# ============================================================

def set_voice(
    name="default",
    rate=22050,
    volume=1.0,
    energy=1.0,
):

    VOICE["name"] = str(name)

    VOICE["rate"] = int(rate)

    VOICE["volume"] = float(volume)

    VOICE["energy"] = float(energy)

    remember("voice_update", {
        "name": name,
    })

    return dict(VOICE)


# ============================================================
# PREPARE
# ============================================================

def prepare(text, strategy=None):

    strategy = strategy or {}

    cleaned = clean(text)

    if strategy.get("verbosity", 0.5) <= 0.35:
        cleaned = cleaned.strip()

    if strategy.get("tone") == "calm":
        VOICE["energy"] = 0.82

    elif strategy.get("tone") == "focused":
        VOICE["energy"] = 1.08

    else:
        VOICE["energy"] = 1.0

    if callable(HANDLERS["prepare"]):

        call_handler(
            "prepare",
            cleaned,
            strategy,
        )

    return cleaned


# ============================================================
# SPEAK
# ============================================================

def speak(
    text,
    strategy=None,
):

    strategy = strategy or {}

    text = clean(text)

    if not SPEECH_STATE["enabled"]:

        return {
            "ok": False,
            "error": "speech_disabled",
        }

    if SPEECH_STATE["muted"]:

        return {
            "ok": False,
            "error": "speech_muted",
        }

    if SPEECH_STATE["safe_mode"]:

        return {
            "ok": False,
            "error": "safe_mode_enabled",
        }

    if not text:

        return {
            "ok": False,
            "error": "empty_text",
        }

    prepared = prepare(
        text,
        strategy,
    )

    SPEECH_STATE["calls"] += 1

    SPEECH_STATE["speaking"] = True

    SPEECH_STATE["last_text"] = prepared

    SPEECH_STATE["last_speak_time"] = now()

    remember("speak", {
        "text": prepared[:120],
    })

    result = None

    # --------------------------------------------------------
    # EXTERNAL SPEAK HANDLER
    # --------------------------------------------------------

    if callable(HANDLERS["speak"]):

        result = call_handler(
            "speak",
            prepared,
            dict(VOICE),
            strategy,
        )

    else:

        # safe fallback
        print(f"\n[SPEECH OUTPUT]\n{prepared}\n")

        result = {
            "ok": True,
            "fallback": True,
        }

    SPEECH_STATE["speaking"] = False

    if callable(HANDLERS["cleanup"]):

        call_handler("cleanup")

    return {
        "ok": True,
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "voice": dict(VOICE),
        "result": result,
    }


# ============================================================
# STOP
# ============================================================

def stop():

    SPEECH_STATE["speaking"] = False

    remember("stop")

    if callable(HANDLERS["stop"]):

        return call_handler(
            "stop"
        )

    return {
        "ok": True,
        "stopped": True,
    }


# ============================================================
# PROCESS
# ============================================================

def process(
    text,
    runtime_state=None,
    strategy=None,
):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    recovery = runtime_state.get(
        "recovery",
        False,
    )

    if recovery:
        enable_safe_mode()

    if pressure >= 0.95:
        mute()

    return speak(
        text,
        strategy,
    )


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "state": dict(SPEECH_STATE),
        "voice": dict(VOICE),
        "handlers": {
            name: callable(handler)
            for name, handler in HANDLERS.items()
        },
        "history_size": len(
            SPEECH_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def speech(
    text,
    strategy=None,
):

    return speak(
        text,
        strategy,
    )


def output(
    text,
    strategy=None,
):

    return speak(
        text,
        strategy,
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" SPEECH ADAPTER STAGE3600")
    print("================================\n")

    speak(
        "Runtime systems online.",
        strategy={
            "tone": "focused",
            "verbosity": 0.42,
        },
    )

    print(status())
