# ============================================================
# RECOVERY CORE — STAGE 3600
# Stable runtime recovery fixture
# ============================================================

import time


STAGE = 3600
ENGINE_NAME = "RECOVERY_CORE"
ENGINE_VERSION = "3600.3-FIXTURE"

DEBUG = True


RECOVERY = {
    "active": False,
    "safe_mode": False,
    "degraded_mode": False,
    "locked": False,
    "level": 0,
    "count": 0,
    "last_reason": "",
    "last_time": 0.0,
    "cooldown_until": 0.0,
}


LIMITS = {
    "pressure_critical": 0.90,
    "pressure_warning": 0.70,
    "stability_critical": 0.25,
    "stability_warning": 0.50,
    "ambiguity_critical": 0.85,
    "cooldown_seconds": 2.0,
    "safe_level": 2,
    "degraded_level": 4,
}


def now():
    return time.time()


def log(msg):
    if DEBUG:
        print(f"[RECOVERY] {msg}")


def clamp(value, low, high):
    return max(low, min(high, value))


def in_cooldown():
    return now() < RECOVERY["cooldown_until"]


def validate(runtime_state=None):
    runtime_state = runtime_state or {}

    pressure = runtime_state.get("pressure", 0.0)
    stability = runtime_state.get("stability", 1.0)
    ambiguity = runtime_state.get("ambiguity", 0.0)
    blocked = runtime_state.get("blocked", False)
    recovery = runtime_state.get("recovery", False)

    failures = []
    warnings = []

    if pressure >= LIMITS["pressure_critical"]:
        failures.append("pressure_critical")
    elif pressure >= LIMITS["pressure_warning"]:
        warnings.append("pressure_warning")

    if stability <= LIMITS["stability_critical"]:
        failures.append("stability_critical")
    elif stability <= LIMITS["stability_warning"]:
        warnings.append("stability_warning")

    if ambiguity >= LIMITS["ambiguity_critical"]:
        failures.append("ambiguity_critical")

    if blocked:
        failures.append("runtime_blocked")

    if recovery:
        warnings.append("external_recovery_flag")

    return {
        "healthy": len(failures) == 0,
        "failures": failures,
        "warnings": warnings,
    }


def start(reason="unknown"):
    if RECOVERY["locked"]:
        return status()

    RECOVERY["active"] = True
    RECOVERY["level"] += 1
    RECOVERY["count"] += 1
    RECOVERY["last_reason"] = str(reason)
    RECOVERY["last_time"] = now()
    RECOVERY["cooldown_until"] = now() + LIMITS["cooldown_seconds"]

    if RECOVERY["level"] >= LIMITS["safe_level"]:
        RECOVERY["safe_mode"] = True

    if RECOVERY["level"] >= LIMITS["degraded_level"]:
        RECOVERY["degraded_mode"] = True

    log(f"started: {reason}")

    return status()


def stop():
    RECOVERY["active"] = False
    RECOVERY["level"] = max(0, RECOVERY["level"] - 1)

    if RECOVERY["level"] < LIMITS["safe_level"]:
        RECOVERY["safe_mode"] = False

    if RECOVERY["level"] < LIMITS["degraded_level"]:
        RECOVERY["degraded_mode"] = False

    log("stopped")

    return status()


def lock():
    RECOVERY["locked"] = True
    log("locked")
    return status()


def unlock():
    RECOVERY["locked"] = False
    log("unlocked")
    return status()


def stabilize(runtime_state=None):
    runtime_state = dict(runtime_state or {})

    pressure = runtime_state.get("pressure", 0.0)
    stability = runtime_state.get("stability", 1.0)
    ambiguity = runtime_state.get("ambiguity", 0.0)

    runtime_state["pressure"] = round(clamp(pressure * 0.82, 0.0, 1.0), 3)
    runtime_state["stability"] = round(clamp(stability + 0.08, 0.0, 1.0), 3)
    runtime_state["ambiguity"] = round(clamp(ambiguity * 0.88, 0.0, 1.0), 3)

    runtime_state["recovery"] = RECOVERY["active"]
    runtime_state["safe_mode"] = RECOVERY["safe_mode"]
    runtime_state["degraded_mode"] = RECOVERY["degraded_mode"]

    return runtime_state


def process(runtime_state=None):
    runtime_state = runtime_state or {}

    health = validate(runtime_state)

    if not health["healthy"] and not in_cooldown():
        start(",".join(health["failures"]))

    stabilized_state = stabilize(runtime_state)

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "healthy": health["healthy"],
        "failures": health["failures"],
        "warnings": health["warnings"],
        "recovery": status(),
        "runtime_state": stabilized_state,
    }


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "active": RECOVERY["active"],
        "safe_mode": RECOVERY["safe_mode"],
        "degraded_mode": RECOVERY["degraded_mode"],
        "locked": RECOVERY["locked"],
        "level": RECOVERY["level"],
        "count": RECOVERY["count"],
        "last_reason": RECOVERY["last_reason"],
        "last_time": RECOVERY["last_time"],
        "cooldown_active": in_cooldown(),
    }


def recovery(runtime_state=None):
    return process(runtime_state)


if __name__ == "__main__":
    test_state = {
        "pressure": 0.94,
        "stability": 0.22,
        "ambiguity": 0.71,
        "blocked": False,
    }

    print(process(test_state))
