# ============================================================
# WHISPLAY ASSISTANT RECOVERY GATE
# STAGE 550 — CONTROLLED RECOVERY APPROVAL GATE CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_recovery_STAGE540_LOCKED as recovery


ENGINE_NAME = "assistant_recovery_gate"
ENGINE_STAGE = 550
ENGINE_VERSION = "550.0-candidate"

READ_ONLY = True
EXECUTION_ALLOWED = False


DECISIONS = {
    "auto_safe",
    "approval_required",
    "blocked",
}


FAULT_POLICY = {
    "missing_engine": "approval_required",
    "stage_mismatch": "blocked",
    "missing_interface": "blocked",
    "runtime_failure": "approval_required",
    "unknown_failure": "blocked",
}


STATE = {
    "evaluations": 0,
    "healthy_results": 0,
    "auto_safe_results": 0,
    "approval_results": 0,
    "blocked_results": 0,
    "items_evaluated": 0,
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def evaluate_item(item):
    fault_type = str(
        item.get("fault_type") or "unknown_failure"
    )

    decision = FAULT_POLICY.get(
        fault_type,
        "blocked",
    )

    reason = {
        "auto_safe": (
            "The recovery type is explicitly allow-listed "
            "for future controlled automation."
        ),
        "approval_required": (
            "The recovery path is known, but user approval "
            "is required before any action."
        ),
        "blocked": (
            "The fault is unsafe or unclear and must not be "
            "recovered automatically."
        ),
    }[decision]

    return {
        "fault_type": fault_type,
        "module": str(item.get("module") or "unknown"),
        "priority": item.get("priority", "high"),
        "decision": decision,
        "reason": reason,
        "recommended_action": item.get(
            "recommended_action",
            "",
        ),
        "recovery_target": item.get(
            "recovery_target",
            "",
        ),
        "verification": item.get(
            "verification",
            "",
        ),
        "user_approval_required": (
            decision == "approval_required"
        ),
        "automatic_execution_allowed": False,
        "read_only": True,
    }


def evaluate(report=None):
    STATE["evaluations"] += 1
    STATE["updated"] = now()

    recommendations = (
        deepcopy(report)
        if isinstance(report, dict)
        and "recommendations" in report
        else recovery.recommend(report)
    )

    decisions = [
        evaluate_item(item)
        for item in recommendations.get(
            "recommendations",
            [],
        )
    ]

    STATE["items_evaluated"] += len(decisions)

    counts = {
        "auto_safe": 0,
        "approval_required": 0,
        "blocked": 0,
    }

    for item in decisions:
        counts[item["decision"]] += 1

    healthy = (
        recommendations.get("ok") is True
        and not decisions
    )

    if healthy:
        overall_decision = "continue"
        STATE["healthy_results"] += 1
        STATE["last_result"] = "continue"
    elif counts["blocked"] > 0:
        overall_decision = "blocked"
        STATE["blocked_results"] += 1
        STATE["last_result"] = "blocked"
    elif counts["approval_required"] > 0:
        overall_decision = "approval_required"
        STATE["approval_results"] += 1
        STATE["last_result"] = "approval_required"
    else:
        overall_decision = "auto_safe"
        STATE["auto_safe_results"] += 1
        STATE["last_result"] = "auto_safe"

    return {
        "ok": healthy,
        "overall_decision": overall_decision,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "decision_count": len(decisions),
        "counts": counts,
        "decisions": decisions,
        "failed_modules": deepcopy(
            recommendations.get(
                "failed_modules",
                [],
            )
        ),
        "state": snapshot(),
    }


def readable_gate(report=None):
    result = evaluate(report)

    if result["ok"]:
        return (
            "Recovery gate: CONTINUE. "
            "No recovery action required."
        )

    lines = [
        "WHISPLAY RECOVERY APPROVAL GATE",
        f"Overall decision: {result['overall_decision'].upper()}",
        "Execution allowed: NO",
        f"Decision count: {result['decision_count']}",
    ]

    for item in result["decisions"]:
        lines.extend([
            (
                f"- [{item['decision'].upper()}] "
                f"{item['fault_type']} in {item['module']}"
            ),
            f"  Reason: {item['reason']}",
            (
                "  User approval required: "
                f"{'YES' if item['user_approval_required'] else 'NO'}"
            ),
            "  Automatic execution allowed: NO",
            (
                "  Recommended action: "
                f"{item['recommended_action']}"
            ),
            f"  Verification: {item['verification']}",
        ])

    return "\n".join(lines)


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "decisions": sorted(DECISIONS),
        "fault_policy": deepcopy(FAULT_POLICY),
        "state": snapshot(),
    }
