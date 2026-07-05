# ============================================================
# WHISPLAY ASSISTANT RECOVERY
# STAGE 540 — READ-ONLY RECOVERY RECOMMENDATIONS CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_faults_STAGE530_LOCKED as faults


ENGINE_NAME = "assistant_recovery"
ENGINE_STAGE = 540
ENGINE_VERSION = "540.0-candidate"

READ_ONLY = True
AUTOMATIC_REPAIR = False


RECOVERY_GUIDES = {
    "missing_engine": {
        "priority": "medium",
        "action": (
            "Inspect the module header and confirm ENGINE_NAME "
            "exists and matches the intended module."
        ),
        "verification": (
            "Re-run Stage 510 health checks after inspection."
        ),
    },
    "stage_mismatch": {
        "priority": "high",
        "action": (
            "Confirm the imported locked file is the intended "
            "stage and verify its ENGINE_STAGE value."
        ),
        "verification": (
            "Compile the file, then re-run Stage 510 health checks."
        ),
    },
    "missing_interface": {
        "priority": "high",
        "action": (
            "Inspect the named module for the required public "
            "callable without modifying any locked file."
        ),
        "verification": (
            "Confirm the callable exists, then re-run Stage 510."
        ),
    },
    "runtime_failure": {
        "priority": "critical",
        "action": (
            "Inspect Stage 500 runtime status, active actor, "
            "and Stage 510 runtime health output."
        ),
        "verification": (
            "Confirm a valid actor is active and the runtime "
            "reports healthy."
        ),
    },
    "unknown_failure": {
        "priority": "high",
        "action": (
            "Inspect Stage 510 and Stage 520 output for the named "
            "module before deciding on any recovery."
        ),
        "verification": (
            "Identify the exact fault before making changes."
        ),
    },
}


STATE = {
    "recommendations": 0,
    "healthy_results": 0,
    "fault_results": 0,
    "items_created": 0,
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def build_recommendation(fault):
    fault_type = str(fault.get("type") or "unknown_failure")
    guide = RECOVERY_GUIDES.get(
        fault_type,
        RECOVERY_GUIDES["unknown_failure"],
    )

    module = str(fault.get("module") or "unknown")

    return {
        "fault_type": fault_type,
        "module": module,
        "priority": guide["priority"],
        "location": fault.get("location", "unknown"),
        "observed": deepcopy(fault.get("actual")),
        "expected": deepcopy(fault.get("expected")),
        "recommended_action": guide["action"],
        "recovery_target": fault.get(
            "recovery_target",
            "manual inspection",
        ),
        "verification": guide["verification"],
        "automatic_action": False,
        "read_only": True,
    }


def recommend(report=None):
    STATE["recommendations"] += 1
    STATE["updated"] = now()

    classified = (
        deepcopy(report)
        if isinstance(report, dict) and "faults" in report
        else faults.classify_report(report)
    )

    recommendations = [
        build_recommendation(item)
        for item in classified.get("faults", [])
    ]

    healthy = (
        classified.get("ok") is True
        and not recommendations
    )

    if healthy:
        STATE["healthy_results"] += 1
        STATE["last_result"] = "no_recovery_needed"
    else:
        STATE["fault_results"] += 1
        STATE["items_created"] += len(recommendations)
        STATE["last_result"] = "recommendations_created"

    return {
        "ok": healthy,
        "read_only": READ_ONLY,
        "automatic_repair": AUTOMATIC_REPAIR,
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
        "failed_modules": deepcopy(
            classified.get("failed_modules", [])
        ),
        "state": snapshot(),
    }


def readable_recommendations(report=None):
    result = recommend(report)

    if result["ok"]:
        return (
            "No recovery recommendations required. "
            "Runtime is healthy."
        )

    lines = [
        "WHISPLAY READ-ONLY RECOVERY RECOMMENDATIONS",
        "Automatic repair: DISABLED",
        f"Recommendation count: {result['recommendation_count']}",
    ]

    for item in result["recommendations"]:
        lines.extend([
            (
                f"- [{item['priority'].upper()}] "
                f"{item['fault_type']} in {item['module']}"
            ),
            f"  Location: {item['location']}",
            f"  Expected: {item['expected']}",
            f"  Observed: {item['observed']}",
            (
                "  Recommended action: "
                f"{item['recommended_action']}"
            ),
            f"  Recovery target: {item['recovery_target']}",
            f"  Verification: {item['verification']}",
            "  Automatic action taken: NO",
        ])

    return "\n".join(lines)


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "read_only": READ_ONLY,
        "automatic_repair": AUTOMATIC_REPAIR,
        "supported_faults": sorted(RECOVERY_GUIDES),
        "state": snapshot(),
    }
