# ============================================================
# MODES CORE — STAGE 3600
# Runtime operational modes + behavioral state layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "MODES_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# MODE DEFINITIONS
# ============================================================

MODES = {

    "idle": {
        "energy": 0.30,
        "verbosity": 0.20,
        "responsiveness": 0.15,
        "recovery_bias": 0.80,
    },

    "balanced": {
        "energy": 1.00,
        "verbosity": 0.60,
        "responsiveness": 0.70,
        "recovery_bias": 0.50,
    },

    "focused": {
        "energy": 1.15,
        "verbosity": 0.42,
        "responsiveness": 0.90,
        "recovery_bias": 0.45,
    },

    "casual": {
        "energy": 0.92,
        "verbosity": 0.78,
        "responsiveness": 0.72,
        "recovery_bias": 0.35,
    },

    "recovery": {
        "energy": 0.55,
        "verbosity": 0.35,
        "responsiveness": 0.40,
        "recovery_bias": 1.00,
    },

    "guarded": {
        "energy": 0.72,
        "verbosity": 0.28,
        "responsiveness": 0.50,
        "recovery_bias": 0.92,
    },

    "critical": {
        "energy": 0.40,
        "verbosity": 0.18,
        "responsiveness": 0.22,
        "recovery_bias": 1.20,
    },
}


# ============================================================
# ACTIVE MODE
# ============================================================

ACTIVE_MODE = "balanced"

LAST_MODE = "idle"

MODE_HISTORY = []

MAX_HISTORY = 120


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[MODES] {message}")


def remember(event, details=None):

    MODE_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(MODE_HISTORY) > MAX_HISTORY:
        MODE_HISTORY.pop(0)


# ============================================================
# MODE ACCESS
# ============================================================

def exists(mode):

    return mode in MODES


def get(mode=None):

    if mode is None:
        mode = ACTIVE_MODE

    return dict(
        MODES.get(
            mode,
            MODES["balanced"],
        )
    )


# ============================================================
# SET MODE
# ============================================================

def set_mode(mode):

    global ACTIVE_MODE
    global LAST_MODE

    if mode not in MODES:
        return False

    LAST_MODE = ACTIVE_MODE

    ACTIVE_MODE = mode

    remember("mode_change", {
        "from": LAST_MODE,
        "to": ACTIVE_MODE,
    })

    log(f"mode: {ACTIVE_MODE}")

    return ACTIVE_MODE


# ============================================================
# AUTO MODE
# ============================================================

def auto(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    stability = runtime_state.get(
        "stability",
        1.0,
    )

    recovery = runtime_state.get(
        "recovery",
        False,
    )

    blocked = runtime_state.get(
        "blocked",
        False,
    )

    intent = runtime_state.get(
        "intent",
        "",
    )

    # ------------------------------------------------
    # CRITICAL
    # ------------------------------------------------

    if blocked:
        return set_mode("critical")

    if stability <= 0.20:
        return set_mode("critical")

    if pressure >= 0.92:
        return set_mode("critical")

    # ------------------------------------------------
    # RECOVERY
    # ------------------------------------------------

    if recovery:
        return set_mode("recovery")

    if pressure >= 0.75:
        return set_mode("guarded")

    # ------------------------------------------------
    # FOCUSED
    # ------------------------------------------------

    if intent in [
        "debug",
        "system",
        "runtime",
        "memory",
        "build",
    ]:
        return set_mode("focused")

    # ------------------------------------------------
    # CASUAL
    # ------------------------------------------------

    if intent in [
        "conversation",
        "casual",
        "greeting",
    ]:
        return set_mode("casual")

    # ------------------------------------------------
    # DEFAULT
    # ------------------------------------------------

    return set_mode("balanced")


# ============================================================
# MODE VALUES
# ============================================================

def energy():

    return get()["energy"]


def verbosity():

    return get()["verbosity"]


def responsiveness():

    return get()["responsiveness"]


def recovery_bias():

    return get()["recovery_bias"]


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

    runtime_state = runtime_state or {}

    mode = auto(runtime_state)

    config = get(mode)

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "active_mode": mode,
        "last_mode": LAST_MODE,
        "config": config,
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "active_mode": ACTIVE_MODE,
        "last_mode": LAST_MODE,
        "available_modes": list(
            MODES.keys()
        ),
        "history_size": len(
            MODE_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def mode(runtime_state=None):
    return process(runtime_state)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" MODES CORE STAGE3600")
    print("================================\n")

    runtime_state = {
        "pressure": 0.82,
        "stability": 0.64,
        "intent": "debug",
    }

    print(process(runtime_state))

    print(status())
