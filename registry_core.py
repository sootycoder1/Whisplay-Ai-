# ============================================================
# REGISTRY CORE — STAGE 3600
# Runtime registry + subsystem authority layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "REGISTRY_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# REGISTRY STORAGE
# ============================================================

REGISTRY = {}

REGISTRY_HISTORY = []

MAX_HISTORY = 120


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[REGISTRY] {message}")


def remember(event, details=None):

    REGISTRY_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(REGISTRY_HISTORY) > MAX_HISTORY:
        REGISTRY_HISTORY.pop(0)


# ============================================================
# REGISTRATION
# ============================================================

def register(
    name,
    obj=None,
    kind="runtime",
    enabled=True,
    metadata=None,
):

    metadata = metadata or {}

    entry = {
        "name": str(name),
        "object": obj,
        "kind": kind,
        "enabled": bool(enabled),
        "metadata": metadata,
        "registered": now(),
        "last_access": 0,
        "calls": 0,
    }

    REGISTRY[name] = entry

    remember("register", {
        "name": name,
        "kind": kind,
    })

    log(f"registered: {name}")

    return entry


# ============================================================
# UNREGISTER
# ============================================================

def unregister(name):

    if name not in REGISTRY:
        return False

    REGISTRY.pop(name)

    remember("unregister", {
        "name": name,
    })

    log(f"unregistered: {name}")

    return True


# ============================================================
# GET
# ============================================================

def get(name, default=None):

    entry = REGISTRY.get(name)

    if not entry:
        return default

    entry["last_access"] = now()
    entry["calls"] += 1

    return entry.get("object")


# ============================================================
# GET ENTRY
# ============================================================

def get_entry(name):

    entry = REGISTRY.get(name)

    if not entry:
        return None

    entry["last_access"] = now()
    entry["calls"] += 1

    return dict(entry)


# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable(name):

    if name not in REGISTRY:
        return False

    REGISTRY[name]["enabled"] = True

    remember("enable", {
        "name": name,
    })

    log(f"enabled: {name}")

    return True


def disable(name):

    if name not in REGISTRY:
        return False

    REGISTRY[name]["enabled"] = False

    remember("disable", {
        "name": name,
    })

    log(f"disabled: {name}")

    return True


# ============================================================
# EXISTS
# ============================================================

def exists(name):

    return name in REGISTRY


# ============================================================
# LIST
# ============================================================

def list_registry(kind=None):

    output = []

    for name, entry in REGISTRY.items():

        if kind and entry["kind"] != kind:
            continue

        output.append({
            "name": name,
            "kind": entry["kind"],
            "enabled": entry["enabled"],
            "calls": entry["calls"],
        })

    return output


# ============================================================
# CALL
# ============================================================

def call(name, *args, **kwargs):

    entry = REGISTRY.get(name)

    if not entry:
        return {
            "ok": False,
            "error": "missing",
            "name": name,
        }

    if not entry["enabled"]:
        return {
            "ok": False,
            "error": "disabled",
            "name": name,
        }

    obj = entry.get("object")

    if not callable(obj):
        return {
            "ok": False,
            "error": "not_callable",
            "name": name,
        }

    try:

        entry["last_access"] = now()
        entry["calls"] += 1

        result = obj(*args, **kwargs)

        return {
            "ok": True,
            "name": name,
            "result": result,
        }

    except Exception as e:

        log(f"call failed: {name}")

        return {
            "ok": False,
            "name": name,
            "error": str(e),
        }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "entries": len(REGISTRY),
        "history_size": len(REGISTRY_HISTORY),
        "registry": list_registry(),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def registry():
    return status()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" REGISTRY CORE STAGE3600")
    print("================================\n")

    def hello():
        return "hello runtime"

    register(
        "hello",
        hello,
        kind="test",
    )

    print(call("hello"))

    print(status())
