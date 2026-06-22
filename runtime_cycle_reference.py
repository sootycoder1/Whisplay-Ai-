# =========================
# WHISPLAY RUNTIME CYCLE (ALIGNED REFERENCE)
# =========================

def runtime_cycle(input_event, STATE):
    """
    Aligned to system_controller_STAGE12010_DEV_MIC.py
    This reflects the REAL execution order.
    """

    # 1. STATE (owned by state_core)
    current_state = STATE

    # 2. EVENTS (runtime bus)
    event_packet = runtime_bus_STAGE7000(input_event)

    # 3. MODE HANDLING (controller responsibility)
    system_controller_handle_modes(event_packet, current_state)

    # 4. DEBUG / TRACE (non-blocking)
    debug_log(current_state, event_packet)

    # 5. MEMORY (context + history)
    memory_context = memory_engine_STAGE7500(current_state, event_packet)

    # 6. SAFETY (contract enforcement)
    safe_context = runtime_contract_STAGE6000(memory_context)

    # 7. STRATEGY (intent selection)
    strategy_output = goal_engine_STAGE8000(safe_context)

    # 8. REASONING (brain — Stage 150)
    decision_output = reasoning_engine_STAGE8500(strategy_output)

    # 9. ADAPTER (route to subsystems)
    routed_output = adapter_manager_STAGE9000(decision_output)

    # 10. ANALYSIS (final shaping / validation)
    final_output = analysis_core_STAGE11500(routed_output)

    # 11. STATE UPDATE (loop closure)
    STATE.update(final_output)

    return final_output


# =========================
# SYSTEM LOOP (HOW IT RUNS)
# =========================

def run_loop():
    """
    Represents how the controller keeps the system alive.
    """

    while STATE.get("running", False):

        # input comes from mic / keyboard / system
        input_event = get_next_input()

        # run full pipeline
        runtime_cycle(input_event, STATE)


# =========================
# NOTES
# =========================
# - This is a REFERENCE file only
# - Real execution lives in:
#   system_controller_STAGE12010_DEV_MIC.py
# - This file exists for clarity and alignment only
