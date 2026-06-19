# ============================================================
# ADAPTER TOOLS CORE — STAGE 3600
# Runtime adapter + external tool bridge layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "ADAPTER_TOOLS_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOLS = {}

TOOL_HISTORY = []

MAX_HISTORY = 300


# ============================================================
# TOOL STATE
# ============================================================

STATE = {
    "enabled": True,
    "safe_mode": False,
    "calls": 0,
    "failures": 0,
    "last_tool": "",
    "last_error": "",
    "last_call_time": 0.0,
}


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[ADAPTER] {message}")


def remember(event, details=None):

    TOOL_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(TOOL_HISTORY) > MAX_HISTORY:
        TOOL_HISTORY.pop(0)


# ============================================================
# REGISTER TOOL
# ============================================================

def register(
    name,
    handler=None,
    enabled=True,
    metadata=None,
):

    metadata = metadata or {}

    TOOLS[name] = {
        "name": name,
        "handler": handler,
        "enabled": enabled,
        "metadata": metadata,
        "calls": 0,
        "failures": 0,
        "registered": now(),
    }

    remember("register", {
        "tool": name,
    })

    log(f"registered: {name}")

    return TOOLS[name]


# ============================================================
# REMOVE TOOL
# ============================================================

def remove(name):

    if name not in TOOLS:
        return False

    TOOLS.pop(name)

    remember("remove", {
        "tool": name,
    })

    log(f"removed: {name}")

    return True


# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable(name):

    if name not in TOOLS:
        return False

    TOOLS[name]["enabled"] = True

    remember("enable", {
        "tool": name,
    })

    return True


def disable(name):

    if name not in TOOLS:
        return False

    TOOLS[name]["enabled"] = False

    remember("disable", {
        "tool": name,
    })

    return True


# ============================================================
# EXISTS
# ============================================================

def exists(name):

    return name in TOOLS


# ============================================================
# GET
# ============================================================

def get(name):

    return TOOLS.get(name)


# ============================================================
# SAFE MODE
# ============================================================

def enable_safe_mode():

    STATE["safe_mode"] = True

    remember("safe_mode_enabled")

    log("safe mode enabled")

    return True


def disable_safe_mode():

    STATE["safe_mode"] = False

    remember("safe_mode_disabled")

    log("safe mode disabled")

    return True


# ============================================================
# CALL TOOL
# ============================================================

def call(
    name,
    *args,
    **kwargs,
):

    if not STATE["enabled"]:

        return {
            "ok": False,
            "error": "adapter_disabled",
        }

    if name not in TOOLS:

        STATE["failures"] += 1

        return {
            "ok": False,
            "error": "missing_tool",
        }

    tool = TOOLS[name]

    if not tool["enabled"]:

        return {
            "ok": False,
            "error": "tool_disabled",
        }

    handler = tool.get("handler")

    if not callable(handler):

        return {
            "ok": False,
            "error": "invalid_handler",
        }

    try:

        result = handler(
            *args,
            **kwargs,
        )

        STATE["calls"] += 1

        STATE["last_tool"] = name

        STATE["last_call_time"] = now()

        tool["calls"] += 1

        remember("call", {
            "tool": name,
        })

        return {
            "ok": True,
            "tool": name,
            "result": result,
        }

    except Exception as e:

        STATE["failures"] += 1

        STATE["last_error"] = str(e)

        tool["failures"] += 1

        remember("failure", {
            "tool": name,
            "error": str(e),
        })

        log(f"failure: {name}")

        return {
            "ok": False,
            "tool": name,
            "error": str(e),
        }


# ============================================================
# LIST TOOLS
# ============================================================

def list_tools():

    output = []

    for name, tool in TOOLS.items():

        output.append({
            "name": name,
            "enabled": tool["enabled"],
            "calls": tool["calls"],
            "failures": tool["failures"],
        })

    return output


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    if pressure >= 0.90:
        enable_safe_mode()

    overloaded = False

    if STATE["failures"] >= 10:
        overloaded = True

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "safe_mode": STATE["safe_mode"],
        "overloaded": overloaded,
        "tools": len(TOOLS),
        "calls": STATE["calls"],
        "failures": STATE["failures"],
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "state": dict(STATE),
        "tools": list_tools(),
        "history_size": len(
            TOOL_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def adapter():
    return status()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" ADAPTER TOOLS CORE STAGE3600")
    print("================================\n")

    def hello():
        return "runtime online"

    register(
        "hello_tool",
        hello,
    )

    print(
        call(
            "hello_tool"
        )
    )

    print(status())
