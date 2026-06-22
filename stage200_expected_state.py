# WHISPLAY STAGE 200 — EXPECTED SYSTEM STATE (Advisory)

STAGE200_EXPECTED = {
    "meta": {
        "type": "reference_model",
        "mode": "advisory_only",
        "enforcement": False,
        "purpose": [
            "define_expected_system_shape",
            "assist_builders",
            "detect_runtime_drift",
        ],
    },
    "system": {
        "status": "online",
        "runtime_state": "idle",
        "subsystems_online": 7,
        "errors": 0,
    },
    "core_layers": {
        "contract": {"autonomy_readonly": True},
        "bus": {"guard_active": True},
        "state": {"can_reason": False},
    },
    "controller": {
        "gpio_enabled": False,
        "safe_mode": False,
    },
    "autonomy": {
        "mode": "observe_only",
        "can_execute": False,
    },
    "hardware": {
        "gpio": {"enabled": False},
        "spi": {"scope": "display_only"},
    },
}

TOLERANCE = {
    "subsystems_online_min": 7,
    "max_errors": 0,
    "allowed_runtime_states": ["idle", "listening", "thinking", "speaking"],
}

def calculate_drift(current: dict):
    score = 0
    issues = []
    try:
        if current.get("status") != "online":
            score += 20
            issues.append("system_not_online")
        if current.get("errors", 0) > TOLERANCE["max_errors"]:
            score += 15
            issues.append("errors_present")
        if current.get("subsystems_online", 0) < TOLERANCE["subsystems_online_min"]:
            score += 15
            issues.append("low_subsystems")
        if current.get("runtime_state") not in TOLERANCE["allowed_runtime_states"]:
            score += 10
            issues.append("invalid_runtime_state")
        auto = current.get("autonomy200", {})
        if auto.get("can_execute", False):
            score += 25
            issues.append("autonomy_executing")
        core = current.get("stage200_core", {})
        if core.get("gpio_enabled", False):
            score += 20
            issues.append("gpio_enabled")
    except Exception as e:
        score = 100
        issues.append(f"drift_check_error:{str(e)}")
    return {
        "drift_score": min(score, 100),
        "health": 100 - min(score, 100),
        "issues": issues,
    }

def expected_stage200():
    return dict(STAGE200_EXPECTED)
