# ============================================================
# RUNTIME CORE — STAGE 3600
# Central runtime authority + orchestration gateway
# ============================================================

import time


# ============================================================
# CORE IMPORTS
# ============================================================

import registry_core
import signal_core
import events_core
import session_core
import state_core
import health_core
import recovery_core
import loader_core

try:
    import strategy_engine
except Exception:
    strategy_engine = None


# ============================================================
# ENGINE
# ============================================================

STAGE = 3600

ENGINE_NAME = "RUNTIME_CORE"
ENGINE_VERSION = "3600.1-GATEWAY"

DEBUG = True


# ============================================================
# RUNTIME FLAGS
# ============================================================

RUNTIME_ACTIVE = False

BOOTED = False
SHUTDOWN = False

RUNTIME_CYCLES = 0

LAST_RUNTIME_TIME = 0.0


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[RUNTIME] {message}")


# ============================================================
# BOOT
# ============================================================

def boot():

    global RUNTIME_ACTIVE
    global BOOTED

    if BOOTED:
        return status()

    log("booting runtime")

    systems = [
        "registry_core",
        "signal_core",
        "events_core",
        "session_core",
        "state_core",
        "health_core",
        "recovery_core",
        "loader_core",
    ]

    for system in systems:

        loader_core.load(
            name=system,
            required=True,
        )

    if strategy_engine:

        loader_core.load(
            name="strategy_engine",
            required=False,
        )

    session_core.start()

    signal_core.create(
        "runtime_boot",
        source="runtime_core",
        level="important",
    )

    events_core.create(
        "runtime_initialized",
        source="runtime_core",
        level="important",
    )

    RUNTIME_ACTIVE = True
    BOOTED = True

    log("runtime online")

    return status()


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown():

    global RUNTIME_ACTIVE
    global SHUTDOWN

    signal_core.create(
        "runtime_shutdown",
        source="runtime_core",
        level="important",
    )

    events_core.create(
        "runtime_shutdown",
        source="runtime_core",
        level="important",
    )

    session_core.stop()

    RUNTIME_ACTIVE = False
    SHUTDOWN = True

    log("runtime shutdown")

    return status()


# ============================================================
# RUNTIME CYCLE
# ============================================================

def cycle(runtime_state=None):

    global RUNTIME_CYCLES
    global LAST_RUNTIME_TIME

    runtime_state = runtime_state or {}

    RUNTIME_CYCLES += 1

    LAST_RUNTIME_TIME = now()

    # ------------------------------------------------
    # HEALTH
    # ------------------------------------------------

    health = health_core.process(
        runtime_state
    )

    # ------------------------------------------------
    # RECOVERY
    # ------------------------------------------------

    recovery = recovery_core.process(
        runtime_state
    )

    # ------------------------------------------------
    # SIGNALS
    # ------------------------------------------------

    signals = signal_core.broadcast(
        runtime_state
    )

    # ------------------------------------------------
    # EVENTS
    # ------------------------------------------------

    events = events_core.broadcast(
        runtime_state
    )

    # ------------------------------------------------
    # STRATEGY
    # ------------------------------------------------

    strategy = None

    if strategy_engine:

        try:

            strategy = strategy_engine.process(
                runtime_state.get(
                    "last_input",
                    "",
                ),
                runtime_state,
            )

        except Exception as e:

            signal_core.create(
                "strategy_failure",
                source="runtime_core",
                level="important",
                payload={
                    "error": str(e),
                },
            )

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "cycle": RUNTIME_CYCLES,
        "health": health,
        "recovery": recovery,
        "signals": signals,
        "events": events,
        "strategy": strategy,
    }


# ============================================================
# RUNTIME INPUT
# ============================================================

def input(text, intent=None):

    session_core.input(
        text,
        intent=intent,
    )

    state_core.on_input(
        text,
        intent=intent,
    )

    signal_core.create(
        "runtime_input",
        source="runtime_core",
        payload={
            "text": text,
            "intent": intent,
        },
    )

    return True


# ============================================================
# RUNTIME OUTPUT
# ============================================================

def output(text):

    session_core.output(text)

    state_core.on_output(text)

    signal_core.create(
        "runtime_output",
        source="runtime_core",
        payload={
            "text": text,
        },
    )

    return True


# ============================================================
# PROCESS
# ============================================================

def process(text, runtime_state=None):

    runtime_state = runtime_state or {}

    input(text)

    runtime_state["last_input"] = text

    result = cycle(runtime_state)

    return result


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "runtime_active": RUNTIME_ACTIVE,
        "booted": BOOTED,
        "shutdown": SHUTDOWN,
        "runtime_cycles": RUNTIME_CYCLES,
        "last_runtime_time": LAST_RUNTIME_TIME,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" RUNTIME CORE STAGE3600")
    print("================================\n")

    boot()

    runtime_state = {
        "pressure": 0.32,
        "stability": 0.91,
        "ambiguity": 0.12,
    }

    result = process(
        "assistant open runtime logs",
        runtime_state,
    )

    print(result)

    print(status())
