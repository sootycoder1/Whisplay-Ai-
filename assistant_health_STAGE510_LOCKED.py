# ============================================================
# WHISPLAY ASSISTANT HEALTH
# STAGE 510 — MULTI-ACTOR RUNTIME HEALTH CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_profile_registry_STAGE430_LOCKED as registry
import assistant_selector_STAGE440_LOCKED as selector
import assistant_context_STAGE450_LOCKED as context
import assistant_session_STAGE460_LOCKED as session
import assistant_response_STAGE470_LOCKED as response_layer
import assistant_action_gate_STAGE480_LOCKED as action_gate
import assistant_turn_STAGE490_LOCKED as turn
import assistant_runtime_STAGE500_LOCKED as runtime


ENGINE_NAME = "assistant_health"
ENGINE_STAGE = 510
ENGINE_VERSION = "510.0-candidate"


EXPECTED_STAGES = {
    "registry": 430,
    "selector": 440,
    "context": 450,
    "session": 460,
    "response": 470,
    "action_gate": 480,
    "turn": 490,
    "runtime": 500,
}


MODULES = {
    "registry": registry,
    "selector": selector,
    "context": context,
    "session": session,
    "response": response_layer,
    "action_gate": action_gate,
    "turn": turn,
    "runtime": runtime,
}


STATE = {
    "checks": 0,
    "passes": 0,
    "failures": 0,
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def check_module(name, module):
    expected_stage = EXPECTED_STAGES[name]
    actual_stage = getattr(module, "ENGINE_STAGE", None)
    engine_name = getattr(module, "ENGINE_NAME", None)

    required_callable = {
        "registry": "status",
        "selector": "select_profile",
        "context": "status",
        "session": "status",
        "response": "status",
        "action_gate": "status",
        "turn": "status",
        "runtime": "status",
    }[name]

    interface_ok = callable(
        getattr(module, required_callable, None)
    )

    ok = (
        engine_name is not None
        and actual_stage == expected_stage
        and interface_ok
    )

    return {
        "ok": ok,
        "name": name,
        "engine": engine_name,
        "expected_stage": expected_stage,
        "actual_stage": actual_stage,
        "required_callable": required_callable,
        "interface_ok": interface_ok,
        "has_status": callable(getattr(module, "status", None)),
    }


def run_checks():
    STATE["checks"] += 1
    STATE["updated"] = now()

    results = {
        name: check_module(name, module)
        for name, module in MODULES.items()
    }

    runtime_result = runtime.active()

    runtime_ok = (
        runtime_result.get("ok") is True
        and runtime_result.get("profile", {}).get("id")
        in registry.list_profiles()
    )

    all_modules_ok = all(
        result["ok"]
        for result in results.values()
    )

    overall_ok = all_modules_ok and runtime_ok

    if overall_ok:
        STATE["passes"] += 1
        STATE["last_result"] = "healthy"
    else:
        STATE["failures"] += 1
        STATE["last_result"] = "unhealthy"

    return {
        "ok": overall_ok,
        "modules": results,
        "runtime": {
            "ok": runtime_ok,
            "active": runtime_result,
        },
        "state": snapshot(),
    }


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "expected_stages": deepcopy(EXPECTED_STAGES),
        "modules": list(MODULES.keys()),
        "state": snapshot(),
    }
