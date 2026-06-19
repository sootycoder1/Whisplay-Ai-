# ============================================================
# WHISPLAY DISPLAY ORCHESTRATOR — STAGE 9550 RECOVERED
# Runtime-safe bridge between cognition/controller and Stage 4300 UI
# ============================================================

import time
import traceback
import threading


ENGINE_NAME = "display_orchestrator"
ENGINE_STAGE = 9550
ENGINE_VERSION = "9.5.5-RECOVERED"


STATE = {
    "status": "offline",
    "screen": "idle",
    "brightness": 90,
    "render_count": 0,
    "render_failures": 0,
    "last_user": "",
    "last_assistant": "",
    "last_state": "idle",
    "last_error": None,
    "created": time.time(),
    "updated": time.time(),
}


LOCK = threading.RLock()
UI = None


def status():
    return dict(STATE)


def snapshot():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "state": dict(STATE),
        "ui_loaded": UI is not None,
    }


def _mark_error(area, exc):
    STATE["status"] = "error"
    STATE["render_failures"] += 1
    STATE["last_error"] = f"{area}: {exc}"
    STATE["updated"] = time.time()
    print("[DISPLAY9550 ERROR]", STATE["last_error"])


print("[DISPLAY9550] module loaded")


def load_ui():
    global UI

    with LOCK:
        if UI is not None:
            STATE["status"] = "online"
            STATE["updated"] = time.time()
            return UI

        try:
            from display_ui_STAGE4300_RUNTIME_SAFE import WhisplayUI

            UI = WhisplayUI()
            STATE["status"] = "online"
            STATE["updated"] = time.time()

            print("[DISPLAY9550] Stage 4300 UI loaded")
            return UI

        except Exception as exc:
            _mark_error("load_ui", exc)
            traceback.print_exc()
            return None

def render(user=None, assistant=None, state="idle"): 
    with LOCK:
        try:
            ui = load_ui()

            if ui is None:
                return False

            ui.show_message(
                user=user,
                assistant=assistant,
                state=state,
            )


            STATE["status"] = "online"
            STATE["screen"] = str(state or STATE["screen"])
            STATE["last_user"] = str(user or "")
            STATE["last_assistant"] = str(assistant or "")
            STATE["last_state"] = str(state or "")
            STATE["render_count"] += 1
            STATE["updated"] = time.time()

            return True

        except Exception as exc:
            _mark_error("render", exc)
            traceback.print_exc()
            return False

def show_idle(message="Idle"):
    return render(assistant=message, state="idle")


def show_listening(message="Listening"):
    return render(assistant=message, state="listening")


def show_thinking(message="Thinking"):
    return render(assistant=message, state="thinking")


def show_speaking(message="Speaking"):
    return render(assistant=message, state="speaking")


def show_error(message="Error"):
    return render(assistant=message, state="error")

