# ============================================================
# DEBUG CORE — STAGE 3600
# Runtime diagnostics + visibility layer
# ============================================================

import time
import traceback


STAGE = 3600

ENGINE_NAME = "DEBUG_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# DEBUG FLAGS
# ============================================================

DEBUG_ENABLED = True

TRACEBACKS_ENABLED = True

CONSOLE_OUTPUT = True


# ============================================================
# LOG STORAGE
# ============================================================

LOGS = []

ERRORS = []

WARNINGS = []

MAX_LOGS = 400


# ============================================================
# LEVELS
# ============================================================

LEVELS = {
    "info": 1,
    "warning": 2,
    "error": 3,
    "critical": 4,
}


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def timestamp():

    return round(now(), 3)


def trim(storage):

    while len(storage) > MAX_LOGS:
        storage.pop(0)


# ============================================================
# CORE LOGGING
# ============================================================

def write(
    message,
    level="info",
    source="runtime",
    payload=None,
):

    payload = payload or {}

    entry = {
        "time": timestamp(),
        "level": level,
        "priority": LEVELS.get(
            level,
            1,
        ),
        "source": source,
        "message": str(message),
        "payload": payload,
    }

    LOGS.append(entry)

    trim(LOGS)

    if level == "warning":
        WARNINGS.append(entry)
        trim(WARNINGS)

    if level in [
        "error",
        "critical",
    ]:
        ERRORS.append(entry)
        trim(ERRORS)

    if CONSOLE_OUTPUT:

        print(
            f"[{source.upper()}]"
            f"[{level.upper()}] "
            f"{message}"
        )

    return entry


# ============================================================
# SHORTCUTS
# ============================================================

def info(message, source="runtime"):

    return write(
        message,
        level="info",
        source=source,
    )


def warning(message, source="runtime"):

    return write(
        message,
        level="warning",
        source=source,
    )


def error(message, source="runtime"):

    return write(
        message,
        level="error",
        source=source,
    )


def critical(message, source="runtime"):

    return write(
        message,
        level="critical",
        source=source,
    )


# ============================================================
# TRACEBACK
# ============================================================

def exception(
    e,
    source="runtime",
):

    trace = traceback.format_exc()

    entry = write(
        str(e),
        level="critical",
        source=source,
        payload={
            "traceback": trace,
        },
    )

    if TRACEBACKS_ENABLED:
        print(trace)

    return entry


# ============================================================
# FETCH
# ============================================================

def logs(limit=20):

    return LOGS[-limit:]


def warnings(limit=20):

    return WARNINGS[-limit:]


def errors(limit=20):

    return ERRORS[-limit:]


# ============================================================
# FILTER
# ============================================================

def by_source(
    source,
    limit=20,
):

    output = []

    for log in LOGS:

        if log["source"] == source:
            output.append(log)

    return output[-limit:]


def by_level(
    level,
    limit=20,
):

    output = []

    for log in LOGS:

        if log["level"] == level:
            output.append(log)

    return output[-limit:]


# ============================================================
# CLEAR
# ============================================================

def clear():

    LOGS.clear()
    WARNINGS.clear()
    ERRORS.clear()

    return True


# ============================================================
# DEBUG FLAGS
# ============================================================

def enable():

    global DEBUG_ENABLED

    DEBUG_ENABLED = True

    return DEBUG_ENABLED


def disable():

    global DEBUG_ENABLED

    DEBUG_ENABLED = False

    return DEBUG_ENABLED


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    stability = runtime_state.get(
        "stability",
        1.0,
    )

    if pressure >= 0.90:

        warning(
            "pressure critical",
            source="health",
        )

    if stability <= 0.25:

        critical(
            "runtime instability",
            source="recovery",
        )

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "logs": len(LOGS),
        "warnings": len(WARNINGS),
        "errors": len(ERRORS),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "debug_enabled": DEBUG_ENABLED,
        "tracebacks_enabled": TRACEBACKS_ENABLED,
        "console_output": CONSOLE_OUTPUT,
        "logs": len(LOGS),
        "warnings": len(WARNINGS),
        "errors": len(ERRORS),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def log(message):
    return info(message)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" DEBUG CORE STAGE3600")
    print("================================\n")

    info(
        "runtime online",
        source="runtime",
    )

    warning(
        "pressure elevated",
        source="health",
    )

    error(
        "display timeout",
        source="display",
    )

    print(status())
