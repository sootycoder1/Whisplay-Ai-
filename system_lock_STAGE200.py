# ============================================================
# WHISPLAY SYSTEM LOCK — STAGE 200 (CAUTION MODE)
# Advisory only — does NOT block execution
# ============================================================

LOCKED_FILES = {
    "runtime_contract_STAGE6000.py": "LAW_LAYER",
    "runtime_bus_STAGE7000.py": "TRANSPORT_LAYER",
    "state_core.py": "TRUTH_LAYER",
}

LOCK_SEVERITY = {
    "LAW_LAYER": "CRITICAL",
    "TRANSPORT_LAYER": "HIGH",
    "TRUTH_LAYER": "HIGH",
}


def is_locked_file(filename: str) -> bool:
    return filename in LOCKED_FILES


def lock_warning(filename: str, action: str):
    """
    Advisory system — never blocks, only warns
    """

    if not is_locked_file(filename):
        return {"ok": True, "warning": None}

    layer = LOCKED_FILES[filename]
    severity = LOCK_SEVERITY.get(layer, "UNKNOWN")

    return {
        "ok": True,
        "warning": {
            "file": filename,
            "layer": layer,
            "severity": severity,
            "action": action,
            "message": f"Modifying {layer} may destabilize system architecture",
        }
    }


def system_lock_status():
    return {
        "mode": "advisory",
        "locked_files": LOCKED_FILES,
        "severity": LOCK_SEVERITY,
        "stage": 200,
    }
