# ============================================================
# FALLBACK CORE — STAGE 3600
# Runtime fallback + graceful degradation layer
# ============================================================

import time
import random


STAGE = 3600

ENGINE_NAME = "FALLBACK_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# FALLBACK STATE
# ============================================================

FALLBACK = {
    "enabled": True,
    "safe_mode": False,
    "degraded_mode": False,
    "fallback_level": 0,
    "calls": 0,
    "failures": 0,
    "recoveries": 0,
    "last_input": "",
    "last_output": "",
    "last_reason": "",
    "last_trigger": 0.0,
}


# ============================================================
# FALLBACK LEVELS
# ============================================================

LEVELS = {

    0: {
        "name": "normal",
        "verbosity": 0.75,
        "personality": True,
    },

    1: {
        "name": "light_degraded",
        "verbosity": 0.60,
        "personality": True,
    },

    2: {
        "name": "degraded",
        "verbosity": 0.45,
        "personality": False,
    },

    3: {
        "name": "minimal",
        "verbosity": 0.25,
        "personality": False,
    },

    4: {
        "name": "critical",
        "verbosity": 0.12,
        "personality": False,
    },
}


# ============================================================
# RESPONSE BANKS
# ============================================================

RESPONSES = {

    "general": [
        "Runtime acknowledged.",
        "I am here.",
        "Understood.",
        "Processing that now.",
        "Continuing.",
    ],

    "debug": [
        "Debug condition detected.",
        "Runtime issue acknowledged.",
        "Analyzing failure path.",
        "Recovery path available.",
    ],

    "recovery": [
        "Recovery mode active.",
        "Stabilizing runtime.",
        "Runtime protection engaged.",
        "Reducing system pressure.",
    ],

    "system": [
        "System state acknowledged.",
        "Runtime systems responding.",
        "Core systems online.",
        "Runtime integrity stable.",
    ],

    "empty": [
        "I did not catch that.",
        "Input unclear.",
        "Please repeat that.",
    ],
}


# ============================================================
# HISTORY
# ============================================================

FALLBACK_HISTORY = []

MAX_HISTORY = 300


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[FALLBACK] {message}")


def remember(event, details=None):

    FALLBACK_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(FALLBACK_HISTORY) > MAX_HISTORY:
        FALLBACK_HISTORY.pop(0)


def clean(text):

    return " ".join(
        str(text or "").strip().split()
    )


def clamp(value, low, high):

    return max(
        low,
        min(high, value),
    )


# ============================================================
# LEVEL CONTROL
# ============================================================

def set_level(level):

    level = int(
        clamp(level, 0, 4)
    )

    FALLBACK["fallback_level"] = level

    remember("level_change", {
        "level": level,
    })

    log(
        f"level: {LEVELS[level]['name']}"
    )

    return level


def escalate():

    current = FALLBACK[
        "fallback_level"
    ]

    if current < 4:
        current += 1

    FALLBACK["fallback_level"] = current

    remember("escalate", {
        "level": current,
    })

    return current


def recover():

    current = FALLBACK[
        "fallback_level"
    ]

    if current > 0:
        current -= 1

    FALLBACK["fallback_level"] = current

    FALLBACK["recoveries"] += 1

    remember("recover", {
        "level": current,
    })

    return current


# ============================================================
# SAFE / DEGRADED MODES
# ============================================================

def enable_safe_mode():

    FALLBACK["safe_mode"] = True

    remember("safe_mode_enabled")

    log("safe mode enabled")

    return True


def disable_safe_mode():

    FALLBACK["safe_mode"] = False

    remember("safe_mode_disabled")

    return True


def enable_degraded_mode():

    FALLBACK["degraded_mode"] = True

    remember("degraded_mode_enabled")

    log("degraded mode enabled")

    return True


def disable_degraded_mode():

    FALLBACK["degraded_mode"] = False

    remember("degraded_mode_disabled")

    return True


# ============================================================
# INTENT GUESS
# ============================================================

def intent(text):

    t = clean(text).lower()

    if not t:
        return "empty"

    if any(w in t for w in [
        "debug",
        "error",
        "traceback",
        "failed",
    ]):
        return "debug"

    if any(w in t for w in [
        "recover",
        "stability",
        "runtime",
        "pressure",
    ]):
        return "recovery"

    if any(w in t for w in [
        "system",
        "health",
        "status",
    ]):
        return "system"

    return "general"


# ============================================================
# BUILD RESPONSE
# ============================================================

def response(
    text,
    runtime_state=None,
):

    runtime_state = runtime_state or {}

    FALLBACK["calls"] += 1

    FALLBACK["last_input"] = text

    current_intent = intent(text)

    level = FALLBACK[
        "fallback_level"
    ]

    config = LEVELS[level]

    choices = RESPONSES.get(
        current_intent,
        RESPONSES["general"],
    )

    result = random.choice(
        choices
    )

    # --------------------------------------------------------
    # MINIMALIZATION
    # --------------------------------------------------------

    if level >= 3:

        result = result.split(".")[0]

    # --------------------------------------------------------
    # SAFE MODE
    # --------------------------------------------------------

    if FALLBACK["safe_mode"]:

        result = "Safe mode active."

    # --------------------------------------------------------
    # DEGRADED MODE
    # --------------------------------------------------------

    if FALLBACK["degraded_mode"]:

        result = (
            result[:80]
        ).strip()

    FALLBACK["last_output"] = result

    remember("response", {
        "intent": current_intent,
        "level": level,
    })

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "intent": current_intent,
        "level": level,
        "mode": config["name"],
        "response": result,
    }


# ============================================================
# PROCESS
# ============================================================

def process(
    text,
    runtime_state=None,
):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    stability = runtime_state.get(
        "stability",
        1.0,
    )

    recovery_state = runtime_state.get(
        "recovery",
        False,
    )

    # --------------------------------------------------------
    # ESCALATION
    # --------------------------------------------------------

    if pressure >= 0.90:
        escalate()

    if stability <= 0.25:
        escalate()

    if recovery_state:
        enable_degraded_mode()

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    if pressure <= 0.30 and stability >= 0.85:
        recover()

    return response(
        text,
        runtime_state,
    )


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "fallback": dict(
            FALLBACK
        ),
        "current_level": LEVELS[
            FALLBACK["fallback_level"]
        ],
        "history_size": len(
            FALLBACK_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def fallback(
    text,
    runtime_state=None,
):

    return process(
        text,
        runtime_state,
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" FALLBACK CORE STAGE3600")
    print("================================\n")

    runtime_state = {
        "pressure": 0.82,
        "stability": 0.48,
    }

    print(
        process(
            "runtime recovery unstable",
            runtime_state,
        )
    )

    print(status())
