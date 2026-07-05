# =========================================================
# RUNTIME CONTRACT
# STAGE 6000
# Shared runtime structures + system definitions
# =========================================================

import copy
import time


# =========================================================
# ENGINE IDENTITY
# =========================================================

ENGINE_NAME = "runtime_contract"

ENGINE_STAGE = 6000

ENGINE_VERSION = "6.1.0-rock"


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
        "stage": 12010,
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

        "data": {} if data is None else data,

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

        "subsystems": copy.deepcopy(
            SUBSYSTEMS
        ),

        "telemetry": copy.deepcopy(
            TELEMETRY
        ),

        "health_limits": copy.deepcopy(
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
    return copy.deepcopy(STAGE200_CONTRACT_LAW)

def autonomy_is_readonly():
    return True

def autonomy_can_control_hardware():
    return False

def gpio_global_control_allowed():
    return False

def spi_global_control_allowed():
    return False

STAGE200_ALLOWED_ACTIONS = {
    "autonomy": {
        "observe",
        "suggest",
        "status",
        "heartbeat",
    },
    "controller": {
        "orchestrate",
        "route_event",
        "load_subsystem",
        "shutdown",
    },
    "brain": {
        "reason",
        "respond",
    },
    "state": {
        "read",
        "update_runtime_state",
        "snapshot",
        "status",
    },
    "display": {
        "render",
        "update",
    },
    "audio": {
        "listen",
        "speak",
    },
    "bus": {
        "emit",
        "subscribe",
        "transport",
    },
    "memory": {
        "read",
        "update",
    },
    "goal": {
        "read",
        "update",
    },
    "reasoning": {
        "analyze",
    },
    "adapter": {
        "adapt",
    },
    "analysis": {
        "analyze",
    },
    "spi": {
        "display_only",
    },
    "gpio": set(),
}


def validate_stage200_action(layer, action):
    layer = str(layer).lower().strip()
    action = str(action).lower().strip()

    if not layer:
        return {
            "ok": False,
            "allowed": False,
            "layer": layer,
            "action": action,
            "reason": "missing_layer",
            "safe_point": STAGE200_SAFE_POINT,
        }

    if not action:
        return {
            "ok": False,
            "allowed": False,
            "layer": layer,
            "action": action,
            "reason": "missing_action",
            "safe_point": STAGE200_SAFE_POINT,
        }

    if layer not in STAGE200_ALLOWED_ACTIONS:
        return {
            "ok": False,
            "allowed": False,
            "layer": layer,
            "action": action,
            "reason": "unknown_layer",
            "safe_point": STAGE200_SAFE_POINT,
        }

    allowed = action in STAGE200_ALLOWED_ACTIONS[layer]

    return {
        "ok": allowed,
        "allowed": allowed,
        "layer": layer,
        "action": action,
        "reason": (
            "allowed_by_stage200_contract"
            if allowed
            else "action_not_allowed_for_layer"
        ),
        "safe_point": STAGE200_SAFE_POINT,
    }


def validate_contract():
    errors = []

    required_identity = {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
    }

    if required_identity["engine"] != "runtime_contract":
        errors.append("invalid_engine_name")

    if required_identity["stage"] != 6000:
        errors.append("invalid_engine_stage")

    if not isinstance(required_identity["version"], str):
        errors.append("invalid_engine_version")

    runtime_states = {
        RuntimeState.BOOTING,
        RuntimeState.IDLE,
        RuntimeState.LISTENING,
        RuntimeState.THINKING,
        RuntimeState.SPEAKING,
        RuntimeState.ACTIVE,
        RuntimeState.RECOVERING,
        RuntimeState.ERROR,
        RuntimeState.SHUTDOWN,
    }

    if len(runtime_states) != 9:
        errors.append("duplicate_or_missing_runtime_states")

    worker_states = {
        WorkerState.OFFLINE,
        WorkerState.STARTING,
        WorkerState.ONLINE,
        WorkerState.BUSY,
        WorkerState.FAILED,
        WorkerState.STOPPED,
    }

    if len(worker_states) != 6:
        errors.append("duplicate_or_missing_worker_states")

    priorities = {
        EventPriority.CRITICAL.value,
        EventPriority.HIGH.value,
        EventPriority.NORMAL.value,
        EventPriority.LOW.value,
    }

    if priorities != {0, 1, 2, 3}:
        errors.append("invalid_event_priorities")

    required_subsystems = {
        "runtime_contract",
        "context_manager",
        "runtime_bus",
        "memory_engine",
        "goal_engine",
        "reasoning_engine",
        "adapter_manager",
        "display_orchestrator",
        "system_controller",
        "persistent_speech_worker",
        "analysis_core",
    }

    missing_subsystems = sorted(
        required_subsystems - set(SUBSYSTEMS)
    )

    if missing_subsystems:
        errors.append(
            f"missing_subsystems:{','.join(missing_subsystems)}"
        )

    if SUBSYSTEMS.get(
        "system_controller", {}
    ).get("stage") != 12010:
        errors.append("controller_stage_not_12010")

    if FINAL_AUTHORITY != "user":
        errors.append("final_authority_not_user")

    if autonomy_is_readonly() is not True:
        errors.append("autonomy_not_readonly")

    if autonomy_can_control_hardware() is not False:
        errors.append("autonomy_hardware_control_enabled")

    if gpio_global_control_allowed() is not False:
        errors.append("gpio_global_control_enabled")

    if spi_global_control_allowed() is not False:
        errors.append("spi_global_control_enabled")

    required_denials = [
        ("autonomy", "control_hardware"),
        ("autonomy", "replace_brain"),
        ("autonomy", "replace_controller"),
        ("brain", "orchestrate"),
        ("state", "reason"),
        ("gpio", "global_control"),
        ("spi", "global_control"),
        ("unknown_layer", "anything"),
    ]

    for layer, action in required_denials:
        result = validate_stage200_action(layer, action)

        if result.get("allowed") is not False:
            errors.append(
                f"unsafe_action_allowed:{layer}:{action}"
            )

    required_allows = [
        ("autonomy", "observe"),
        ("controller", "orchestrate"),
        ("brain", "reason"),
        ("state", "snapshot"),
        ("display", "render"),
        ("audio", "listen"),
        ("bus", "transport"),
        ("spi", "display_only"),
    ]

    for layer, action in required_allows:
        result = validate_stage200_action(layer, action)

        if result.get("allowed") is not True:
            errors.append(
                f"required_action_denied:{layer}:{action}"
            )

    return {
        "ok": not errors,
        "errors": errors,
        "error_count": len(errors),
        "safe_point": STAGE200_SAFE_POINT,
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
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

# =========================================================
# TEST MODE
# Complete contract self-test
# =========================================================

if __name__ == "__main__":
    print("\n================================")
    print(" RUNTIME CONTRACT STAGE 6000")
    print(" ROCK-SOLID SELF TEST")
    print("================================\n")

    runtime_log("contract online")

    validation = validate_contract()

    print(status())
    print(snapshot())
    print(stage200_contract_status())
    print(validation)

    if not validation["ok"]:
        raise SystemExit(
            f"CONTRACT SELF-TEST FAILED: {validation['errors']}"
        )

    print("RUNTIME CONTRACT SELF-TEST PASSED")

