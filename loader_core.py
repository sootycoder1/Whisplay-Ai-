# ============================================================
# LOADER CORE — STAGE 3600
# Runtime subsystem loader + initialization layer
# ============================================================

import time
import traceback


STAGE = 3600

ENGINE_NAME = "LOADER_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# LOADER STATE
# ============================================================

LOADED = {}

FAILED = {}

LOAD_HISTORY = []

MAX_HISTORY = 200


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[LOADER] {message}")


def remember(event, details=None):

    LOAD_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(LOAD_HISTORY) > MAX_HISTORY:
        LOAD_HISTORY.pop(0)


# ============================================================
# LOAD
# ============================================================

def load(
    name,
    loader=None,
    required=False,
    metadata=None,
):

    metadata = metadata or {}

    started = now()

    try:

        result = None

        if callable(loader):
            result = loader()

        entry = {
            "name": name,
            "loaded": True,
            "required": required,
            "metadata": metadata,
            "result": result,
            "load_time": round(
                now() - started,
                4,
            ),
            "time": now(),
        }

        LOADED[name] = entry

        if name in FAILED:
            FAILED.pop(name)

        remember("load_success", {
            "name": name,
        })

        log(f"loaded: {name}")

        return {
            "ok": True,
            "entry": entry,
        }

    except Exception as e:

        error_entry = {
            "name": name,
            "loaded": False,
            "required": required,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "time": now(),
        }

        FAILED[name] = error_entry

        remember("load_failed", {
            "name": name,
            "error": str(e),
        })

        log(f"failed: {name}")

        if required:
            log(f"required subsystem failed: {name}")

        return {
            "ok": False,
            "error": error_entry,
        }


# ============================================================
# UNLOAD
# ============================================================

def unload(name):

    if name not in LOADED:
        return False

    LOADED.pop(name)

    remember("unload", {
        "name": name,
    })

    log(f"unloaded: {name}")

    return True


# ============================================================
# RELOAD
# ============================================================

def reload(
    name,
    loader=None,
    required=False,
    metadata=None,
):

    unload(name)

    return load(
        name=name,
        loader=loader,
        required=required,
        metadata=metadata,
    )


# ============================================================
# EXISTS
# ============================================================

def exists(name):

    return name in LOADED


# ============================================================
# GET
# ============================================================

def get(name):

    return LOADED.get(name)


# ============================================================
# FAILED CHECK
# ============================================================

def failed(name=None):

    if name is None:
        return dict(FAILED)

    return FAILED.get(name)


# ============================================================
# LOAD ORDER
# ============================================================

def boot_sequence():

    return [
        "registry_core",
        "signal_core",
        "session_core",
        "state_core",
        "health_core",
        "recovery_core",
        "strategy_engine",
    ]


# ============================================================
# SUMMARY
# ============================================================

def summary():

    return {
        "loaded": len(LOADED),
        "failed": len(FAILED),
        "loaded_systems": list(
            LOADED.keys()
        ),
        "failed_systems": list(
            FAILED.keys()
        ),
    }


# ============================================================
# PROCESS
# ============================================================

def process():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "summary": summary(),
        "boot_sequence": boot_sequence(),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "loaded": dict(LOADED),
        "failed": dict(FAILED),
        "history_size": len(LOAD_HISTORY),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def loader():
    return process()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" LOADER CORE STAGE3600")
    print("================================\n")

    def test_loader():
        return "runtime ready"

    load(
        "test_runtime",
        loader=test_loader,
        required=True,
    )

    print(process())
