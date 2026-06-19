# ============================================================
# BRAIN ADAPTER — STAGE 3600
# Runtime brain bridge + intelligence adapter layer
# ============================================================

import time
import traceback


STAGE = 3600

ENGINE_NAME = "BRAIN_ADAPTER"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# BRAIN STATE
# ============================================================

BRAIN_STATE = {
    "enabled": True,
    "safe_mode": False,
    "fallback_mode": False,
    "last_input": "",
    "last_output": "",
    "last_intent": "",
    "last_error": "",
    "calls": 0,
    "failures": 0,
    "last_call_time": 0.0,
}


# ============================================================
# BRAIN HANDLERS
# ============================================================

HANDLERS = {
    "router": None,
    "generator": None,
    "memory": None,
    "personality": None,
    "fallback": None,
}


# ============================================================
# HISTORY
# ============================================================

BRAIN_HISTORY = []

MAX_HISTORY = 200


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):
    if DEBUG:
        print(f"[BRAIN_ADAPTER] {message}")


def remember(event, details=None):
    BRAIN_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(BRAIN_HISTORY) > MAX_HISTORY:
        BRAIN_HISTORY.pop(0)


def clean(text):
    return " ".join(str(text or "").strip().split())


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_handler(name, handler):
    if name not in HANDLERS:
        return False

    HANDLERS[name] = handler

    remember("handler_registered", {
        "name": name,
    })

    log(f"handler registered: {name}")

    return True


def remove_handler(name):
    if name not in HANDLERS:
        return False

    HANDLERS[name] = None

    remember("handler_removed", {
        "name": name,
    })

    return True


# ============================================================
# SAFE / FALLBACK MODE
# ============================================================

def enable_safe_mode():
    BRAIN_STATE["safe_mode"] = True
    remember("safe_mode_enabled")
    log("safe mode enabled")
    return True


def disable_safe_mode():
    BRAIN_STATE["safe_mode"] = False
    remember("safe_mode_disabled")
    return True


def enable_fallback_mode():
    BRAIN_STATE["fallback_mode"] = True
    remember("fallback_mode_enabled")
    log("fallback mode enabled")
    return True


def disable_fallback_mode():
    BRAIN_STATE["fallback_mode"] = False
    remember("fallback_mode_disabled")
    return True


# ============================================================
# INTENT GUESS
# ============================================================

def guess_intent(text):
    t = clean(text).lower()

    if not t:
        return "empty"

    if any(w in t for w in [
        "error",
        "traceback",
        "debug",
        "broken",
        "crash",
        "failed",
    ]):
        return "debug"

    if any(w in t for w in [
        "build",
        "file",
        "code",
        "render",
        "create",
        "make",
    ]):
        return "build"

    if any(w in t for w in [
        "status",
        "health",
        "runtime",
        "state",
        "system",
    ]):
        return "system"

    if any(w in t for w in [
        "remember",
        "memory",
        "recall",
        "checkpoint",
    ]):
        return "memory"

    if any(w in t for w in [
        "hi",
        "hello",
        "hey",
        "mate",
        "thanks",
        "cheers",
    ]):
        return "conversation"

    return "general"


# ============================================================
# FALLBACK RESPONSE
# ============================================================

def fallback_response(text, intent="general"):
    if intent == "empty":
        return "I did not catch that."

    if intent == "debug":
        return "I can see a debug issue. Send the error and I will mark the fault."

    if intent == "build":
        return "I can build that as a clean runtime file."

    if intent == "system":
        return "Runtime is listening. Send the system area you want checked."

    if intent == "memory":
        return "Memory/checkpoint request detected."

    return "I am here."


# ============================================================
# CALL HANDLER SAFE
# ============================================================

def call_handler(name, *args, **kwargs):
    handler = HANDLERS.get(name)

    if not callable(handler):
        return {
            "ok": False,
            "error": "missing_handler",
            "handler": name,
        }

    try:
        result = handler(*args, **kwargs)

        return {
            "ok": True,
            "handler": name,
            "result": result,
        }

    except Exception as e:
        BRAIN_STATE["failures"] += 1
        BRAIN_STATE["last_error"] = str(e)

        remember("handler_failure", {
            "handler": name,
            "error": str(e),
        })

        if DEBUG:
            print(traceback.format_exc())

        return {
            "ok": False,
            "handler": name,
            "error": str(e),
        }


# ============================================================
# RESPONSE PIPELINE
# ============================================================

def process(text, runtime_state=None, strategy=None):
    runtime_state = runtime_state or {}
    strategy = strategy or {}

    text = clean(text)

    if not BRAIN_STATE["enabled"]:
        return {
            "ok": False,
            "engine": ENGINE_NAME,
            "error": "brain_disabled",
            "response": "",
        }

    BRAIN_STATE["calls"] += 1
    BRAIN_STATE["last_input"] = text
    BRAIN_STATE["last_call_time"] = now()

    intent = runtime_state.get("intent") or guess_intent(text)

    BRAIN_STATE["last_intent"] = intent

    remember("input", {
        "text": text[:120],
        "intent": intent,
    })

    # --------------------------------------------------------
    # SAFE MODE SHORT PATH
    # --------------------------------------------------------

    if BRAIN_STATE["safe_mode"] or runtime_state.get("safe_mode"):
        response = fallback_response(text, intent)

        BRAIN_STATE["last_output"] = response

        return {
            "ok": True,
            "engine": ENGINE_NAME,
            "stage": STAGE,
            "intent": intent,
            "mode": "safe",
            "response": response,
        }

    # --------------------------------------------------------
    # ROUTER HANDLER
    # --------------------------------------------------------

    route_result = None

    if HANDLERS["router"]:
        route_result = call_handler(
            "router",
            text,
            runtime_state,
        )

    # --------------------------------------------------------
    # GENERATOR HANDLER
    # --------------------------------------------------------

    response = ""

    if HANDLERS["generator"]:
        generated = call_handler(
            "generator",
            text,
            runtime_state,
            strategy,
        )

        if generated["ok"]:
            response = str(generated["result"])

    # --------------------------------------------------------
    # FALLBACK HANDLER
    # --------------------------------------------------------

    if not response and HANDLERS["fallback"]:
        fallback = call_handler(
            "fallback",
            text,
            intent,
        )

        if fallback["ok"]:
            response = str(fallback["result"])

    # --------------------------------------------------------
    # INTERNAL FALLBACK
    # --------------------------------------------------------

    if not response:
        response = fallback_response(text, intent)
        enable_fallback_mode()

    # --------------------------------------------------------
    # PERSONALITY HANDLER
    # --------------------------------------------------------

    if HANDLERS["personality"]:
        styled = call_handler(
            "personality",
            response,
            strategy,
        )

        if styled["ok"] and styled["result"]:
            response = str(styled["result"])

    # --------------------------------------------------------
    # MEMORY HANDLER
    # --------------------------------------------------------

    if HANDLERS["memory"]:
        call_handler(
            "memory",
            {
                "input": text,
                "output": response,
                "intent": intent,
                "time": now(),
            },
        )

    BRAIN_STATE["last_output"] = response

    remember("output", {
        "text": response[:120],
        "intent": intent,
    })

    return {
        "ok": True,
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "intent": intent,
        "route": route_result,
        "strategy": strategy,
        "response": response,
    }


# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable():
    BRAIN_STATE["enabled"] = True
    return True


def disable():
    BRAIN_STATE["enabled"] = False
    return True


# ============================================================
# STATUS
# ============================================================

def status():
    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "state": dict(BRAIN_STATE),
        "handlers": {
            name: callable(handler)
            for name, handler in HANDLERS.items()
        },
        "history_size": len(BRAIN_HISTORY),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def brain(text, runtime_state=None, strategy=None):
    return process(text, runtime_state, strategy)


def generate(text, runtime_state=None, strategy=None):
    result = process(text, runtime_state, strategy)
    return result.get("response", "")


def adapter(text, runtime_state=None, strategy=None):
    return process(text, runtime_state, strategy)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" BRAIN ADAPTER STAGE3600")
    print("================================\n")

    print(
        process(
            "assistant show runtime status",
            runtime_state={
                "pressure": 0.22,
                "stability": 0.94,
                "intent": "system",
            },
            strategy={
                "tone": "focused",
                "verbosity": 0.45,
            },
        )
    )

    print(status())
