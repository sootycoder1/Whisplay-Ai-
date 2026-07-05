# ============================================================
# WHISPLAY ASSISTANT RECOVERY POLICY
# STAGE 560 — CONTROLLED RECOVERY ACTION POLICY CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_recovery_gate_STAGE550_LOCKED as recovery_gate


ENGINE_NAME = "assistant_recovery_policy"
ENGINE_STAGE = 560
ENGINE_VERSION = "560.0-candidate"

READ_ONLY = True
EXECUTION_ALLOWED = False


POLICY_LEVELS = {
    "auto_safe",
    "approval_required",
    "forbidden",
}


ANTI_LOOP_POLICY = {
    "max_recovery_attempts": 1,
    "max_rollback_attempts": 1,
    "cooldown_seconds": 30,
    "recursive_recovery_allowed": False,
    "same_fault_retry_allowed": False,
    "block_after_failed_attempt": True,
    "user_approval_after_failure": True,
}


ACTION_POLICY = {
    "inspect_status": {
        "level": "auto_safe",
        "description": (
            "Read runtime, health, diagnostic, or state status."
        ),
    },
    "run_health_check": {
        "level": "auto_safe",
        "description": (
            "Run existing read-only health checks."
        ),
    },
    "run_diagnostics": {
        "level": "auto_safe",
        "description": (
            "Build read-only diagnostic reports."
        ),
    },
    "verify_locked_file": {
        "level": "auto_safe",
        "description": (
            "Compile, compare, or inspect a known locked file."
        ),
    },
    "restart_worker": {
        "level": "approval_required",
        "description": (
            "Restart a known non-hardware worker after approval."
        ),
    },
    "reload_locked_module": {
        "level": "approval_required",
        "description": (
            "Reload a verified locked software module."
        ),
    },
    "restore_verified_snapshot": {
        "level": "approval_required",
        "description": (
            "Restore a verified known-good software snapshot."
        ),
    },
    "clear_temporary_runtime_state": {
        "level": "approval_required",
        "description": (
            "Clear temporary runtime state without altering locks."
        ),
    },
    "edit_locked_file": {
        "level": "forbidden",
        "description": (
            "Locked files must never be edited automatically."
        ),
    },
    "replace_unknown_file": {
        "level": "forbidden",
        "description": (
            "Unknown or unverified files must not be replaced."
        ),
    },
    "change_hardware_state": {
        "level": "forbidden",
        "description": (
            "Recovery cannot control GPIO, SPI, or hardware."
        ),
    },
    "change_permissions": {
        "level": "forbidden",
        "description": (
            "Recovery cannot alter user or system permissions."
        ),
    },
    "execute_shell_command": {
        "level": "forbidden",
        "description": (
            "Arbitrary shell execution is not allowed."
        ),
    },
    "recursive_recovery": {
        "level": "forbidden",
        "description": (
            "A recovery process must never start another recovery."
        ),
    },
}


FAULT_ACTIONS = {
    "missing_engine": [
        "inspect_status",
        "verify_locked_file",
    ],
    "stage_mismatch": [
        "inspect_status",
        "verify_locked_file",
    ],
    "missing_interface": [
        "inspect_status",
        "verify_locked_file",
    ],
    "runtime_failure": [
        "inspect_status",
        "run_health_check",
        "run_diagnostics",
        "restart_worker",
        "reload_locked_module",
        "clear_temporary_runtime_state",
    ],
    "unknown_failure": [
        "inspect_status",
        "run_health_check",
        "run_diagnostics",
    ],
}


STATE = {
    "evaluations": 0,
    "allowed_results": 0,
    "approval_results": 0,
    "forbidden_results": 0,
    "unknown_actions": 0,
    "loop_blocks": 0,
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def fault_fingerprint(fault_type, module, location=""):
    return "|".join([
        str(fault_type or "unknown_failure"),
        str(module or "unknown"),
        str(location or "unknown"),
    ])


def anti_loop_check(
    fingerprint,
    previous_fingerprint="",
    recovery_attempts=0,
    rollback_attempts=0,
    recovery_active=False,
):
    reasons = []

    if recovery_active:
        reasons.append("recovery_already_active")

    if (
        previous_fingerprint
        and fingerprint == previous_fingerprint
        and recovery_attempts > 0
    ):
        reasons.append("same_fault_repeated")

    if recovery_attempts >= ANTI_LOOP_POLICY[
        "max_recovery_attempts"
    ]:
        reasons.append("recovery_attempt_limit_reached")

    if rollback_attempts >= ANTI_LOOP_POLICY[
        "max_rollback_attempts"
    ]:
        reasons.append("rollback_attempt_limit_reached")

    blocked = bool(reasons)

    if blocked:
        STATE["loop_blocks"] += 1

    return {
        "ok": not blocked,
        "blocked": blocked,
        "fingerprint": fingerprint,
        "reasons": reasons,
        "next_decision": (
            "blocked"
            if blocked
            else "continue_policy_evaluation"
        ),
        "user_approval_required": blocked,
        "recursive_recovery_allowed": False,
        "same_fault_retry_allowed": False,
        "read_only": True,
    }


def action_policy(action):
    action_name = str(action or "")
    policy = ACTION_POLICY.get(action_name)

    if policy is None:
        STATE["unknown_actions"] += 1

        return {
            "action": action_name,
            "known": False,
            "level": "forbidden",
            "description": "Unknown recovery actions are forbidden.",
            "execution_allowed": False,
            "approval_required": False,
            "read_only": True,
        }

    level = policy["level"]

    return {
        "action": action_name,
        "known": True,
        "level": level,
        "description": policy["description"],
        "execution_allowed": False,
        "approval_required": level == "approval_required",
        "read_only": True,
    }


def evaluate_action(action):
    STATE["evaluations"] += 1
    STATE["updated"] = now()

    result = action_policy(action)
    level = result["level"]

    if level == "auto_safe":
        STATE["allowed_results"] += 1
        STATE["last_result"] = "auto_safe"
    elif level == "approval_required":
        STATE["approval_results"] += 1
        STATE["last_result"] = "approval_required"
    else:
        STATE["forbidden_results"] += 1
        STATE["last_result"] = "forbidden"

    result["state"] = snapshot()

    return result


def policy_for_fault(fault_type):
    name = str(fault_type or "unknown_failure")

    actions = FAULT_ACTIONS.get(
        name,
        FAULT_ACTIONS["unknown_failure"],
    )

    return {
        "fault_type": name,
        "actions": [
            action_policy(action)
            for action in actions
        ],
        "anti_loop_policy": deepcopy(ANTI_LOOP_POLICY),
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
    }


def evaluate_gate(report=None):
    gate_result = (
        deepcopy(report)
        if isinstance(report, dict)
        and "decisions" in report
        else recovery_gate.evaluate(report)
    )

    policies = []

    for decision in gate_result.get("decisions", []):
        fault_type = decision.get(
            "fault_type",
            "unknown_failure",
        )

        policies.append(
            policy_for_fault(fault_type)
        )

    return {
        "ok": gate_result.get("ok") is True,
        "overall_decision": gate_result.get(
            "overall_decision",
            "blocked",
        ),
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "policy_count": len(policies),
        "policies": policies,
        "anti_loop_policy": deepcopy(ANTI_LOOP_POLICY),
        "state": snapshot(),
    }


def readable_policy(report=None):
    result = evaluate_gate(report)

    if result["ok"]:
        return "Recovery policy: no recovery action required."

    lines = [
        "WHISPLAY RECOVERY ACTION POLICY",
        f"Gate decision: {result['overall_decision'].upper()}",
        "Execution allowed: NO",
        "Recursive recovery: FORBIDDEN",
        "Same-fault retry: FORBIDDEN",
        (
            "Maximum recovery attempts: "
            f"{ANTI_LOOP_POLICY['max_recovery_attempts']}"
        ),
        (
            "Maximum rollback attempts: "
            f"{ANTI_LOOP_POLICY['max_rollback_attempts']}"
        ),
        f"Policy count: {result['policy_count']}",
    ]

    for policy in result["policies"]:
        lines.append(
            f"- Fault: {policy['fault_type']}"
        )

        for item in policy["actions"]:
            lines.append(
                f"  {item['action']}: "
                f"{item['level'].upper()}"
            )

    return "\n".join(lines)


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "read_only": READ_ONLY,
        "execution_allowed": EXECUTION_ALLOWED,
        "policy_levels": sorted(POLICY_LEVELS),
        "actions": deepcopy(ACTION_POLICY),
        "fault_actions": deepcopy(FAULT_ACTIONS),
        "anti_loop_policy": deepcopy(ANTI_LOOP_POLICY),
        "state": snapshot(),
    }
