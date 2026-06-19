# WHISPLAY DISPLAY ORCHESTRATOR — STAGE 9500*
# ============================================================

import time
import threading
import traceback

from cognitive_core import process


# ============================================================
# SAFE CONTRACT IMPORT
# ============================================================

try:

    from runtime.runtime_contract_STAGE6000 import (

        RuntimeState,
        WorkerState,
        Event,
        EventPriority,

        LIMITS,
        TELEMETRY,

        runtime_log,
        runtime_warning,
        runtime_error,
    )

except Exception:

    LIMITS = {}

    TELEMETRY = {}

    class RuntimeState:

        IDLE = "idle"

        LISTENING = "listening"

        THINKING = "thinking"

        SPEAKING = "speaking"

        ERROR = "error"

        PROCESSING = "processing"


    class WorkerState:

        OFFLINE = "offline"

        ONLINE = "online"

        BUSY = "busy"

        FAILED = "failed"

        DEGRADED = "degraded"


    class Event:

        DISPLAY_UPDATE = "display.update"

        DISPLAY_CLEAR = "display.clear"

        DISPLAY_ERROR = "display.error"

        DISPLAY_STATUS = "display.status"

        SPEECH_HEARD = "speech.heard"

        SPEECH_START = "speech.start"

        SPEECH_STOP = "speech.stop"

        CONTEXT_UPDATE = "context.update"

        SYSTEM_READY = "system.ready"

        SYSTEM_ERROR = "system.error"


    class EventPriority:

        HIGH = type("", (), {"value": 1})()

        NORMAL = type("", (), {"value": 2})()

        LOW = type("", (), {"value": 3})()


    def runtime_log(msg):

        print(f"[RUNTIME] {msg}")


    def runtime_warning(msg):

        print(f"[RUNTIME WARNING] {msg}")


    def runtime_error(msg):

        print(f"[RUNTIME ERROR] {msg}")


# ============================================================
# SAFE BUS IMPORT
# ============================================================

try:

    from runtime import runtime_bus_STAGE7000 as runtime_bus

except Exception as e:

    runtime_bus = None

    print(
        "[DISPLAY9500] runtime bus unavailable:",
        e
    )


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "display_orchestrator"

ENGINE_STAGE = 9500

ENGINE_VERSION = "9.5.1-BUILD*"


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {

    "status": "offline",

    "runtime_state": "idle",

    "worker_state": "offline",

    "mode": "adaptive",

    "running": False,

    "active_screen": "idle",

    "brightness": 90,

    "display_pressure": 0.0,

    "render_count": 0,

    "render_failures": 0,

    "frame_skips": 0,

    "duplicate_skips": 0,

    "ui_updates": 0,

    "events_received": 0,

    "events_emitted": 0,

    "last_render": "",

    "last_state": "",

    "last_message": "",

    "last_event": None,

    "last_error": None,

    "runtime_cycles": 0,

    "last_render_time": 0.0,

    "created": time.time(),

    "updated": time.time(),
}


# ============================================================
# MEMORY
# ============================================================

MEMORY = {

    "screens": [],

    "messages": [],

    "runtime_events": [],

    "render_history": [],

    "errors": [],
}


# ============================================================
# FLAGS
# ============================================================

FLAGS = {

    "display_enabled": True,

    "adaptive_rendering": True,

    "pressure_awareness": True,

    "safe_rendering": True,

    "frame_regulation": True,

    "brightness_control": True,

    "runtime_events": True,

    "ui_memory": True,

    "dedupe_renders": True,

    "debug": True,
}


# ============================================================
# DISPLAY LIMITS
# ============================================================

DISPLAY_LIMITS = {

    "max_memory": 40,

    "max_message_length": 160,

    "min_render_interval": 0.08,

    "pressure_skip_threshold": 0.90,
}


# ============================================================
# LOCK
# ============================================================

display_lock = threading.RLock()


# ============================================================
# HELPERS
# ============================================================

def now():

    return time.time()


def log(msg):

    if FLAGS["debug"]:

        print(
            f"[DISPLAY9500] {msg}"
        )


def normalize(value):

    if hasattr(value, "value"):

        return value.value

    return value


def clamp(
    value,
    minimum=0.0,
    maximum=1.0,
):

    return max(
        minimum,
        min(maximum, value)
    )


def clean(text):

    text = " ".join(
        str(text or "").strip().split()
    )

    return text[
        :DISPLAY_LIMITS[
            "max_message_length"
        ]
    ]


def remember(
    category,
    value,
    limit=None,
):

    if category not in MEMORY:
        return

    if limit is None:

        limit = DISPLAY_LIMITS[
            "max_memory"
        ]

    MEMORY[category].append(value)

    MEMORY[category] = (
        MEMORY[category][-limit:]
    )


def mark_error(
    area,
    exc,
):

    STATE["render_failures"] += 1

    STATE["last_error"] = (
        f"{area}: {exc}"
    )

    remember(
        "errors",
        STATE["last_error"],
    )

    runtime_error(
        f"{area}: {exc}"
    )


# ============================================================
# PRESSURE REGULATION
# ============================================================

def regulate_pressure():

    try:

        bus_pressure = TELEMETRY.get(
            "pressure",
            0.0
        )

    except Exception:

        bus_pressure = 0.0

    pressure = 0.0

    pressure += (
        STATE["render_failures"] * 0.08
    )

    pressure += (
        STATE["frame_skips"] * 0.04
    )

    pressure += (
        STATE["duplicate_skips"] * 0.01
    )

    pressure += (
        float(bus_pressure) * 0.25
    )

    STATE["display_pressure"] = clamp(
        pressure
    )

    return STATE["display_pressure"]
