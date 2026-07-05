# ============================================================
# WHISPLAY ASSISTANT DIAGNOSTICS
# STAGE 520 — READABLE RUNTIME DIAGNOSTICS CANDIDATE
# ============================================================

from copy import deepcopy
from time import time

import assistant_health_STAGE510_LOCKED as health
import assistant_runtime_STAGE500_LOCKED as runtime


ENGINE_NAME = "assistant_diagnostics"
ENGINE_STAGE = 520
ENGINE_VERSION = "520.0-candidate"


STATE = {
    "reports": 0,
    "healthy_reports": 0,
    "unhealthy_reports": 0,
    "last_result": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def build_report():
    STATE["reports"] += 1
    STATE["updated"] = now()

    health_result = health.run_checks()
    runtime_status = runtime.status()

    module_rows = []
    failed_modules = []

    for name, result in health_result["modules"].items():
        row = {
            "name": name,
            "ok": result["ok"],
            "engine": result["engine"],
            "expected_stage": result["expected_stage"],
            "actual_stage": result["actual_stage"],
            "required_callable": result["required_callable"],
            "interface_ok": result["interface_ok"],
        }

        module_rows.append(row)

        if not result["ok"]:
            failed_modules.append(name)

    active = health_result.get("runtime", {}).get("active", {})
    profile = active.get("profile") or {}
    context = active.get("context") or {}

    overall_ok = health_result.get("ok") is True

    if overall_ok:
        STATE["healthy_reports"] += 1
        STATE["last_result"] = "healthy"
    else:
        STATE["unhealthy_reports"] += 1
        STATE["last_result"] = "unhealthy"

    summary = (
        "Multi-actor runtime healthy."
        if overall_ok
        else "Multi-actor runtime unhealthy."
    )

    return {
        "ok": overall_ok,
        "summary": summary,
        "active_actor": {
            "id": profile.get("id", ""),
            "name": profile.get("name", ""),
            "role": profile.get("role", ""),
            "style_mode": profile.get("style_mode", ""),
        },
        "active_context": {
            "turns": context.get("turns", 0),
            "last_input": context.get("last_input", ""),
            "last_response": context.get("last_response", ""),
        },
        "modules": module_rows,
        "failed_modules": failed_modules,
        "runtime_state": deepcopy(
            runtime_status.get("state", {})
        ),
        "health_state": deepcopy(
            health_result.get("state", {})
        ),
        "state": snapshot(),
    }


def readable_report():
    report = build_report()

    actor = report["active_actor"]
    context = report["active_context"]

    lines = [
        "WHISPLAY MULTI-ACTOR DIAGNOSTICS",
        f"Health: {'PASS' if report['ok'] else 'FAIL'}",
        f"Summary: {report['summary']}",
        (
            "Active actor: "
            f"{actor['name']} ({actor['id']})"
        ),
        f"Role: {actor['role']}",
        f"Style: {actor['style_mode']}",
        f"Context turns: {context['turns']}",
        "Modules:",
    ]

    for module in report["modules"]:
        result = "PASS" if module["ok"] else "FAIL"

        lines.append(
            f"- {module['name']}: {result} "
            f"(stage {module['actual_stage']})"
        )

    if report["failed_modules"]:
        lines.append(
            "Failed modules: "
            + ", ".join(report["failed_modules"])
        )
    else:
        lines.append("Failed modules: none")

    return "\n".join(lines)


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "state": snapshot(),
    }
