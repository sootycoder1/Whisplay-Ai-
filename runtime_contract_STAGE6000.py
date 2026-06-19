# =========================================================
# RUNTIME CONTRACT
# STAGE 6000
# Shared runtime structures + system definitions
# =========================================================

import time


# =========================================================
# ENGINE IDENTITY
# =========================================================

ENGINE_NAME = "runtime_contract"

ENGINE_STAGE = 6000

ENGINE_VERSION = "6.0.0"


# =========================================================
# RUNTIME STATES
# =========================================================

class RuntimeState:

    BOOTING = "booting"

    IDLE = "idle"

    LISTENING = "listening"

    THINKING = "thinking"

    SPEAKING = "speaking"

    ACTIVE = "active"

    RECOVERING = "recovering"

    ERROR = "error"

    SHUTDOWN = "shutdown"


# =========================================================
# WORKER STATES
# =========================================================

class WorkerState:

    OFFLINE = "offline"

    STARTING = "starting"

    ONLINE = "online"

    BUSY = "busy"

    FAILED = "failed"

    STOPPED = "stopped"


# =========================================================
# EVENT TYPES
# =========================================================

class Event:

    SYSTEM_BOOT = "system.boot"

    SYSTEM_READY = "system.ready"

    SYSTEM_ERROR = "system.error"

    SYSTEM_WARNING = "system.warning"

    SYSTEM_HEARTBEAT = "system.heartbeat"

    SYSTEM_SHUTDOWN = "system.shutdown"

    RUNTIME_PRESSURE = "runtime.pressure"

    MEMORY_UPDATE = "memory.update"

    GOAL_UPDATE = "goal.update"

    REASONING_UPDATE = "reasoning.update"

    DISPLAY_UPDATE = "display.update"

    SPEECH_START = "speech.start"

    SPEECH_STOP = "speech.stop"
    
    SPEECH_HEARD = "speech.heard"

    SPEECH_OUTPUT = "speech.output"

# =========================================================
# EVENT PRIORITY
# =========================================================

class EventPriority:

    CRITICAL = type(
        "",
        (),
        {"value": 0}
    )()

    HIGH = type(
        "",
        (),
        {"value": 1}
    )()

    NORMAL = type(
        "",
        (),
        {"value": 2}
    )()

    LOW = type(
        "",
        (),
        {"value": 3}
    )()


# =========================================================
# SUBSYSTEM REGISTRY
# =========================================================

SUBSYSTEMS = {

    "runtime_contract": {
        "stage": 6000,
        "status": "online",
    },

    "context_manager": {
        "stage": 6500,
        "status": "online",
    },

    "runtime_bus": {
        "stage": 7000,
        "status": "online",
    },

    "memory_engine": {
        "stage": 7500,
        "status": "online",
    },

    "goal_engine": {
        "stage": 8000,
        "status": "online",
    },

    "reasoning_engine": {
        "stage": 8500,
        "status": "online",
    },

    "adapter_manager": {
        "stage": 9000,
        "status": "online",
    },

    "display_orchestrator": {
        "stage": 9500,
        "status": "online",
    },

    "system_controller": {
        "stage": 10000,
        "status": "online",
    },

    "persistent_speech_worker": {
        "stage": 10500,
        "status": "online",
    },

    "analysis_core": {
        "stage": 11500,
        "status": "online",
    },
}


# =========================================================
# TELEMETRY
# =========================================================

TELEMETRY = {

    "runtime_cycles": 0,

    "events_processed": 0,

    "events_dropped": 0,

    "runtime_errors": 0,

    "pressure": 0.0,

    "last_event": None,

    "last_error": None,

    "created": time.time(),

    "updated": time.time(),
}


# =========================================================
# HEALTH LIMITS
# =========================================================

HEALTH_LIMITS = {

    "max_pressure": 0.90,

    "max_runtime_errors": 25,

    "max_queue_size": 100,

    "max_event_backlog": 250,
}


# =========================================================
# HELPERS
# =========================================================

def now():

    return time.time()


def runtime_log(message):

    print(
        f"[RUNTIME] {message}"
    )


def runtime_warning(message):

    print(
        f"[RUNTIME WARNING] {message}"
    )


def runtime_error(message):

    TELEMETRY["runtime_errors"] += 1

    TELEMETRY["last_error"] = str(
        message
    )

    print(
        f"[RUNTIME ERROR] {message}"
    )


# =========================================================
# SAFE RESULT
# =========================================================

def safe_result(
    ok=True,
    message="",
    data=None,
):

    return {

        "ok": ok,

        "message": message,

        "data": data or {},

        "timestamp": now(),
    }


# =========================================================
# SNAPSHOT
# =========================================================

def snapshot():

    return {

        "engine": ENGINE_NAME,

        "stage": ENGINE_STAGE,

        "version": ENGINE_VERSION,

        "subsystems": dict(
            SUBSYSTEMS
        ),

        "telemetry": dict(
            TELEMETRY
        ),

        "health_limits": dict(
            HEALTH_LIMITS
        ),
    }


# =========================================================
# STATUS
# =========================================================

def status():

    return (

        "\n"

        "====================================\n"

        " RUNTIME CONTRACT STAGE 6000\n"

        "====================================\n"

        f"SUBSYSTEMS:    "
        f"{len(SUBSYSTEMS)}\n"

        f"RUNTIME:       "
        f"{TELEMETRY['runtime_cycles']}\n"

        f"ERRORS:        "
        f"{TELEMETRY['runtime_errors']}\n"

        f"PRESSURE:      "
        f"{TELEMETRY['pressure']:.2f}\n"

        "====================================\n"
    )


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print(
        "\n================================"
    )

    print(
        " RUNTIME CONTRACT STAGE 6000"
    )

    print(
        "================================\n"
    )

    runtime_log(
        "contract online"
    )

    print(status())

    print(snapshot())

# =========================================================
# STAGE 200 LAW BRIDGE
# Added after STAGE200_STATUS_VISIBLE_READONLY_OK
# Passive/read-only definitions only.
# =========================================================

STAGE200_SAFE_POINT = "STAGE200_STATUS_VISIBLE_READONLY_OK"
FINAL_AUTHORITY = "user"

STAGE200_CONTRACT_LAW = {
    "safe_point": STAGE200_SAFE_POINT,
    "final_authority": FINAL_AUTHORITY,
    "controller": "orchestration_only",
    "brain": "reasoning_only",
    "state": "runtime_truth_only",
    "display": "rendering_only",
    "audio": "listen_speak_only",
    "autonomy": "observe_suggest_only_readonly",
    "gpio_edge_interrupt": "blocked",
    "gpio_global_control": False,
    "spi_global_control": False,
    "spi_scope": "display_only",
    "hardware_authority": "explicit_controller_governed_only",
    "import_side_effects_allowed": False,
}

def stage200_law():
    return dict(STAGE200_CONTRACT_LAW)

def autonomy_is_readonly():
    return True

def autonomy_can_control_hardware():
    return False

def gpio_global_control_allowed():
    return False

def spi_global_control_allowed():
    return False

def validate_stage200_action(layer, action):
    layer = str(layer).lower().strip()
    action = str(action).lower().strip()

    blocked = {
        ("autonomy", "control_hardware"),
        ("autonomy", "replace_brain"),
        ("autonomy", "replace_controller"),
        ("brain", "control_hardware"),
        ("brain", "orchestrate"),
        ("state", "reason"),
        ("state", "control_hardware"),
        ("display", "reason"),
        ("display", "control_hardware"),
        ("audio", "reason"),
        ("audio", "control_hardware"),
        ("gpio", "global_control"),
        ("spi", "global_control"),
    }

    allowed = (layer, action) not in blocked

    return {
        "ok": allowed,
        "allowed": allowed,
        "layer": layer,
        "action": action,
        "reason": "not_blocked_by_stage200_contract" if allowed else "blocked_by_stage200_contract",
        "safe_point": STAGE200_SAFE_POINT,
    }

def stage200_contract_status():
    return {
        "ok": True,
        "safe_point": STAGE200_SAFE_POINT,
        "final_authority": FINAL_AUTHORITY,
        "autonomy_readonly": autonomy_is_readonly(),
        "autonomy_controls_hardware": autonomy_can_control_hardware(),
        "gpio_global_control": gpio_global_control_allowed(),
        "spi_global_control": spi_global_control_allowed(),
        "spi_scope": "display_only",
    }

