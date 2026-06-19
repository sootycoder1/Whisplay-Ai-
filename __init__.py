# ============================================================
# WHISPLAY RUNTIME INIT
# STAGE 3600
# ============================================================


# ============================================================
# CORE IMPORTS
# ============================================================

from registry_core import *
from signal_core import *
from session_core import *
from state_core import *
from health_core import *
from recovery_core import *
from loader_core import *


# ============================================================
# OPTIONAL IMPORTS
# ============================================================

try:
    from strategy_engine import *
except Exception:
    pass


# ============================================================
# RUNTIME INFO
# ============================================================

RUNTIME_NAME = "WHISPLAY_RUNTIME"

RUNTIME_STAGE = 3600

RUNTIME_VERSION = "3600.1-STABLE"


# ============================================================
# STATUS
# ============================================================

def runtime_status():

    return {
        "runtime": RUNTIME_NAME,
        "stage": RUNTIME_STAGE,
        "version": RUNTIME_VERSION,
    }


# ============================================================
# BOOT
# ============================================================

def runtime_boot():

    systems = [
        "registry_core",
        "signal_core",
        "session_core",
        "state_core",
        "health_core",
        "recovery_core",
        "loader_core",
        "strategy_engine",
    ]

    return {
        "boot": True,
        "systems": systems,
        "count": len(systems),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" WHISPLAY RUNTIME INIT")
    print("================================\n")

    print(runtime_status())

    print(runtime_boot())
