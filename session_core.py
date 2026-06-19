# ============================================================
# SESSION CORE — STAGE 3600
# Runtime session + live context layer
# ============================================================

import time
import uuid


STAGE = 3600

ENGINE_NAME = "SESSION_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# SESSION
# ============================================================

SESSION = {
    "id": None,
    "active": False,
    "created": 0.0,
    "last_activity": 0.0,
    "interaction_count": 0,
    "state": "idle",
    "mode": "balanced",
    "user_input": "",
    "assistant_output": "",
    "intent": "",
    "topic": "",
    "context": {},
}


# ============================================================
# HISTORY
# ============================================================

SESSION_HISTORY = []

MAX_HISTORY = 120


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[SESSION] {message}")


def remember(event, details=None):

    SESSION_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(SESSION_HISTORY) > MAX_HISTORY:
        SESSION_HISTORY.pop(0)


# ============================================================
# SESSION START
# ============================================================

def start(mode="balanced"):

    SESSION["id"] = str(uuid.uuid4())[:8]

    SESSION["active"] = True

    SESSION["created"] = now()
    SESSION["last_activity"] = now()

    SESSION["interaction_count"] = 0

    SESSION["state"] = "active"
    SESSION["mode"] = mode

    SESSION["user_input"] = ""
    SESSION["assistant_output"] = ""

    SESSION["intent"] = ""
    SESSION["topic"] = ""

    SESSION["context"] = {}

    remember("session_start", {
        "mode": mode,
    })

    log("session started")

    return dict(SESSION)


# ============================================================
# SESSION STOP
# ============================================================

def stop():

    SESSION["active"] = False

    SESSION["state"] = "stopped"

    SESSION["last_activity"] = now()

    remember("session_stop")

    log("session stopped")

    return dict(SESSION)


# ============================================================
# TOUCH
# ============================================================

def touch():

    SESSION["last_activity"] = now()

    return SESSION["last_activity"]


# ============================================================
# INPUT
# ============================================================

def input(text, intent=None):

    SESSION["user_input"] = str(text or "").strip()

    if intent:
        SESSION["intent"] = str(intent)

    SESSION["interaction_count"] += 1

    SESSION["last_activity"] = now()

    remember("input", {
        "text": SESSION["user_input"][:120],
        "intent": intent,
    })

    return dict(SESSION)


# ============================================================
# OUTPUT
# ============================================================

def output(text):

    SESSION["assistant_output"] = str(
        text or ""
    ).strip()

    SESSION["interaction_count"] += 1

    SESSION["last_activity"] = now()

    remember("output", {
        "text": SESSION["assistant_output"][:120],
    })

    return dict(SESSION)


# ============================================================
# TOPIC
# ============================================================

def set_topic(topic):

    SESSION["topic"] = str(topic)

    SESSION["last_activity"] = now()

    remember("topic", {
        "topic": topic,
    })

    return SESSION["topic"]


# ============================================================
# MODE
# ============================================================

def set_mode(mode):

    SESSION["mode"] = str(mode)

    SESSION["last_activity"] = now()

    remember("mode", {
        "mode": mode,
    })

    return SESSION["mode"]


# ============================================================
# CONTEXT
# ============================================================

def set_context(key, value):

    SESSION["context"][key] = value

    SESSION["last_activity"] = now()

    return value


def get_context(key=None, default=None):

    if key is None:
        return dict(SESSION["context"])

    return SESSION["context"].get(
        key,
        default,
    )


# ============================================================
# IDLE CHECK
# ============================================================

def idle_time():

    return round(
        now() - SESSION["last_activity"],
        2,
    )


def inactive(limit=300):

    return idle_time() >= limit


# ============================================================
# RESET
# ============================================================

def reset():

    current_mode = SESSION["mode"]

    start(mode=current_mode)

    remember("reset")

    log("session reset")

    return dict(SESSION)


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "session": dict(SESSION),
        "idle_seconds": idle_time(),
        "history_size": len(SESSION_HISTORY),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def session():
    return status()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" SESSION CORE STAGE3600")
    print("================================\n")

    start()

    input(
        "assistant open logs",
        intent="debug",
    )

    output(
        "Opening runtime logs."
    )

    set_topic(
        "runtime"
    )

    print(status())
