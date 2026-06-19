# ============================================================
# SAFETY CORE — STAGE 3600
# Runtime safety authority + veto layer
# ============================================================

import time


STAGE = 3600

ENGINE_NAME = "SAFETY_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


SAFETY = {
    "enabled": True,
    "lockdown": False,
    "containment": False,
    "last_risk": 0.0,
    "last_decision": "allow",
    "last_reason": "",
    "checks": 0,
    "blocks": 0,
    "warnings": 0,
    "last_check": 0.0,
}


LIMITS = {
    "warn": 0.45,
    "block": 0.72,
    "critical": 0.90,
}


DANGEROUS_PATTERNS = [
    "delete",
    "wipe",
    "format",
    "rm -rf",
    "shutdown",
    "reboot",
    "sudo",
    "chmod",
    "chown",
    "dd if",
    "mkfs",
    "killall",
    "override",
    "bypass",
    "disable safety",
    "disable permissions",
    "turn off recovery",
    "ignore watchdog",
]


CRITICAL_TARGETS = [
    "filesystem",
    "shell",
    "network",
    "gpio",
    "audio",
    "display",
    "memory",
    "recovery_core",
    "permissions_core",
    "runtime_core",
]


ADAPTER_RESTRICTIONS = {
    "computer_adapter": 0.55,
    "adapter_tools_core": 0.60,
    "speech_adapter": 0.80,
    "brain_adapter": 0.75,
}


SAFETY_HISTORY = []
MAX_HISTORY = 300


def now():
    return time.time()


def log(message):
    if DEBUG:
        print(f"[SAFETY] {message}")


def clamp(value, low, high):
    return max(low, min(high, value))


def remember(event, details=None):
    SAFETY_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(SAFETY_HISTORY) > MAX_HISTORY:
        SAFETY_HISTORY.pop(0)


def clean(text):
    return " ".join(str(text or "").strip().split())


def pattern_risk(text):
    t = clean(text).lower()

    hits = []

    for pattern in DANGEROUS_PATTERNS:
        if pattern in t:
            hits.append(pattern)

    score = min(1.0, len(hits) * 0.22)

    return score, hits


def target_risk(target):
    target = str(target or "").lower()

    if not target:
        return 0.0, []

    hits = []

    for item in CRITICAL_TARGETS:
        if item in target:
            hits.append(item)

    score = min(1.0, len(hits) * 0.18)

    return score, hits


def adapter_risk(adapter):
    adapter = str(adapter or "")

    if adapter in ADAPTER_RESTRICTIONS:
        return ADAPTER_RESTRICTIONS[adapter]

    return 0.20


def runtime_risk(runtime_state=None):
    runtime_state = runtime_state or {}

    pressure = runtime_state.get("pressure", 0.0)
    ambiguity = runtime_state.get("ambiguity", 0.0)
    stability = runtime_state.get("stability", 1.0)
    recovery = runtime_state.get("recovery", False)
    blocked = runtime_state.get("blocked", False)

    risk = 0.0

    risk += pressure * 0.28
    risk += ambiguity * 0.22
    risk += (1.0 - stability) * 0.30

    if recovery:
        risk += 0.12

    if blocked:
        risk += 0.25

    return clamp(risk, 0.0, 1.0)


def score(
    text="",
    target="",
    adapter="",
    runtime_state=None,
):
    runtime_state = runtime_state or {}

    p_score, patterns = pattern_risk(text)
    t_score, targets = target_risk(target)
    a_score = adapter_risk(adapter)
    r_score = runtime_risk(runtime_state)

    total = (
        p_score * 0.35
        + t_score * 0.20
        + a_score * 0.15
        + r_score * 0.30
    )

    total = clamp(total, 0.0, 1.0)

    return {
        "risk": round(total, 3),
        "pattern_risk": round(p_score, 3),
        "target_risk": round(t_score, 3),
        "adapter_risk": round(a_score, 3),
        "runtime_risk": round(r_score, 3),
        "patterns": patterns,
        "targets": targets,
    }


def decide(
    text="",
    target="",
    adapter="",
    runtime_state=None,
):
    if not SAFETY["enabled"]:
        return {
            "allow": True,
            "decision": "allow",
            "reason": "safety_disabled",
        }

    result = score(
        text=text,
        target=target,
        adapter=adapter,
        runtime_state=runtime_state,
    )

    risk = result["risk"]

    decision = "allow"
    allow = True
    reason = "risk_clear"

    if SAFETY["lockdown"]:
        decision = "block"
        allow = False
        reason = "lockdown_active"

    elif risk >= LIMITS["critical"]:
        decision = "critical_block"
        allow = False
        reason = "critical_risk"

    elif risk >= LIMITS["block"]:
        decision = "block"
        allow = False
        reason = "risk_too_high"

    elif risk >= LIMITS["warn"]:
        decision = "warn"
        allow = True
        reason = "risk_warning"

    SAFETY["checks"] += 1
    SAFETY["last_risk"] = risk
    SAFETY["last_decision"] = decision
    SAFETY["last_reason"] = reason
    SAFETY["last_check"] = now()

    if not allow:
        SAFETY["blocks"] += 1

    if decision == "warn":
        SAFETY["warnings"] += 1

    remember("decision", {
        "decision": decision,
        "reason": reason,
        "risk": risk,
        "target": target,
        "adapter": adapter,
    })

    return {
        "allow": allow,
        "decision": decision,
        "reason": reason,
        "score": result,
        "safety": status(),
    }


def veto(
    text="",
    target="",
    adapter="",
    runtime_state=None,
):
    decision = decide(
        text=text,
        target=target,
        adapter=adapter,
        runtime_state=runtime_state,
    )

    return not decision["allow"]


def escalate(reason="unknown"):
    SAFETY["containment"] = True

    remember("escalate", {
        "reason": reason,
    })

    log(f"containment active: {reason}")

    return status()


def contain(reason="manual"):
    SAFETY["containment"] = True

    remember("containment", {
        "reason": reason,
    })

    log(f"contained: {reason}")

    return status()


def release_containment():
    SAFETY["containment"] = False

    remember("containment_released")

    log("containment released")

    return status()


def lockdown(reason="manual"):
    SAFETY["lockdown"] = True
    SAFETY["containment"] = True

    remember("lockdown", {
        "reason": reason,
    })

    log(f"lockdown: {reason}")

    return status()


def unlock():
    SAFETY["lockdown"] = False

    remember("unlock")

    log("lockdown released")

    return status()


def enable():
    SAFETY["enabled"] = True
    return True


def disable():
    SAFETY["enabled"] = False
    return True


def process(
    text="",
    runtime_state=None,
    target="runtime",
    adapter="",
):
    runtime_state = runtime_state or {}

    decision = decide(
        text=text,
        target=target,
        adapter=adapter,
        runtime_state=runtime_state,
    )

    risk = decision["score"]["risk"]

    if risk >= LIMITS["critical"]:
        lockdown("critical_risk")

    elif risk >= LIMITS["block"]:
        contain("block_level_risk")

    elif runtime_state.get("recovery"):
        contain("runtime_recovery_active")

    return decision


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "enabled": SAFETY["enabled"],
        "lockdown": SAFETY["lockdown"],
        "containment": SAFETY["containment"],
        "last_risk": SAFETY["last_risk"],
        "last_decision": SAFETY["last_decision"],
        "last_reason": SAFETY["last_reason"],
        "checks": SAFETY["checks"],
        "blocks": SAFETY["blocks"],
        "warnings": SAFETY["warnings"],
        "history_size": len(SAFETY_HISTORY),
    }


def safety(
    text="",
    runtime_state=None,
    target="runtime",
    adapter="",
):
    return process(
        text=text,
        runtime_state=runtime_state,
        target=target,
        adapter=adapter,
    )


if __name__ == "__main__":
    test_state = {
        "pressure": 0.82,
        "stability": 0.40,
        "ambiguity": 0.35,
        "recovery": False,
    }

    print(
        process(
            text="delete old runtime files",
            target="filesystem",
            adapter="computer_adapter",
            runtime_state=test_state,
        )
    )
