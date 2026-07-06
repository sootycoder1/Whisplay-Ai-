# ============================================================
# WHISPLAY ASSISTANT RECOVERY VERIFY
# STAGE 580 — READ-ONLY RECOVERY VERIFICATION CANDIDATE
# ============================================================

from copy import deepcopy
from time import time


ENGINE_NAME = "assistant_recovery_verify"
ENGINE_STAGE = 580
ENGINE_VERSION = "580.0-candidate"

READ_ONLY = True
EXECUTION_ALLOWED = False


STATE = {
    "verifications": 0,
    "verified_results": 0,
    "failed_results": 0,
    "blocked_results": 0,
    "approval_results": 0,
    "same_fault_blocks": 0,
    "forbidden_action_blocks": 0,
    "execution_blocks": 0,
    "last_result": "",
    "updated": 0.0,
}


FORBIDDEN_ACTIONS = {
    "edit_locked_file",
    "replace_unknown_file",
    "change_hardware_state",
    "change_permissions",
    "execute_shell_command",
    "recursive_recovery",
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _as_list(value):
    return value if isinstance(value, list) else []


def _step_failed(step):
    status = str(step.get("status", "")).lower()
    if status in {"failed", "error", "blocked"}:
        return True

    if step.get("failed") is True:
        return True

    if step.get("ok") is False:
        return True

    return False


def _step_completed(step):
    if step.get("completed") is True:
        return True

    status = str(step.get("status", "")).lower()
    if status in {"done", "complete", "completed", "passed", "ok"}:
        return True

    return False


def _contains_forbidden_action(steps):
    found = []

    for step in steps:
        action = str(step.get("action", ""))
        if action in FORBIDDEN_ACTIONS:
            found.append(action)

    return found


def _execution_detected(plan, result, steps):
    if plan.get("execution_allowed") is True:
        return True

    if result.get("execution_allowed") is True:
        return True

    if result.get("executed") is True:
        return True

    for step in steps:
        if step.get("execution_allowed") is True:
            return True

        if step.get("executed") is True:
            return True

    return False


def verify(plan=None, result=None, current_fault=None):
    STATE["verifications"] += 1
    STATE["updated"] = now()

    plan = _as_dict(plan)
    result = _as_dict(result)
    current_fault = _as_dict(current_fault)

    steps = _as_list(
        result.get("steps")
        or plan.get("steps")
    )

    original_fingerprint = str(
        plan.get("fingerprint")
        or result.get("fingerprint")
        or ""
    )

    current_fingerprint = str(
        current_fault.get("fingerprint")
        or result.get("current_fingerprint")
        or ""
    )

    failed_steps = [
        step for step in steps
        if isinstance(step, dict) and _step_failed(step)
    ]

    incomplete_required_steps = [
        step for step in steps
        if isinstance(step, dict)
        and step.get("required", True) is True
        and not _step_completed(step)
        and not _step_failed(step)
    ]

    forbidden_actions = _contains_forbidden_action(
        [step for step in steps if isinstance(step, dict)]
    )

    same_fault_returned = (
        bool(original_fingerprint)
        and bool(current_fingerprint)
        and original_fingerprint == current_fingerprint
    )

    execution_detected = _execution_detected(
        plan,
        result,
        [step for step in steps if isinstance(step, dict)],
    )

    verification_passed = result.get("verification_passed")
    result_ok = result.get("ok")

    reasons = []

    if execution_detected:
        reasons.append("execution_detected")

    if forbidden_actions:
        reasons.append("forbidden_action_detected")

    if same_fault_returned:
        reasons.append("same_fault_returned")

    if failed_steps:
        reasons.append("failed_steps_detected")

    if incomplete_required_steps:
        reasons.append("required_steps_incomplete")

    if verification_passed is False:
        reasons.append("verification_reported_failed")

    if result_ok is False:
        reasons.append("result_reported_not_ok")

    if execution_detected or forbidden_actions or same_fault_returned:
        verdict = "blocked"
    elif reasons:
        verdict = "failed"
    elif plan.get("approval_required") is True:
        verdict = "needs_approval"
    else:
        verdict = "verified"

    if verdict == "verified":
        STATE["verified_results"] += 1
    elif verdict == "failed":
        STATE["failed_results"] += 1
    elif verdict == "blocked":
        STATE["blocked_results"] += 1
    elif verdict == "needs_approval":
        STATE["approval_results"] += 1

    if same_fault_returned:
        STATE["same_fault_blocks"] += 1

    if forbidden_actions:
        STATE["forbidden_action_blocks"] += 1

    if execution_detected:
        STATE["execution_blocks"] += 1

    STATE["last_result"] = verdict

    return {
        "ok": verdict in {"verified", "needs_approval"},
        "verdict": verdict,
        "stage": ENGINE_STAGE,
        "engine": ENGINE_NAME,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "recovery_verified": verdict == "verified",
        "approval_required": verdict == "needs_approval",
        "blocked": verdict == "blocked",
        "failed": verdict == "failed",
        "reasons": reasons,
        "failed_step_count": len(failed_steps),
        "incomplete_required_step_count": len(incomplete_required_steps),
        "forbidden_actions": forbidden_actions,
        "same_fault_returned": same_fault_returned,
        "execution_detected": execution_detected,
        "original_fingerprint": original_fingerprint,
        "current_fingerprint": current_fingerprint,
        "state": snapshot(),
    }


def status():
    return {
        "ok": True,
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "state": snapshot(),
    }


if __name__ == "__main__":
    demo_plan = {
        "ok": True,
        "fingerprint": "demo:fault:one",
        "approval_required": False,
        "execution_allowed": False,
        "steps": [
            {
                "step": 1,
                "action": "inspect_status",
                "completed": True,
                "execution_allowed": False,
            },
            {
                "step": 2,
                "action": "run_health_check",
                "completed": True,
                "execution_allowed": False,
            },
        ],
    }

    demo_result = {
        "ok": True,
        "verification_passed": True,
        "execution_allowed": False,
        "executed": False,
    }

    print(verify(demo_plan, demo_result))
