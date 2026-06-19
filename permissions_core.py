# ============================================================
# PERMISSIONS CORE — STAGE 3600
# Runtime permissions + execution authority layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "PERMISSIONS_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# PERMISSION LEVELS
# ============================================================

LEVELS = {
    "none": 0,
    "read": 1,
    "basic": 2,
    "trusted": 3,
    "system": 4,
    "core": 5,
}


# ============================================================
# RUNTIME POLICIES
# ============================================================

POLICIES = {

    "runtime_core": "core",
    "recovery_core": "core",
    "health_core": "system",

    "registry_core": "trusted",
    "queue_core": "trusted",
    "router_core": "trusted",

    "signal_core": "basic",
    "events_core": "basic",
    "context_core": "basic",
    "session_core": "basic",

    "strategy_engine": "trusted",

    "display": "basic",
    "audio": "basic",

    "shell": "none",
    "network": "none",
    "filesystem": "read",
}


# ============================================================
# SECURITY STATE
# ============================================================

SECURITY = {
    "safe_mode": False,
    "lockdown": False,
    "permission_failures": 0,
    "last_failure": "",
    "last_check": 0.0,
}


# ============================================================
# HISTORY
# ============================================================

PERMISSION_HISTORY = []

MAX_HISTORY = 300


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[PERMISSIONS] {message}")


def remember(event, details=None):

    PERMISSION_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(PERMISSION_HISTORY) > MAX_HISTORY:
        PERMISSION_HISTORY.pop(0)


# ============================================================
# ACCESS
# ============================================================

def level(name):

    policy = POLICIES.get(
        name,
        "none",
    )

    return LEVELS.get(
        policy,
        0,
    )


def allowed(
    source,
    target,
):

    source_level = level(source)
    target_level = level(target)

    SECURITY["last_check"] = now()

    if SECURITY["lockdown"]:

        remember("denied", {
            "source": source,
            "target": target,
            "reason": "lockdown",
        })

        return False

    permitted = source_level >= target_level

    if not permitted:

        SECURITY["permission_failures"] += 1

        SECURITY["last_failure"] = (
            f"{source}->{target}"
        )

        remember("denied", {
            "source": source,
            "target": target,
        })

        log(
            f"denied: {source} -> {target}"
        )

    return permitted


# ============================================================
# SAFE MODE
# ============================================================

def enable_safe_mode():

    SECURITY["safe_mode"] = True

    remember("safe_mode_enabled")

    log("safe mode enabled")

    return True


def disable_safe_mode():

    SECURITY["safe_mode"] = False

    remember("safe_mode_disabled")

    log("safe mode disabled")

    return True


# ============================================================
# LOCKDOWN
# ============================================================

def lockdown():

    SECURITY["lockdown"] = True

    remember("lockdown")

    log("lockdown enabled")

    return True


def unlock():

    SECURITY["lockdown"] = False

    remember("unlock")

    log("lockdown disabled")

    return True


# ============================================================
# REGISTER POLICY
# ============================================================

def register(
    name,
    permission,
):

    if permission not in LEVELS:
        return False

    POLICIES[name] = permission

    remember("register_policy", {
        "name": name,
        "permission": permission,
    })

    log(
        f"policy: {name} -> {permission}"
    )

    return True


# ============================================================
# REMOVE POLICY
# ============================================================

def remove(name):

    if name not in POLICIES:
        return False

    POLICIES.pop(name)

    remember("remove_policy", {
        "name": name,
    })

    log(f"removed: {name}")

    return True


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

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
        lockdown()

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "safe_mode": SECURITY["safe_mode"],
        "lockdown": SECURITY["lockdown"],
        "permission_failures": SECURITY[
            "permission_failures"
        ],
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "security": dict(SECURITY),
        "policies": dict(POLICIES),
        "history_size": len(
            PERMISSION_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def permissions():
    return status()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" PERMISSIONS CORE STAGE3600")
    print("================================\n")

    print(
        allowed(
            "runtime_core",
            "health_core",
        )
    )

    print(
        allowed(
            "signal_core",
            "runtime_core",
        )
    )

    print(status())
