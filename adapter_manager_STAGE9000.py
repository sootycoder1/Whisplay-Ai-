# ============================================================
# ADAPTER MANAGER
# STAGE 9000
# Unified adapter orchestration + runtime bridge system
# ============================================================

import time
import threading


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "adapter_manager"

ENGINE_STAGE = 9000


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "adaptive",
    "status": "online",
    "active_adapter": None,
    "adapter_count": 0,
    "dispatch_count": 0,
    "failures": 0,
    "recoveries": 0,
    "pressure": 0.0,
    "focus": 1.0,
    "stability": 1.0,
    "runtime_cycles": 0,
    "last_adapter": None,
    "last_route": None,
    "created": time.time(),
    "updated": time.time(),
}


# ============================================================
# ADAPTER STORE
# ============================================================

ADAPTERS = {}

ROUTES = []

EVENTS = []


# ============================================================
# FLAGS
# ============================================================

FLAGS = {
    "adapter_control": True,
    "safe_dispatch": True,
    "runtime_monitoring": True,
    "adaptive_routing": True,
    "pressure_awareness": True,
    "event_tracking": True,
    "recovery_enabled": True,
}


# ============================================================
# LOCK
# ============================================================

adapter_lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def now():

    return time.time()


def clamp(
    value,
    minimum=0.0,
    maximum=1.0,
):

    return max(
        minimum,
        min(maximum, value)
    )


# ============================================================
# REGISTER ADAPTER
# ============================================================

def register_adapter(
    name,
    handler,
    metadata=None,
):

    with adapter_lock:

        ADAPTERS[name] = {
            "handler": handler,
            "metadata": metadata or {},
            "registered": now(),
            "calls": 0,
            "failures": 0,
            "status": "online",
        }

        STATE["adapter_count"] = len(
            ADAPTERS
        )

        STATE["updated"] = now()

        print(
            f"[ADAPTER] registered "
            f"{name}"
        )


# ============================================================
# REMOVE ADAPTER
# ============================================================

def remove_adapter(name):

    with adapter_lock:

        if name in ADAPTERS:

            del ADAPTERS[name]

            STATE["adapter_count"] = len(
                ADAPTERS
            )

            print(
                f"[ADAPTER] removed "
                f"{name}"
            )


# ============================================================
# DISPATCH
# ============================================================

def dispatch(
    adapter_name,
    payload=None,
):

    with adapter_lock:

        if adapter_name not in ADAPTERS:

            STATE["failures"] += 1

            return {
                "ok": False,
                "error": "adapter missing",
            }

        adapter = ADAPTERS[
            adapter_name
        ]

        handler = adapter["handler"]

        try:

            adapter["calls"] += 1

            STATE["dispatch_count"] += 1

            STATE["active_adapter"] = (
                adapter_name
            )

            STATE["last_adapter"] = (
                adapter_name
            )

            STATE["last_route"] = (
                f"dispatch:{adapter_name}"
            )

            ROUTES.append(
                STATE["last_route"]
            )

            result = handler(payload)

            EVENTS.append({
                "adapter": adapter_name,
                "payload": payload,
                "timestamp": now(),
            })

            STATE["updated"] = now()

            return {
                "ok": True,
                "adapter": adapter_name,
                "result": result,
            }

        except Exception as e:

            adapter["failures"] += 1

            STATE["failures"] += 1

            print(
                f"[ADAPTER ERROR] {e}"
            )

            return {
                "ok": False,
                "adapter": adapter_name,
                "error": str(e),
            }


# ============================================================
# RECOVERY
# ============================================================

def recover():

    STATE["recoveries"] += 1

    STATE["pressure"] *= 0.5

    STATE["updated"] = now()

    print(
        "[ADAPTER] recovery complete"
    )

    return True


# ============================================================
# PROCESS
# ============================================================

def process():

    with adapter_lock:

        STATE["runtime_cycles"] += 1

        pressure = (
            STATE["failures"] * 0.05
        )

        STATE["pressure"] = clamp(
            pressure
        )

        STATE["stability"] = clamp(
            1.0 - STATE["pressure"]
        )

        STATE["updated"] = now()

        return {
            "adapters": len(ADAPTERS),
            "dispatches": STATE[
                "dispatch_count"
            ],
            "pressure": STATE["pressure"],
        }


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "adapters": dict(ADAPTERS),
        "flags": dict(FLAGS),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return (
        "\n"
        "==============================\n"
        " ADAPTER MANAGER STAGE 9000\n"
        "==============================\n"
        f"STATUS:        {STATE['status']}\n"
        f"ADAPTERS:      {STATE['adapter_count']}\n"
        f"DISPATCHES:    {STATE['dispatch_count']}\n"
        f"FAILURES:      {STATE['failures']}\n"
        f"RECOVERIES:    {STATE['recoveries']}\n"
        f"PRESSURE:      {STATE['pressure']:.2f}\n"
        f"STABILITY:     {STATE['stability']:.2f}\n"
        f"LAST ADAPTER:  {STATE['last_adapter']}\n"
        f"CYCLES:        {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


# ============================================================
# TEST ADAPTER
# ============================================================

def speech_adapter(payload):

    return (
        f"speech processed: "
        f"{payload}"
    )


def runtime_adapter(payload):

    return (
        f"runtime processed: "
        f"{payload}"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" ADAPTER MANAGER STAGE 9000")
    print("================================\n")

    register_adapter(
        "speech",
        speech_adapter,
    )

    register_adapter(
        "runtime",
        runtime_adapter,
    )

    print(
        dispatch(
            "speech",
            {
                "text": "hello"
            },
        )
    )

    print(
        dispatch(
            "runtime",
            {
                "mode": "online"
            },
        )
    )

    process()

    print(status())

    recover()

    print(status())

    print("\n[ADAPTER MANAGER COMPLETE]")
