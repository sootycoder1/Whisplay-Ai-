# ============================================================
# HEALTH CORE — STAGE 3600
# Runtime health + integrity monitoring layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "HEALTH_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# HEALTH STATE
# ============================================================

HEALTH = {
    "runtime": 1.0,
    "strategy": 1.0,
    "state": 1.0,
    "memory": 1.0,
    "brain": 1.0,
    "display": 1.0,
    "audio": 1.0,
    "registry": 1.0,
    "signal": 1.0,
    "session": 1.0,
}


STATUS = {
    "healthy": True,
    "warnings": [],
    "failures": [],
    "last_check": 0.0,
}


# ============================================================
# HISTORY
# ============================================================

HEALTH_HISTORY = []

MAX_HISTORY = 200


# ============================================================
# LIMITS
# ============================================================

LIMITS = {
    "healthy": 0.80,
    "warning": 0.55,
    "critical": 0.30,
}


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def clamp(value, low, high):

    return max(low, min(high, value))


def log(message):

    if DEBUG:
        print(f"[HEALTH] {message}")


def remember(event, details=None):

    HEALTH_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(HEALTH_HISTORY) > MAX_HISTORY:
        HEALTH_HISTORY.pop(0)


# ============================================================
# HEALTH ACCESS
# ============================================================

def set_health(component, value):

    HEALTH[component] = clamp(
        float(value),
        0.0,
        1.0,
    )

    remember("health_update", {
        "component": component,
        "value": HEALTH[component],
    })

    return HEALTH[component]


def get_health(component=None):

    if component is None:
        return dict(HEALTH)

    return HEALTH.get(component)


# ============================================================
# DAMAGE
# ============================================================

def damage(component, amount):

    if component not in HEALTH:
        return None

    HEALTH[component] -= abs(amount)

    HEALTH[component] = clamp(
        HEALTH[component],
        0.0,
        1.0,
    )

    remember("damage", {
        "component": component,
        "amount": amount,
    })

    return HEALTH[component]


# ============================================================
# RECOVERY
# ============================================================

def recover(component, amount):

    if component not in HEALTH:
        return None

    HEALTH[component] += abs(amount)

    HEALTH[component] = clamp(
        HEALTH[component],
        0.0,
        1.0,
    )

    remember("recover", {
        "component": component,
        "amount": amount,
    })

    return HEALTH[component]


# ============================================================
# GLOBAL RECOVERY
# ============================================================

def recover_all(amount=0.05):

    for component in HEALTH:

        HEALTH[component] += amount

        HEALTH[component] = clamp(
            HEALTH[component],
            0.0,
            1.0,
        )

    remember("recover_all", {
        "amount": amount,
    })

    log("global recovery")

    return dict(HEALTH)


# ============================================================
# VALIDATION
# ============================================================

def validate():

    warnings = []
    failures = []

    for component, value in HEALTH.items():

        if value <= LIMITS["critical"]:

            failures.append({
                "component": component,
                "value": value,
            })

        elif value <= LIMITS["warning"]:

            warnings.append({
                "component": component,
                "value": value,
            })

    STATUS["healthy"] = len(failures) == 0

    STATUS["warnings"] = warnings
    STATUS["failures"] = failures

    STATUS["last_check"] = now()

    remember("validate", {
        "healthy": STATUS["healthy"],
        "warnings": len(warnings),
        "failures": len(failures),
    })

    return dict(STATUS)


# ============================================================
# SCORE
# ============================================================

def score():

    values = list(HEALTH.values())

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        3,
    )


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

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

    if pressure >= 0.90:
        damage("runtime", 0.08)

    if stability <= 0.30:
        damage("state", 0.10)

    if ambiguity >= 0.85:
        damage("strategy", 0.07)

    validation = validate()

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "score": score(),
        "healthy": validation["healthy"],
        "warnings": validation["warnings"],
        "failures": validation["failures"],
        "health": dict(HEALTH),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "score": score(),
        "status": dict(STATUS),
        "health": dict(HEALTH),
        "history_size": len(HEALTH_HISTORY),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def health(runtime_state=None):
    return process(runtime_state)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" HEALTH CORE STAGE3600")
    print("================================\n")

    runtime_state = {
        "pressure": 0.93,
        "stability": 0.24,
        "ambiguity": 0.82,
    }

    print(process(runtime_state))
