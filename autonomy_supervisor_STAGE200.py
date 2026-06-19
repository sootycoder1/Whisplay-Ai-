# WHISPLAY AUTONOMY SUPERVISOR — STAGE 200
# Observe-only layer above Stage 150.
# It watches runtime state and suggests. It does not control hardware.

import time

ENGINE_NAME = "autonomy_supervisor_STAGE200"
ENGINE_STAGE = 200
ENGINE_VERSION = "200.0-observe-only"

ALLOW_GPIO = False
ALLOW_SPI = False
ALLOW_AUDIO_CONTROL = False
ALLOW_DISPLAY_CONTROL = False
ALLOW_REMOTE_CONTROL = False
ALLOW_BRAIN_MUTATION = False
ALLOW_CONTROLLER_REPLACE = False

STATE = {
    "online": False,
    "started_at": None,
    "last_runtime_state": "unknown",
    "last_input": "",
    "last_output": "",
    "last_error": "",
    "last_suggestion": "none",
    "events": [],
}


def _event(kind, message):
    item = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": str(kind),
        "message": str(message),
    }
    STATE["events"].append(item)
    STATE["events"] = STATE["events"][-50:]
    return item


def start():
    STATE["online"] = True
    STATE["started_at"] = time.time()
    _event("start", "Stage 200 autonomy supervisor online")
    return status()


def observe_runtime(runtime_state="unknown"):
    STATE["last_runtime_state"] = str(runtime_state)
    _event("runtime", runtime_state)
    return analyze()


def observe_input(text):
    STATE["last_input"] = str(text)
    _event("input", text)
    return analyze()


def observe_output(text):
    STATE["last_output"] = str(text)
    _event("output", text)
    return analyze()


def observe_error(error):
    STATE["last_error"] = str(error)
    _event("error", error)
    return analyze()


def analyze():
    if STATE["last_error"]:
        STATE["last_suggestion"] = "suggest_manual_review"
    else:
        STATE["last_suggestion"] = "continue"

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "online": STATE["online"],
        "runtime_state": STATE["last_runtime_state"],
        "suggestion": STATE["last_suggestion"],
        "allowed_to_act": False,
    }


def request_action(action, reason=""):
    _event("blocked_action", action)
    return {
        "requested_action": str(action),
        "reason": str(reason),
        "approved": False,
        "executed": False,
        "message": "Stage 200 is observe-only. User approval required.",
    }


def status():
    uptime = None
    if STATE["started_at"]:
        uptime = round(time.time() - STATE["started_at"], 2)

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "online": STATE["online"],
        "uptime": uptime,
        "last_runtime_state": STATE["last_runtime_state"],
        "last_suggestion": STATE["last_suggestion"],
        "locks": {
            "gpio_locked": not ALLOW_GPIO,
            "spi_locked": not ALLOW_SPI,
            "audio_control_locked": not ALLOW_AUDIO_CONTROL,
            "display_control_locked": not ALLOW_DISPLAY_CONTROL,
            "remote_control_locked": not ALLOW_REMOTE_CONTROL,
            "brain_mutation_locked": not ALLOW_BRAIN_MUTATION,
            "controller_replace_locked": not ALLOW_CONTROLLER_REPLACE,
        },
    }


def process(**kwargs):
    return observe_runtime(kwargs.get("runtime_state", "unknown"))


if __name__ == "__main__":
    print("WHISPLAY AUTONOMY SUPERVISOR — STAGE 200")
    print(start())
    print(observe_input("test input"))
    print(observe_output("stage 150 alive"))
    print(request_action("restart_controller", "test only"))
    print(status())
