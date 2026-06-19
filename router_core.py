# ============================================================
# ROUTER CORE — STAGE 3600
# Runtime routing + subsystem direction layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "ROUTER_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# ROUTES
# ============================================================

ROUTES = {
    "system": "runtime_core",
    "runtime": "runtime_core",
    "debug": "debug_core",
    "health": "health_core",
    "recovery": "recovery_core",
    "state": "state_core",
    "signals": "signal_core",
    "events": "events_core",
    "session": "session_core",
    "queue": "queue_core",
    "strategy": "strategy_engine",
    "modes": "modes_core",
}


# ============================================================
# ROUTER STATE
# ============================================================

LAST_ROUTE = None

ROUTE_HISTORY = []

MAX_HISTORY = 300


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[ROUTER] {message}")


def remember(event, details=None):

    ROUTE_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(ROUTE_HISTORY) > MAX_HISTORY:
        ROUTE_HISTORY.pop(0)


# ============================================================
# REGISTER ROUTE
# ============================================================

def register(
    name,
    destination,
):

    ROUTES[str(name)] = str(destination)

    remember("register_route", {
        "name": name,
        "destination": destination,
    })

    log(f"route: {name} -> {destination}")

    return True


# ============================================================
# REMOVE ROUTE
# ============================================================

def remove(name):

    if name not in ROUTES:
        return False

    ROUTES.pop(name)

    remember("remove_route", {
        "name": name,
    })

    log(f"removed: {name}")

    return True


# ============================================================
# EXISTS
# ============================================================

def exists(name):

    return name in ROUTES


# ============================================================
# DESTINATION
# ============================================================

def destination(name):

    return ROUTES.get(name)


# ============================================================
# SIMPLE ANALYSIS
# ============================================================

def analyze(text):

    text = str(text or "").lower()

    if any(word in text for word in [
        "debug",
        "traceback",
        "error",
        "log",
    ]):
        return "debug"

    if any(word in text for word in [
        "health",
        "status",
        "integrity",
    ]):
        return "health"

    if any(word in text for word in [
        "recover",
        "recovery",
        "stability",
    ]):
        return "recovery"

    if any(word in text for word in [
        "signal",
        "event",
        "queue",
    ]):
        return "signals"

    if any(word in text for word in [
        "mode",
        "state",
        "runtime",
    ]):
        return "runtime"

    return "system"


# ============================================================
# ROUTE
# ============================================================

def route(
    text,
    metadata=None,
):

    global LAST_ROUTE

    metadata = metadata or {}

    intent = analyze(text)

    target = ROUTES.get(
        intent,
        "runtime_core",
    )

    route_data = {
        "intent": intent,
        "target": target,
        "text": text,
        "metadata": metadata,
        "time": now(),
    }

    LAST_ROUTE = route_data

    remember("route", {
        "intent": intent,
        "target": target,
    })

    log(f"{intent} -> {target}")

    return route_data


# ============================================================
# PRIORITY ROUTE
# ============================================================

def priority_route(
    text,
    level="normal",
):

    route_data = route(text)

    route_data["priority"] = level

    remember("priority_route", {
        "level": level,
        "target": route_data["target"],
    })

    return route_data


# ============================================================
# PROCESS
# ============================================================

def process(
    text,
    runtime_state=None,
):

    runtime_state = runtime_state or {}

    blocked = runtime_state.get(
        "blocked",
        False,
    )

    recovery = runtime_state.get(
        "recovery",
        False,
    )

    if blocked:

        return {
            "intent": "critical",
            "target": "recovery_core",
            "blocked": True,
        }

    if recovery:

        return {
            "intent": "recovery",
            "target": "recovery_core",
            "recovery": True,
        }

    return route(text)


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "routes": dict(ROUTES),
        "last_route": LAST_ROUTE,
        "history_size": len(
            ROUTE_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def router(
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
    print(" ROUTER CORE STAGE3600")
    print("================================\n")

    print(
        process(
            "show runtime logs"
        )
    )

    print(
        process(
            "recovery system unstable"
        )
    )

    print(status())
