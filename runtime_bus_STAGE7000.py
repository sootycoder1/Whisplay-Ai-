# ============================================================
# RUNTIME BUS
# STAGE 7000
# Unified runtime communication + event spine
# ============================================================

import time
import queue
import threading


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "runtime_bus"

ENGINE_STAGE = 7000


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "adaptive",
    "status": "online",
    "events_processed": 0,
    "events_dropped": 0,
    "listeners": 0,
    "pressure": 0.0,
    "last_event": None,
    "last_source": None,
    "last_target": None,
    "runtime_cycles": 0,
    "created": time.time(),
    "updated": time.time(),
}


# ============================================================
# BUS MEMORY
# ============================================================

MEMORY = {
    "events": [],
    "errors": [],
    "routes": [],
    "sources": [],
}


# ============================================================
# FLAGS
# ============================================================

FLAGS = {
    "bus_enabled": True,
    "event_memory": True,
    "adaptive_pressure": True,
    "listener_tracking": True,
    "safe_dispatch": True,
    "runtime_monitoring": True,
}


# ============================================================
# BUS OBJECTS
# ============================================================

runtime_queue = queue.Queue()

listeners = {}

bus_lock = threading.Lock()

worker_running = False

worker_thread = None


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
# MEMORY
# ============================================================

def remember(
    category,
    value,
    limit=50,
):

    if category not in MEMORY:
        return

    MEMORY[category].append(value)

    MEMORY[category] = (
        MEMORY[category][-limit:]
    )


# ============================================================
# PRESSURE
# ============================================================

def update_pressure():

    size = runtime_queue.qsize()

    pressure = (
        size / 25.0
    )

    STATE["pressure"] = clamp(
        pressure
    )

    return STATE["pressure"]


# ============================================================
# LISTENER REGISTRATION
# ============================================================

def register(
    event_name,
    callback,
):

    with bus_lock:

        if event_name not in listeners:
            listeners[event_name] = []

        listeners[event_name].append(
            callback
        )

        STATE["listeners"] = sum(
            len(v)
            for v in listeners.values()
        )

        STATE["updated"] = now()

        print(
            f"[BUS] registered "
            f"{event_name}"
        )


# ============================================================
# EVENT CREATION
# ============================================================

def emit(
    event_name,
    payload=None,
    source="unknown",
    target="broadcast",
):

    event = {
        "event": event_name,
        "payload": payload,
        "source": source,
        "target": target,
        "timestamp": now(),
    }

    runtime_queue.put(event)

    remember(
        "events",
        event_name,
    )

    remember(
        "sources",
        source,
    )

    STATE["updated"] = now()

    update_pressure()

    return event


# ============================================================
# DISPATCH
# ============================================================

def dispatch(event):

    event_name = event.get(
        "event"
    )

    callbacks = listeners.get(
        event_name,
        []
    )

    if not callbacks:

        STATE["events_dropped"] += 1

        return

    for callback in callbacks:

        try:

            callback(event)

        except Exception as e:

            remember(
                "errors",
                str(e),
            )

            print(
                f"[BUS ERROR] {e}"
            )

    STATE["events_processed"] += 1

    STATE["last_event"] = event_name

    STATE["last_source"] = event.get(
        "source"
    )

    STATE["last_target"] = event.get(
        "target"
    )

    STATE["updated"] = now()


# ============================================================
# WORKER
# ============================================================

def _worker():

    global worker_running

    print("[BUS] worker online")

    while worker_running:

        try:

            event = runtime_queue.get(
                timeout=0.25
            )

        except queue.Empty:

            continue

        try:

            dispatch(event)

        except Exception as e:

            remember(
                "errors",
                str(e),
            )

        finally:

            runtime_queue.task_done()

            update_pressure()

            STATE["runtime_cycles"] += 1

    print("[BUS] worker stopped")


# ============================================================
# START
# ============================================================

def start():

    global worker_running
    global worker_thread

    if worker_running:
        return

    worker_running = True

    worker_thread = threading.Thread(
        target=_worker,
        daemon=True,
    )

    worker_thread.start()

    print("[BUS] started")


# ============================================================
# STOP
# ============================================================

def stop():

    global worker_running

    worker_running = False

    print("[BUS] stopping")


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "memory": dict(MEMORY),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return (
        "\n"
        "==============================\n"
        " RUNTIME BUS STAGE 7000\n"
        "==============================\n"
        f"STATUS:       {STATE['status']}\n"
        f"PRESSURE:     {STATE['pressure']:.2f}\n"
        f"LISTENERS:    {STATE['listeners']}\n"
        f"PROCESSED:    {STATE['events_processed']}\n"
        f"DROPPED:      {STATE['events_dropped']}\n"
        f"LAST EVENT:   {STATE['last_event']}\n"
        f"LAST SOURCE:  {STATE['last_source']}\n"
        f"CYCLES:       {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


# ============================================================
# TEST CALLBACK
# ============================================================

def test_listener(event):

    print(
        f"\n[EVENT RECEIVED] "
        f"{event}"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" RUNTIME BUS STAGE 7000")
    print("================================\n")

    register(
        "speech",
        test_listener,
    )

    register(
        "runtime",
        test_listener,
    )

    start()

    emit(
        "speech",
        payload={
            "text": "hello"
        },
        source="speech_core",
    )

    emit(
        "runtime",
        payload={
            "state": "online"
        },
        source="runtime_core",
    )

    time.sleep(2)

    print(status())

    stop()

    print("\n[RUNTIME BUS COMPLETE]")

# ============================================================
# STAGE 200 BUS GUARD - SMALL SAFE PATCH
# ============================================================

_ORIGINAL_STAGE7000_EMIT = emit

STAGE200_BUS_SAFE_POINT = "STAGE200_STATUS_VISIBLE_READONLY_OK"

def stage200_bus_status():
    return {
        "ok": True,
        "safe_point": STAGE200_BUS_SAFE_POINT,
        "bus_role": "transport_only",
        "autonomy": "observe_suggest_only",
        "hardware_control": "blocked",
    }

def stage200_bus_allows_event(event_name, payload=None, source="unknown", target="broadcast"):

    # Allow core system speech events
    if str(event_name).startswith("speech."):
        return {"allowed": True, "reason": "core_speech_event_allowed"}

    text = f"{event_name} {payload} {source} {target}".lower()

    safe_words = ("status", "observe", "observation", "suggest", "suggestion", "readonly", "read_only")
    blocked_words = ("gpio", "spi", "hardware", "interrupt", "edge", "execute", "actuate", "control_hardware", "replace_brain", "replace_controller")

    if "autonomy" in text:
        if "autonomy.observation" in text or "autonomy.suggestion" in text or "autonomy.status" in text:
            return {"allowed": True, "reason": "autonomy_readonly_event_allowed"}

        for word in blocked_words:
            if word in text:
                return {"allowed": False, "reason": "autonomy_action_blocked_by_stage200_bus_guard", "matched": word}

    for word in blocked_words:
        if word in text and not any(safe in text for safe in safe_words):
            return {"allowed": False, "reason": "hardware_control_event_blocked_by_stage200_bus_guard", "matched": word}

    return {"allowed": True, "reason": "event_allowed_by_stage200_bus_guard"}

def emit(event_name, payload=None, source="unknown", target="broadcast"):
    guard = stage200_bus_allows_event(event_name, payload, source, target)

    if not guard.get("allowed"):
        STATE["events_dropped"] += 1
        STATE["last_event"] = event_name
        STATE["last_source"] = source
        STATE["last_target"] = target
        STATE["updated"] = now()
        remember("errors", {"event": event_name, "guard": guard})
        print(f"[BUS GUARD] blocked {event_name}: {guard.get('reason')}")

        return {
            "event": event_name,
            "payload": payload,
            "source": source,
            "target": target,
            "timestamp": now(),
            "blocked": True,
            "guard": guard,
        }

    return _ORIGINAL_STAGE7000_EMIT(event_name, payload=payload, source=source, target=target)

