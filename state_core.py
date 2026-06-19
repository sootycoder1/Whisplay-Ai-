# ============================================================
# WHISPLAY STATE CORE
# STAGE 3600
# ============================================================
#
# Central runtime state layer
#
# Owns:
# - runtime state
# - mode tracking
# - system flags
# - state transitions
# - energy/mood values
# - runtime timing
# - temporary context
# - safety state
# - recovery state
# - lightweight runtime memory
#
# Does NOT:
# - generate responses
# - run shell/network
# - speak audio
# - control GPIO
# - make strategy decisions
# - store permanent memory
# ============================================================

import time


# ============================================================
# ENGINE
# ============================================================

STAGE = 3600
ENGINE_NAME = "WHISPLAY_STATE_CORE"
ENGINE_VERSION = "3600.1-RUNTIME"

DEBUG = True


# ============================================================
# RUNTIME STATE
# ============================================================

STATE = {
    "mode": "idle",
    "mood": "steady",
    "energy": 1.0,
    "stability": 1.0,
    "risk": 0.05,
    "ambiguity": 0.0,
    "pressure": 0.0,
    "recovery": False,
    "blocked": False,
    "busy": False,
    "listening": False,
    "thinking": False,
    "speaking": False,
    "last_input": "",
    "last_output": "",
    "last_intent": "",
    "last_event": "boot",
    "active_task": None,
    "runtime_cycles": 0,
    "boot_time": time.time(),
    "last_update": time.time(),
}


# ============================================================
# HISTORY
# ============================================================

STATE_HISTORY = []
MAX_HISTORY = 60


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def clamp(value, low, high):
    return max(low, min(high, value))


def remember(event, details=None):
    STATE_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(STATE_HISTORY) > MAX_HISTORY:
        STATE_HISTORY.pop(0)


# ============================================================
# STATE ACCESS
# ============================================================

def get(key=None, default=None):
    if key is None:
        return dict(STATE)

    return STATE.get(key, default)


def set(key, value=None):
    """
    Compatibility set.

    state.set("listening") sets mode.
    state.set("mood", "steady") sets a field.
    """
    if value is None:
        STATE["mode"] = str(key)
        STATE["last_event"] = f"mode:{key}"
        result = STATE["mode"]
    else:
        STATE[key] = value
        STATE["last_event"] = f"set:{key}"
        result = value

    STATE["last_update"] = now()
    normalize()

    return result


def update(data=None, **kwargs):
    data = data or {}

    STATE.update(data)
    STATE.update(kwargs)

    STATE["last_update"] = now()
    STATE["runtime_cycles"] += 1

    normalize()

    return dict(STATE)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize():
    STATE["energy"] = clamp(
        float(STATE.get("energy", 1.0)),
        0.0,
        2.0,
    )

    STATE["risk"] = clamp(
        float(STATE.get("risk", 0.05)),
        0.0,
        1.0,
    )

    STATE["ambiguity"] = clamp(
        float(STATE.get("ambiguity", 0.0)),
        0.0,
        1.0,
    )

    STATE["pressure"] = clamp(
        float(STATE.get("pressure", 0.0)),
        0.0,
        1.0,
    )

    STATE["stability"] = clamp(
        float(STATE.get("stability", 1.0)),
        0.0,
        1.0,
    )


# ============================================================
# MODE CONTROL
# ============================================================

def set_mode(mode):
    STATE["mode"] = str(mode)
    STATE["last_event"] = f"mode:{mode}"
    STATE["last_update"] = now()

    remember("mode_change", {
        "mode": mode,
    })

    return STATE["mode"]


# ============================================================
# INPUT EVENTS
# ============================================================

def on_input(text, intent=None):
    text = str(text or "").strip()

    STATE["last_input"] = text
    STATE["last_intent"] = intent or ""

    STATE["listening"] = False
    STATE["thinking"] = True
    STATE["busy"] = True

    STATE["last_event"] = "input"
    STATE["last_update"] = now()

    remember("input", {
        "text": text[:120],
        "intent": intent,
    })

    return dict(STATE)


# ============================================================
# OUTPUT EVENTS
# ============================================================

def on_output(text):
    text = str(text or "").strip()

    STATE["last_output"] = text

    STATE["thinking"] = False
    STATE["speaking"] = True
    STATE["busy"] = True

    STATE["last_event"] = "output"
    STATE["last_update"] = now()

    remember("output", {
        "text": text[:120],
    })

    return dict(STATE)


# ============================================================
# IDLE STATE
# ============================================================

def set_idle():
    STATE["busy"] = False
    STATE["thinking"] = False
    STATE["speaking"] = False
    STATE["listening"] = False

    STATE["mode"] = "idle"
    STATE["last_event"] = "idle"
    STATE["last_update"] = now()

    remember("idle")

    return dict(STATE)


# ============================================================
# LISTENING STATE
# ============================================================

def set_listening():
    STATE["busy"] = True
    STATE["listening"] = True
    STATE["thinking"] = False
    STATE["speaking"] = False

    STATE["mode"] = "listening"
    STATE["last_event"] = "listening"
    STATE["last_update"] = now()

    remember("listening")

    return dict(STATE)


# ============================================================
# RECOVERY
# ============================================================

def trigger_recovery(reason="unknown"):
    STATE["recovery"] = True
    STATE["stability"] *= 0.8
    STATE["pressure"] += 0.15

    normalize()

    STATE["last_event"] = "recovery"
    STATE["last_update"] = now()

    remember("recovery", {
        "reason": reason,
    })

    return dict(STATE)


def clear_recovery():
    STATE["recovery"] = False

    STATE["last_event"] = "recovery_clear"
    STATE["last_update"] = now()

    remember("recovery_clear")

    return dict(STATE)


# ============================================================
# PRESSURE
# ============================================================

def adjust_pressure(amount):
    STATE["pressure"] += amount

    normalize()

    STATE["last_update"] = now()

    return STATE["pressure"]


# ============================================================
# ENERGY
# ============================================================

def adjust_energy(amount):
    STATE["energy"] += amount

    normalize()

    STATE["last_update"] = now()

    return STATE["energy"]


# ============================================================
# STATUS
# ============================================================

def status():
    uptime = round(now() - STATE["boot_time"], 2)

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "uptime": uptime,
        "state": dict(STATE),
        "recent_history": STATE_HISTORY[-8:],
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def state():
    return status()


def runtime_state():
    return dict(STATE)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("\n================================")
    print(" WHISPLAY STATE CORE STAGE3600")
    print("================================\n")

    set_listening()
    on_input("assistant open runtime logs", intent="debug")
    on_output("Opening runtime logs.")

    print(status())

# ============================================================
# STAGE 200 STATE VISIBILITY PATCH
# Added after STAGE200_CONTRACT_AND_BUS_GUARDED_OK
# State remains runtime truth only.
# No reasoning, orchestration, hardware control, GPIO, or SPI control.
# ============================================================

_ORIGINAL_STAGE3600_STATUS = status

STAGE200_STATE_SAFE_POINT = "STAGE200_CONTRACT_AND_BUS_GUARDED_OK"

STAGE200_STATE_VIEW = {
    "safe_point": STAGE200_STATE_SAFE_POINT,
    "state_role": "runtime_truth_only",
    "autonomy": "readonly_observer",
    "controller": "orchestration_only",
    "brain": "reasoning_only",
    "display": "rendering_only",
    "audio": "listen_speak_only",
    "gpio": "blocked_global_control",
    "spi": "display_only",
    "state_can_reason": False,
    "state_can_orchestrate": False,
    "state_can_control_hardware": False,
}

def stage200_state_status():
    return dict(STAGE200_STATE_VIEW)

def state_can_control_hardware():
    return False

def state_can_reason():
    return False

def state_can_orchestrate():
    return False

def status():
    base = _ORIGINAL_STAGE3600_STATUS()

    base["stage200"] = stage200_state_status()
    base["architecture_role"] = "runtime_truth_only"

    return base

