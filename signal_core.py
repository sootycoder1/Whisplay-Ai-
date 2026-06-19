# ============================================================
# SIGNAL CORE — STAGE 3600
# Runtime signal + event propagation layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "SIGNAL_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# SIGNAL STORAGE
# ============================================================

SIGNALS = []

SIGNAL_HISTORY = []

MAX_SIGNALS = 80
MAX_HISTORY = 200


# ============================================================
# SIGNAL PRIORITY
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
        print(f"[SIGNAL] {message}")


def remember(signal):

    SIGNAL_HISTORY.append(signal)

    while len(SIGNAL_HISTORY) > MAX_HISTORY:
        SIGNAL_HISTORY.pop(0)


# ============================================================
# SIGNAL CREATION
# ============================================================

def create(
    signal,
    source="runtime",
    level="normal",
    payload=None,
):

    payload = payload or {}

    entry = {
        "signal": str(signal),
        "source": str(source),
        "level": level,
        "priority": PRIORITY.get(
            level,
            PRIORITY["normal"],
        ),
        "payload": payload,
        "time": now(),
        "handled": False,
    }

    SIGNALS.append(entry)

    while len(SIGNALS) > MAX_SIGNALS:
        SIGNALS.pop(0)

    remember(dict(entry))

    log(f"{level}: {signal}")

    return entry


# ============================================================
# FETCH
# ============================================================

def fetch(limit=10):

    ordered = sorted(
        SIGNALS,
        key=lambda s: (
            s["priority"],
            s["time"],
        ),
        reverse=True,
    )

    return ordered[:limit]


# ============================================================
# FETCH UNHANDLED
# ============================================================

def fetch_unhandled(limit=10):

    pending = []

    for signal in SIGNALS:

        if not signal["handled"]:
            pending.append(signal)

    ordered = sorted(
        pending,
        key=lambda s: (
            s["priority"],
            s["time"],
        ),
        reverse=True,
    )

    return ordered[:limit]


# ============================================================
# MARK HANDLED
# ============================================================

def handled(index):

    try:

        SIGNALS[index]["handled"] = True

        return True

    except Exception:
        return False


# ============================================================
# CLEAR
# ============================================================

def clear():

    SIGNALS.clear()

    log("signals cleared")

    return True


# ============================================================
# REMOVE
# ============================================================

def remove(signal_name):

    removed = 0

    remaining = []

    for signal in SIGNALS:

        if signal["signal"] == signal_name:
            removed += 1
            continue

        remaining.append(signal)

    SIGNALS[:] = remaining

    log(f"removed: {signal_name}")

    return removed


# ============================================================
# EXISTS
# ============================================================

def exists(signal_name):

    for signal in SIGNALS:

        if signal["signal"] == signal_name:
            return True

    return False


# ============================================================
# CRITICAL CHECK
# ============================================================

def critical():

    critical_signals = []

    for signal in SIGNALS:

        if signal["level"] == "critical":
            critical_signals.append(signal)

    return critical_signals


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
            source="state_core",
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

    return fetch_unhandled()


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "active_signals": len(SIGNALS),
        "history_size": len(SIGNAL_HISTORY),
        "critical": len(critical()),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def signal(
    signal_name,
    source="runtime",
    level="normal",
    payload=None,
):

    return create(
        signal_name,
        source,
        level,
        payload,
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" SIGNAL CORE STAGE3600")
    print("================================\n")

    create(
        "runtime_boot",
        source="system",
        level="important",
    )

    create(
        "display_ready",
        source="display",
    )

    print(fetch())

    print(status())
