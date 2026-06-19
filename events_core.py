# ============================================================
# EVENTS CORE — STAGE 3600
# Runtime event orchestration + lifecycle layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "EVENTS_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# EVENT STORAGE
# ============================================================

EVENTS = []

EVENT_HISTORY = []

MAX_EVENTS = 120
MAX_HISTORY = 300


# ============================================================
# EVENT PRIORITY
# ============================================================

PRIORITY = {
    "low": 1,
    "normal": 2,
    "important": 3,
    "critical": 4,
}


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[EVENTS] {message}")


def remember(event):

    EVENT_HISTORY.append(event)

    while len(EVENT_HISTORY) > MAX_HISTORY:
        EVENT_HISTORY.pop(0)


# ============================================================
# EVENT CREATE
# ============================================================

def create(
    name,
    source="runtime",
    level="normal",
    payload=None,
):

    payload = payload or {}

    event = {
        "name": str(name),
        "source": str(source),
        "level": level,
        "priority": PRIORITY.get(
            level,
            PRIORITY["normal"],
        ),
        "payload": payload,
        "created": now(),
        "handled": False,
        "active": True,
    }

    EVENTS.append(event)

    while len(EVENTS) > MAX_EVENTS:
        EVENTS.pop(0)

    remember(dict(event))

    log(f"{level}: {name}")

    return event


# ============================================================
# FETCH
# ============================================================

def fetch(limit=10):

    ordered = sorted(
        EVENTS,
        key=lambda e: (
            e["priority"],
            e["created"],
        ),
        reverse=True,
    )

    return ordered[:limit]


# ============================================================
# FETCH ACTIVE
# ============================================================

def active(limit=10):

    output = []

    for event in EVENTS:

        if event["active"]:
            output.append(event)

    ordered = sorted(
        output,
        key=lambda e: (
            e["priority"],
            e["created"],
        ),
        reverse=True,
    )

    return ordered[:limit]


# ============================================================
# FETCH UNHANDLED
# ============================================================

def unhandled(limit=10):

    output = []

    for event in EVENTS:

        if not event["handled"]:
            output.append(event)

    ordered = sorted(
        output,
        key=lambda e: (
            e["priority"],
            e["created"],
        ),
        reverse=True,
    )

    return ordered[:limit]


# ============================================================
# HANDLE
# ============================================================

def handle(index):

    try:

        EVENTS[index]["handled"] = True

        return True

    except Exception:
        return False


# ============================================================
# COMPLETE
# ============================================================

def complete(index):

    try:

        EVENTS[index]["active"] = False
        EVENTS[index]["handled"] = True

        return True

    except Exception:
        return False


# ============================================================
# REMOVE
# ============================================================

def remove(name):

    removed = 0

    remaining = []

    for event in EVENTS:

        if event["name"] == name:
            removed += 1
            continue

        remaining.append(event)

    EVENTS[:] = remaining

    log(f"removed: {name}")

    return removed


# ============================================================
# EXISTS
# ============================================================

def exists(name):

    for event in EVENTS:

        if event["name"] == name:
            return True

    return False


# ============================================================
# CLEAR
# ============================================================

def clear():

    EVENTS.clear()

    log("events cleared")

    return True


# ============================================================
# CRITICAL EVENTS
# ============================================================

def critical():

    output = []

    for event in EVENTS:

        if event["level"] == "critical":
            output.append(event)

    return output


# ============================================================
# BROADCAST
# ============================================================

def broadcast(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    stability = runtime_state.get(
        "stability",
        1.0,
    )

    blocked = runtime_state.get(
        "blocked",
        False,
    )

    if pressure >= 0.90:

        create(
            "pressure_critical",
            source="state_core",
            level="critical",
            payload={
                "pressure": pressure,
            },
        )

    if stability <= 0.25:

        create(
            "stability_critical",
            source="health_core",
            level="critical",
            payload={
                "stability": stability,
            },
        )

    if blocked:

        create(
            "runtime_blocked",
            source="runtime",
            level="important",
        )

    return unhandled()


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "events": len(EVENTS),
        "history": len(EVENT_HISTORY),
        "critical": len(critical()),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def event(
    name,
    source="runtime",
    level="normal",
    payload=None,
):

    return create(
        name,
        source,
        level,
        payload,
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" EVENTS CORE STAGE3600")
    print("================================\n")

    create(
        "runtime_boot",
        source="loader_core",
        level="important",
    )

    create(
        "display_ready",
        source="display",
    )

    print(fetch())

    print(status())
