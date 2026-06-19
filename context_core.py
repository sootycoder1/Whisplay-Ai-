# ============================================================
# CONTEXT CORE — STAGE 3600
# Runtime context + active awareness layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "CONTEXT_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# ACTIVE CONTEXT
# ============================================================

CONTEXT = {
    "topic": "",
    "intent": "",
    "mode": "balanced",
    "focus": "",
    "conversation_state": "idle",
    "last_user_input": "",
    "last_assistant_output": "",
    "active_runtime": "runtime_core",
    "active_route": "",
    "active_signal": "",
    "active_event": "",
    "recovery": False,
    "pressure": 0.0,
    "stability": 1.0,
    "ambiguity": 0.0,
    "updated": 0.0,
}


# ============================================================
# CONTEXT MEMORY
# ============================================================

CONTEXT_HISTORY = []

MAX_HISTORY = 240


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[CONTEXT] {message}")


def remember(event, details=None):

    CONTEXT_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(CONTEXT_HISTORY) > MAX_HISTORY:
        CONTEXT_HISTORY.pop(0)


# ============================================================
# BASIC ACCESS
# ============================================================

def get(key=None, default=None):

    if key is None:
        return dict(CONTEXT)

    return CONTEXT.get(
        key,
        default,
    )


def set(key, value):

    CONTEXT[key] = value

    CONTEXT["updated"] = now()

    return value


def update(data=None, **kwargs):

    data = data or {}

    CONTEXT.update(data)
    CONTEXT.update(kwargs)

    CONTEXT["updated"] = now()

    remember("context_update", {
        "keys": list(data.keys())
    })

    return dict(CONTEXT)


# ============================================================
# TOPIC
# ============================================================

def set_topic(topic):

    CONTEXT["topic"] = str(topic)

    CONTEXT["updated"] = now()

    remember("topic", {
        "topic": topic,
    })

    return CONTEXT["topic"]


# ============================================================
# INTENT
# ============================================================

def set_intent(intent):

    CONTEXT["intent"] = str(intent)

    CONTEXT["updated"] = now()

    remember("intent", {
        "intent": intent,
    })

    return CONTEXT["intent"]


# ============================================================
# INPUT / OUTPUT
# ============================================================

def user_input(text):

    CONTEXT["last_user_input"] = str(
        text or ""
    ).strip()

    CONTEXT["conversation_state"] = "processing"

    CONTEXT["updated"] = now()

    remember("user_input", {
        "text": text[:120],
    })

    return CONTEXT["last_user_input"]


def assistant_output(text):

    CONTEXT["last_assistant_output"] = str(
        text or ""
    ).strip()

    CONTEXT["conversation_state"] = "responding"

    CONTEXT["updated"] = now()

    remember("assistant_output", {
        "text": text[:120],
    })

    return CONTEXT["last_assistant_output"]


# ============================================================
# ROUTE / SIGNAL / EVENT
# ============================================================

def set_route(route):

    CONTEXT["active_route"] = str(route)

    CONTEXT["updated"] = now()

    return route


def set_signal(signal):

    CONTEXT["active_signal"] = str(signal)

    CONTEXT["updated"] = now()

    return signal


def set_event(event):

    CONTEXT["active_event"] = str(event)

    CONTEXT["updated"] = now()

    return event


# ============================================================
# RUNTIME CONDITIONS
# ============================================================

def runtime_conditions(runtime_state=None):

    runtime_state = runtime_state or {}

    CONTEXT["pressure"] = runtime_state.get(
        "pressure",
        0.0,
    )

    CONTEXT["stability"] = runtime_state.get(
        "stability",
        1.0,
    )

    CONTEXT["ambiguity"] = runtime_state.get(
        "ambiguity",
        0.0,
    )

    CONTEXT["recovery"] = runtime_state.get(
        "recovery",
        False,
    )

    CONTEXT["updated"] = now()

    remember("runtime_conditions", {
        "pressure": CONTEXT["pressure"],
        "stability": CONTEXT["stability"],
    })

    return dict(CONTEXT)


# ============================================================
# RESET
# ============================================================

def reset():

    CONTEXT["topic"] = ""
    CONTEXT["intent"] = ""

    CONTEXT["focus"] = ""

    CONTEXT["conversation_state"] = "idle"

    CONTEXT["last_user_input"] = ""
    CONTEXT["last_assistant_output"] = ""

    CONTEXT["active_route"] = ""
    CONTEXT["active_signal"] = ""
    CONTEXT["active_event"] = ""

    CONTEXT["updated"] = now()

    remember("reset")

    log("context reset")

    return dict(CONTEXT)


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

    runtime_state = runtime_state or {}

    runtime_conditions(
        runtime_state
    )

    overloaded = False

    if CONTEXT["pressure"] >= 0.90:
        overloaded = True

    if CONTEXT["stability"] <= 0.25:
        overloaded = True

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "overloaded": overloaded,
        "context": dict(CONTEXT),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "context": dict(CONTEXT),
        "history_size": len(
            CONTEXT_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def context(runtime_state=None):
    return process(runtime_state)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" CONTEXT CORE STAGE3600")
    print("================================\n")

    user_input(
        "assistant show runtime"
    )

    set_topic(
        "runtime"
    )

    set_intent(
        "debug"
    )

    runtime_conditions({
        "pressure": 0.32,
        "stability": 0.91,
    })

    print(status())
