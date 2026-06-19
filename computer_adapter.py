# ============================================================
# COMPUTER ADAPTER — STAGE 3600
# Runtime computer bridge + controlled system interface
# ============================================================

import os
import time
import subprocess
import traceback


STAGE = 3600

ENGINE_NAME = "COMPUTER_ADAPTER"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# COMPUTER STATE
# ============================================================

COMPUTER_STATE = {
    "enabled": True,
    "safe_mode": False,
    "lockdown": False,
    "shell_enabled": False,
    "filesystem_enabled": False,
    "network_enabled": False,
    "calls": 0,
    "failures": 0,
    "last_command": "",
    "last_error": "",
    "last_execution": 0.0,
}


# ============================================================
# EXECUTION POLICY
# ============================================================

POLICY = {
    "allow_shell": False,
    "allow_filesystem": False,
    "allow_network": False,
    "allow_shutdown": False,
    "allow_reboot": False,
}


# ============================================================
# SAFE COMMANDS
# ============================================================

SAFE_COMMANDS = [
    "ls",
    "pwd",
    "whoami",
    "uptime",
    "date",
    "hostname",
    "free",
    "df",
    "cat",
    "echo",
]


# ============================================================
# HISTORY
# ============================================================

COMPUTER_HISTORY = []

MAX_HISTORY = 240


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[COMPUTER] {message}")


def remember(event, details=None):

    COMPUTER_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(COMPUTER_HISTORY) > MAX_HISTORY:
        COMPUTER_HISTORY.pop(0)


def clean(text):

    return " ".join(
        str(text or "").strip().split()
    )


# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable():

    COMPUTER_STATE["enabled"] = True

    return True


def disable():

    COMPUTER_STATE["enabled"] = False

    return True


# ============================================================
# SAFE MODE
# ============================================================

def enable_safe_mode():

    COMPUTER_STATE["safe_mode"] = True

    remember("safe_mode_enabled")

    log("safe mode enabled")

    return True


def disable_safe_mode():

    COMPUTER_STATE["safe_mode"] = False

    remember("safe_mode_disabled")

    return True


# ============================================================
# LOCKDOWN
# ============================================================

def lockdown():

    COMPUTER_STATE["lockdown"] = True

    remember("lockdown")

    log("lockdown enabled")

    return True


def unlock():

    COMPUTER_STATE["lockdown"] = False

    remember("unlock")

    log("lockdown disabled")

    return True


# ============================================================
# POLICY CONTROL
# ============================================================

def set_policy(
    key,
    value,
):

    if key not in POLICY:
        return False

    POLICY[key] = bool(value)

    remember("policy_update", {
        "key": key,
        "value": value,
    })

    return True


# ============================================================
# VALIDATION
# ============================================================

def allowed(command):

    command = clean(command)

    if not command:
        return False

    base = command.split()[0]

    if base in SAFE_COMMANDS:
        return True

    if not POLICY["allow_shell"]:
        return False

    return True


# ============================================================
# SHELL EXECUTION
# ============================================================

def execute(
    command,
    timeout=5,
):

    command = clean(command)

    if not COMPUTER_STATE["enabled"]:

        return {
            "ok": False,
            "error": "adapter_disabled",
        }

    if COMPUTER_STATE["safe_mode"]:

        return {
            "ok": False,
            "error": "safe_mode_enabled",
        }

    if COMPUTER_STATE["lockdown"]:

        return {
            "ok": False,
            "error": "lockdown_enabled",
        }

    if not allowed(command):

        COMPUTER_STATE["failures"] += 1

        return {
            "ok": False,
            "error": "command_blocked",
        }

    try:

        COMPUTER_STATE["calls"] += 1

        COMPUTER_STATE["last_command"] = command

        COMPUTER_STATE["last_execution"] = now()

        remember("execute", {
            "command": command,
        })

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "ok": True,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except Exception as e:

        COMPUTER_STATE["failures"] += 1

        COMPUTER_STATE["last_error"] = str(e)

        remember("execution_failure", {
            "command": command,
            "error": str(e),
        })

        if DEBUG:
            print(traceback.format_exc())

        return {
            "ok": False,
            "error": str(e),
        }


# ============================================================
# FILE CHECK
# ============================================================

def exists(path):

    try:
        return os.path.exists(path)

    except Exception:
        return False


# ============================================================
# DIRECTORY LIST
# ============================================================

def list_directory(path="."):

    if not POLICY["allow_filesystem"]:

        return {
            "ok": False,
            "error": "filesystem_disabled",
        }

    try:

        files = os.listdir(path)

        remember("list_directory", {
            "path": path,
        })

        return {
            "ok": True,
            "path": path,
            "files": files,
        }

    except Exception as e:

        return {
            "ok": False,
            "error": str(e),
        }


# ============================================================
# PROCESS
# ============================================================

def process(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    recovery = runtime_state.get(
        "recovery",
        False,
    )

    blocked = runtime_state.get(
        "blocked",
        False,
    )

    if recovery:
        enable_safe_mode()

    if blocked:
        lockdown()

    if pressure >= 0.95:
        lockdown()

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "safe_mode": COMPUTER_STATE[
            "safe_mode"
        ],
        "lockdown": COMPUTER_STATE[
            "lockdown"
        ],
        "calls": COMPUTER_STATE[
            "calls"
        ],
        "failures": COMPUTER_STATE[
            "failures"
        ],
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "state": dict(COMPUTER_STATE),
        "policy": dict(POLICY),
        "history_size": len(
            COMPUTER_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def computer(command):

    return execute(command)


def shell(command):

    return execute(command)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" COMPUTER ADAPTER STAGE3600")
    print("================================\n")

    print(
        execute(
            "pwd"
        )
    )

    print(status())
