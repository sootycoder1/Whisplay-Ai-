# ============================================================
# WATCHDOG CORE — STAGE 3600
# Runtime watchdog + protection supervision layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "WATCHDOG_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# WATCHDOG STATE
# ============================================================

WATCHDOG = {
    "active": True,
    "armed": True,
    "triggered": False,
    "last_check": 0.0,
    "last_trigger": 0.0,
    "cycles": 0,
    "failures": 0,
}


# ============================================================
# WATCH TARGETS
# ============================================================

TARGETS = {
    "runtime": True,
    "state": True,
    "health": True,
    "recovery": True,
    "strategy": True,
    "signals": True,
    "events": True,
    "session": True,
}


# ============================================================
# LIMITS
# ============================================================

LIMITS = {
    "pressure_critical": 0.95,
    "stability_critical": 0.20,
    "ambiguity_critical": 0.92,
    "max_failures": 5,
}


# ============================================================
# HISTORY
# ============================================================

WATCH_HISTORY = []

MAX_HISTORY = 300


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[WATCHDOG] {message}")


def remember(event, details=None):

    WATCH_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(WATCH_HISTORY) > MAX_HISTORY:
        WATCH_HISTORY.pop(0)


# ============================================================
# ARM / DISARM
# ============================================================

def arm():

    WATCHDOG["armed"] = True

    remember("armed")

    log("armed")

    return WATCHDOG["armed"]


def disarm():

    WATCHDOG["armed"] = False

    remember("disarmed")

    log("disarmed")

    return WATCHDOG["armed"]


# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable():

    WATCHDOG["active"] = True

    remember("enabled")

    log("enabled")

    return WATCHDOG["active"]


def disable():

    WATCHDOG["active"] = False

    remember("disabled")

    log("disabled")

    return WATCHDOG["active"]


# ============================================================
# TRIGGER
# ============================================================

def trigger(reason="unknown"):

    WATCHDOG["triggered"] = True

    WATCHDOG["last_trigger"] = now()

    WATCHDOG["failures"] += 1

    remember("trigger", {
        "reason": reason,
    })

    log(f"triggered: {reason}")

    return status()


# ============================================================
# RESET
# ============================================================

def reset():

    WATCHDOG["triggered"] = False

    remember("reset")

    log("reset")

    return status()


# ============================================================
# TARGET CONTROL
# ============================================================

def enable_target(name):

    if name not in TARGETS:
        return False

    TARGETS[name] = True

    return True


def disable_target(name):

    if name not in TARGETS:
        return False

    TARGETS[name] = False

    return True


# ============================================================
# VALIDATION
# ============================================================

def validate(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    stability = runtime_state.get(
        "stability",
        1.0,
    )

    ambiguity = runtime_state.get(
        "ambiguity",
        0.0,
    )

    blocked = runtime_state.get(
        "blocked",
        False,
    )

    failures = []

    if pressure >= LIMITS["pressure_critical"]:

        failures.append(
            "pressure_critical"
        )

    if stability <= LIMITS["stability_critical"]:

        failures.append(
            "stability_critical"
        )

    if ambiguity >= LIMITS["ambiguity_critical"]:

        failures.append(
            "ambiguity_critical"
        )

    if blocked:

        failures.append(
            "runtime_blocked"
        )

    return failures


# ============================================================
# WATCH CYCLE
# ============================================================

def cycle(runtime_state=None):

    runtime_state = runtime_state or {}

    if not WATCHDOG["active"]:
        return status()

    if not WATCHDOG["armed"]:
        return status()

    WATCHDOG["cycles"] += 1

    WATCHDOG["last_check"] = now()

    failures = validate(runtime_state)

    if failures:

        trigger(",".join(failures))

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "healthy": len(failures) == 0,
        "failures": failures,
        "watchdog": dict(WATCHDOG),
    }


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

    return cycle(runtime_state)


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "watchdog": dict(WATCHDOG),
        "targets": dict(TARGETS),
        "history_size": len(
            WATCH_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def watchdog(runtime_state=None):
    return process(runtime_state)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" WATCHDOG CORE STAGE3600")
    print("================================\n")

    runtime_state = {
        "pressure": 0.97,
        "stability": 0.18,
        "ambiguity": 0.41,
    }

    print(process(runtime_state))

    print(status())
