
# ============================================================
# WHISPLAY ASSISTANT RECOVERY PLAN
# STAGE 570 — CONTROLLED NON-EXECUTING RECOVERY PLAN CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_recovery_policy_STAGE560_LOCKED as policy


ENGINE_NAME = "assistant_recovery_plan"
ENGINE_STAGE = 570
ENGINE_VERSION = "570.0-candidate"

READ_ONLY = True
EXECUTION_ALLOWED = False


STATE = {
    "plans_built": 0,
    "healthy_results": 0,
    "blocked_plans": 0,
    "approval_plans": 0,
    "auto_safe_plans": 0,
    "steps_created": 0,
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def make_step(
    number,
    action,
    level,
    description,
    stop_on_failure=True,
):
    return {
        "step": number,
        "action": action,
        "level": level,
        "description": description,
        "stop_on_failure": stop_on_failure,
        "execution_allowed": False,
        "completed": False,
        "read_only": True,
    }


def build_fault_plan(fault_type, module="unknown", location=""):
    fault_name = str(fault_type or "unknown_failure")
    module_name = str(module or "unknown")
    fault_location = str(location or "unknown")

    fingerprint = policy.fault_fingerprint(
        fault_name,
        module_name,
        fault_location,
    )

    fault_policy = policy.policy_for_fault(fault_name)
    actions = fault_policy.get("actions", [])

    steps = []

    for number, item in enumerate(actions, start=1):
        steps.append(
            make_step(
                number=number,
                action=item["action"],
                level=item["level"],
                description=item["description"],
            )
        )

    levels = {
        item.get("level", "forbidden")
        for item in actions
    }

    if "forbidden" in levels:
        decision = "blocked"
    elif "approval_required" in levels:
        decision = "approval_required"
    elif actions:
        decision = "auto_safe"
    else:
        decision = "blocked"

    return {
        "ok": decision != "blocked",
        "fault_type": fault_name,
        "module": module_name,
        "location": fault_location,
        "fingerprint": fingerprint,
        "decision": decision,
        "approval_required": decision == "approval_required",
        "execution_allowed": EXECUTION_ALLOWED,
        "read_only": READ_ONLY,
        "step_count": len(steps),
        "steps": steps,
        "stop_conditions": [
            "Stop immediately if any step fails.",
            "Stop if the same fault fingerprint reappears.",
            "Stop if recovery is already active.",
            "Stop after one recovery attempt.",
            "Stop after one rollback attempt.",
            "Stop if verification does not pass.",
        ],
        "verification_required": True,
        "rollback_allowed": (
            policy.ANTI_LOOP_POLICY[
                "max_rollback_attempts"
            ] == 1
        ),
        "max_recovery_attempts": policy.ANTI_LOOP_POLICY[
            "max_recovery_attempts"
        ],
        "max_rollback_attempts": policy.ANTI_LOOP_POLICY[
            "max_rollback_attempts"
        ],
        "cooldown_seconds": policy.ANTI_LOOP_POLICY[
            "cooldown_seconds"
        ],
    }


def build(report=None):
    STATE["plans_built"] += 1
    STATE["updated"] = now()

    gate_policy = (
        deepcopy(report)
        if isinstance(report, dict)
        and "policies" in report
        else policy.evaluate_gate(report)
    )

    plans = []

    for item in gate_policy.get("policies", []):
        fault_type = item.get(
            "fault_type",
            "unknown_failure",
        )

        plans.append(
            build_fault_plan(
                fault_type=fault_type,
                module="unknown",
                location="",
            )
        )

    STATE["steps_created"] += sum(
        item["step_count"]
        for item in plans
    )

    if gate_policy.get("ok") is True and not plans:
        overall_decision = "continue"
        STATE["healthy_results"] += 1
        STATE["last_result"] = "continue"
    elif any(
        item["decision"] == "blocked"
        for item in plans
    ):
        overall_decision = "blocked"
        STATE["blocked_plans"] += 1
        STATE["last_result"] = "blocked"
    elif any(
        item["decision"] == "approval_required"
        for item in plans
    ):
        overall_decision = "approval_required"
        STATE["approval_plans"] += 1
        STATE["last_result"] = "approval_required"
    else:
        overall_decision = "auto_safe"
        STATE["auto_safe_plans"] += 1
        STATE["last_result"] = "auto_safe"

    return {
        "ok": overall_decision == "continue",
        "overall_decision": overall_decision,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "plan_count": len(plans),
        "plans": plans,
        "anti_loop_policy": deepcopy(
            policy.ANTI_LOOP_POLICY
        ),
        "state": snapshot(),
    }


def readable_plan(report=None):
    result = build(report)

    if result["ok"]:
        return (
            "Recovery plan: CONTINUE. "
            "No recovery steps required."
        )

    lines = [
        "WHISPLAY CONTROLLED RECOVERY PLAN",
        f"Overall decision: {result['overall_decision'].upper()}",
        "Execution allowed: NO",
        f"Plan count: {result['plan_count']}",
    ]

    for plan in result["plans"]:
        lines.extend([
            (
                f"- Fault: {plan['fault_type']} "
                f"in {plan['module']}"
            ),
            f"  Decision: {plan['decision'].upper()}",
            f"  Fingerprint: {plan['fingerprint']}",
            (
                "  Approval required: "
                f"{'YES' if plan['approval_required'] else 'NO'}"
            ),
            f"  Step count: {plan['step_count']}",
        ])

        for step in plan["steps"]:
            lines.append(
                f"  {step['step']}. "
                f"{step['action']} "
                f"[{step['level'].upper()}]"
            )

        lines.append(
            "  Verification required: YES"
        )
        lines.append(
            "  Automatic execution: DISABLED"
        )

    return "\n".join(lines)


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "anti_loop_policy": deepcopy(
            policy.ANTI_LOOP_POLICY
        ),
        "state": snapshot(),
    }
