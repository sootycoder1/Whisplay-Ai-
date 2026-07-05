import json
import os
import re
import shutil
import time
from copy import deepcopy
from pathlib import Path

from brain.brain_cognitive_STAGE420_STATUS_INTENT_LOCKED import process as stage190_process
from brain.brain_cognitive_STAGE420_STATUS_INTENT_LOCKED import status as stage190_status


# ============================================================
# WHISPLAY STAGE 200 — OUTCOME-AWARE ADAPTIVE PLANNER
# ============================================================
#
# Stage 150 and Stage 190 remain authoritative and untouched.
# All memory and planning behaviour in this file is local to
# Stage 200.
#
# This file remains Stage 200 until its capability is proven
# sufficient to earn a later stage designation.
# ============================================================

MAX_HISTORY = 24
MAX_SUBJECT_EVENTS = 12

MEMORY_SCHEMA_VERSION = 1
MEMORY_DIRECTORY = Path.home() / ".whisplay" / "stage220"
MEMORY_FILE = MEMORY_DIRECTORY / "planner_memory.json"
MEMORY_BACKUP_FILE = MEMORY_DIRECTORY / "planner_memory.last_good.json"


PLANNER_MEMORY = {
    "last_input": None,
    "last_subject": None,
    "repeat_count": 0,
    "escalation_level": 0,
    "total_requests": 0,
    "last_outcome": "unknown",
    "last_plan_subject": None,
    "last_plan_level": 0,
    "last_plan_steps": [],
    "history": [],
    "subjects": {},
    "outcome_counts": {
        "success": 0,
        "failure": 0,
        "partial": 0,
        "not_attempted": 0,
        "unknown": 0,
    },
}

DEFAULT_PLANNER_MEMORY = deepcopy(PLANNER_MEMORY)


AUDIO_STEPS = {
    0: [
        ("audio_input", "Check microphone/input is working"),
        ("audio_recognition", "Verify recognition pipeline (Vosk / input adapter)"),
        ("audio_pipeline", "Confirm processing reaches the cognitive pipeline"),
        ("audio_output", "Test audio output device (Piper / ALSA)"),
    ],
    1: [
        ("audio_adapter_boundary", "Confirm microphone input reaches the input adapter"),
        ("audio_vosk_result", "Confirm Vosk returns recognized text"),
        ("audio_stage190_boundary", "Confirm recognized text reaches Stage 190"),
        ("audio_piper_isolation", "Test Piper separately from recognition"),
        ("audio_failure_boundary", "Record the first boundary where data disappears"),
    ],
    2: [
        ("audio_freeze", "Freeze the current runtime state before changing anything"),
        ("audio_direct_capture", "Test microphone capture outside the controller"),
        ("audio_saved_wav", "Test Vosk with a known saved WAV file"),
        ("audio_trace", "Trace adapter output into the cognitive pipeline"),
        ("audio_direct_output", "Test Piper and ALSA independently"),
        ("audio_compare_lock", "Compare the failure against the last working lock"),
        ("audio_single_change", "Change only the confirmed failing layer"),
    ],
}


DISPLAY_STEPS = {
    0: [
        ("display_trigger", "Check the render trigger is firing"),
        ("display_buffer", "Verify the display buffer is updating"),
        ("display_driver", "Confirm the SPI/display driver connection"),
        ("display_refresh", "Force one refresh cycle and test output"),
    ],
    1: [
        ("display_state_boundary", "Confirm the orchestrator receives the state update"),
        ("display_frame", "Confirm a new frame or buffer is produced"),
        ("display_render_boundary", "Verify the render call reaches the driver"),
        ("display_static_frame", "Run one forced static-frame test"),
        ("display_failure_layer", "Identify whether failure is state, render, driver, or SPI"),
    ],
    2: [
        ("display_freeze", "Freeze the runtime and preserve the working lock"),
        ("display_direct_driver", "Run the display driver with a static test image"),
        ("display_spi_scope", "Verify SPI remains restricted to display-only scope"),
        ("display_trace", "Trace state to orchestrator to buffer to driver"),
        ("display_compare_lock", "Compare the current paths against the last working backup"),
        ("display_component_test", "Test refresh, backlight, and frame transfer separately"),
        ("display_single_change", "Change only the confirmed failing layer"),
    ],
}


GENERAL_STEPS = {
    0: [
        ("general_isolate", "Identify the subsystem or layer involved"),
        ("general_reproduce", "Reproduce the issue with the smallest possible test"),
        ("general_boundary", "Find the first boundary where expected behaviour stops"),
        ("general_verify", "Verify that boundary before changing code"),
    ],
    1: [
        ("general_preserve", "Preserve the current working lock"),
        ("general_trace", "Trace input, state, processing, and output in order"),
        ("general_compare", "Compare the failing path with the last working state"),
        ("general_narrow", "Narrow the issue to one confirmed layer"),
        ("general_one_change", "Make only one controlled change"),
    ],
    2: [
        ("general_freeze", "Freeze the current runtime state"),
        ("general_minimal_test", "Build a minimal isolated reproduction"),
        ("general_instrument", "Capture evidence at every subsystem boundary"),
        ("general_known_good", "Substitute known-good input or output where possible"),
        ("general_root_cause", "Identify the root cause before modifying the runtime"),
        ("general_retest", "Retest the complete path after the single-layer repair"),
    ],
}


def _new_subject_memory():
    return {
        "requests": 0,
        "successes": 0,
        "failures": 0,
        "partial_results": 0,
        "completed_steps": [],
        "failed_steps": [],
        "events": [],
    }


def _normalize_input(text):
    if text is None:
        return ""

    normalized = str(text).strip().lower()
    normalized = re.sub(r"[^\w\s'-]", " ", normalized)
    return " ".join(normalized.split())


def _safe_subject(subject):
    normalized = _normalize_input(subject)

    if normalized:
        return normalized

    previous = PLANNER_MEMORY.get("last_subject")
    return previous if previous else "general"


def _subject_memory(subject):
    subject = _safe_subject(subject)

    if subject not in PLANNER_MEMORY["subjects"]:
        PLANNER_MEMORY["subjects"][subject] = _new_subject_memory()

    return PLANNER_MEMORY["subjects"][subject]


def _append_unique(values, item):
    if item and item not in values:
        values.append(item)


def _remove_value(values, item):
    while item in values:
        values.remove(item)


def _bounded_append(values, item, limit):
    values.append(item)

    if len(values) > limit:
        del values[:-limit]


def _record_event(event_type, subject, detail=None):
    event = {
        "type": event_type,
        "subject": _safe_subject(subject),
        "detail": detail,
        "request_number": PLANNER_MEMORY["total_requests"],
    }

    _bounded_append(PLANNER_MEMORY["history"], event, MAX_HISTORY)

    subject_state = _subject_memory(subject)
    _bounded_append(subject_state["events"], event, MAX_SUBJECT_EVENTS)


def _detect_step_numbers(normalized):
    numbers = []

    for match in re.findall(r"\bstep\s*(\d+)\b", normalized):
        number = int(match)

        if number > 0 and number not in numbers:
            numbers.append(number)

    return numbers


def _detect_outcome(text):
    normalized = _normalize_input(text)

    if not normalized:
        return "unknown", []

    step_numbers = _detect_step_numbers(normalized)

    numbered_partial = re.search(
        r"\bstep\s+\d+\s+(?:partly|partially)\s+worked\b",
        normalized,
    )
    numbered_failure = re.search(
        r"\bstep\s+\d+\s+(?:failed|fails|didn't work|did not work|still fails)\b",
        normalized,
    )
    numbered_success = re.search(
        r"\bstep\s+\d+\s+(?:worked|works|passed|succeeded|fixed it)\b",
        normalized,
    )

    if numbered_partial:
        return "partial", step_numbers

    if numbered_failure:
        return "failure", step_numbers

    if numbered_success:
        return "success", step_numbers

    success_phrases = (
        "that worked",
        "it worked",
        "working now",
        "fixed now",
        "that fixed it",
        "problem solved",
        "issue solved",
        "successful",
        "step worked",
    )

    partial_phrases = (
        "partly worked",
        "partially worked",
        "helped a bit",
        "some improvement",
        "better but",
        "works sometimes",
    )

    not_attempted_phrases = (
        "not tried",
        "not attempted",
        "haven't tried",
        "have not tried",
        "didn't try",
        "did not try",
    )

    failure_phrases = (
        "didn't work",
        "did not work",
        "still broken",
        "still not working",
        "already tried",
        "tried that",
        "same problem",
        "same issue",
        "still fails",
        "failed again",
        "step failed",
        "no change",
    )

    if any(phrase in normalized for phrase in partial_phrases):
        return "partial", step_numbers

    if any(phrase in normalized for phrase in not_attempted_phrases):
        return "not_attempted", step_numbers

    if any(phrase in normalized for phrase in failure_phrases):
        return "failure", step_numbers

    if any(phrase in normalized for phrase in success_phrases):
        return "success", step_numbers

    return "unknown", step_numbers


def _steps_from_numbers(step_numbers):
    last_steps = PLANNER_MEMORY.get("last_plan_steps", [])
    selected = []

    for number in step_numbers:
        index = number - 1

        if 0 <= index < len(last_steps):
            selected.append(last_steps[index])

    return selected


def _apply_outcome(outcome, subject, step_numbers):
    subject = _safe_subject(subject)
    subject_state = _subject_memory(subject)

    if outcome not in PLANNER_MEMORY["outcome_counts"]:
        outcome = "unknown"

    PLANNER_MEMORY["last_outcome"] = outcome
    PLANNER_MEMORY["outcome_counts"][outcome] += 1

    selected_steps = _steps_from_numbers(step_numbers)

    if not selected_steps:
        selected_steps = list(PLANNER_MEMORY.get("last_plan_steps", []))

    if outcome == "success":
        subject_state["successes"] += 1

        for step in selected_steps:
            step_id = step["id"]
            _append_unique(subject_state["completed_steps"], step_id)
            _remove_value(subject_state["failed_steps"], step_id)

        PLANNER_MEMORY["repeat_count"] = 0
        PLANNER_MEMORY["escalation_level"] = max(
            0,
            PLANNER_MEMORY["escalation_level"] - 1,
        )

    elif outcome == "failure":
        subject_state["failures"] += 1

        for step in selected_steps:
            step_id = step["id"]
            _append_unique(subject_state["failed_steps"], step_id)

        PLANNER_MEMORY["repeat_count"] += 1
        PLANNER_MEMORY["escalation_level"] = min(
            2,
            PLANNER_MEMORY["escalation_level"] + 1,
        )

    elif outcome == "partial":
        subject_state["partial_results"] += 1

        for step in selected_steps:
            step_id = step["id"]
            _append_unique(subject_state["completed_steps"], step_id)

        PLANNER_MEMORY["escalation_level"] = max(
            1,
            PLANNER_MEMORY["escalation_level"],
        )

    _record_event(
        "outcome",
        subject,
        {
            "outcome": outcome,
            "step_numbers": list(step_numbers),
            "affected_steps": [step["id"] for step in selected_steps],
        },
    )


def _update_repeat_memory(text, subject):
    normalized = _normalize_input(text)
    subject = _safe_subject(subject)

    same_input = (
        normalized != ""
        and normalized == PLANNER_MEMORY["last_input"]
    )

    same_subject = (
        subject != "general"
        and subject == PLANNER_MEMORY["last_subject"]
    )

    if same_input or same_subject:
        PLANNER_MEMORY["repeat_count"] += 1
    else:
        PLANNER_MEMORY["repeat_count"] = 0

    repeat_count = PLANNER_MEMORY["repeat_count"]

    if repeat_count >= 3:
        PLANNER_MEMORY["escalation_level"] = 2
    elif repeat_count >= 1:
        PLANNER_MEMORY["escalation_level"] = max(
            1,
            PLANNER_MEMORY["escalation_level"],
        )
    else:
        PLANNER_MEMORY["escalation_level"] = 0

    PLANNER_MEMORY["last_input"] = normalized
    PLANNER_MEMORY["last_subject"] = subject

    subject_state = _subject_memory(subject)
    subject_state["requests"] += 1


def _catalog_for_subject(subject):
    subject = _safe_subject(subject)

    if subject == "audio":
        return AUDIO_STEPS

    if subject == "display":
        return DISPLAY_STEPS

    return GENERAL_STEPS


def _plan_title(subject, level):
    subject = _safe_subject(subject)

    if subject == "audio":
        if level == 0:
            return "Audio fix plan"
        if level == 1:
            return "Audio boundary-isolation plan"
        return "Audio escalation plan"

    if subject == "display":
        if level == 0:
            return "Display fix plan"
        if level == 1:
            return "Display boundary-isolation plan"
        return "Display escalation plan"

    if level == 0:
        return "Step-by-step diagnostic plan"
    if level == 1:
        return "Narrowed diagnostic plan"
    return "Escalated root-cause plan"


def _select_steps(subject, level):
    subject = _safe_subject(subject)
    catalog = _catalog_for_subject(subject)
    subject_state = _subject_memory(subject)

    completed = set(subject_state["completed_steps"])
    failed = set(subject_state["failed_steps"])

    selected = []
    skipped = []

    for step_id, instruction in catalog[level]:
        reason = None

        if step_id in completed:
            reason = "completed"
        elif step_id in failed:
            reason = "previously_failed"

        if reason:
            skipped.append({
                "id": step_id,
                "instruction": instruction,
                "reason": reason,
            })
        else:
            selected.append({
                "id": step_id,
                "instruction": instruction,
            })

    # If every step at the current level has already been exhausted,
    # move upward once and try the deeper catalog.
    if not selected and level < 2:
        deeper_level = level + 1

        for step_id, instruction in catalog[deeper_level]:
            if step_id not in completed and step_id not in failed:
                selected.append({
                    "id": step_id,
                    "instruction": instruction,
                })

        if selected:
            level = deeper_level
            PLANNER_MEMORY["escalation_level"] = max(
                PLANNER_MEMORY["escalation_level"],
                deeper_level,
            )

    # Final bounded fallback prevents an empty response.
    if not selected:
        selected = [{
            "id": "manual_root_cause_review",
            "instruction": (
                "Review the accumulated evidence and identify a new test "
                "that does not repeat any exhausted step"
            ),
        }]

    return level, selected, skipped


def _build_plan(subject):
    subject = _safe_subject(subject)
    level = PLANNER_MEMORY["escalation_level"]

    level, selected, skipped = _select_steps(subject, level)
    title = _plan_title(subject, level)

    lines = [f"{title}:"]

    for number, step in enumerate(selected, start=1):
        lines.append(f"{number}. {step['instruction']}")

    if skipped:
        skipped_completed = sum(
            1 for step in skipped if step["reason"] == "completed"
        )
        skipped_failed = sum(
            1 for step in skipped if step["reason"] == "previously_failed"
        )

        lines.append(
            "Skipped from earlier attempts: "
            f"{skipped_completed} completed, "
            f"{skipped_failed} previously failed."
        )

    PLANNER_MEMORY["last_plan_subject"] = subject
    PLANNER_MEMORY["last_plan_level"] = level
    PLANNER_MEMORY["last_plan_steps"] = deepcopy(selected)

    _record_event(
        "plan",
        subject,
        {
            "level": level,
            "step_ids": [step["id"] for step in selected],
            "skipped_ids": [step["id"] for step in skipped],
        },
    )

    return "\n".join(lines), selected, skipped


def _is_reset_request(normalized):
    reset_phrases = (
        "reset planner",
        "reset planner memory",
        "clear planner",
        "clear planner memory",
        "forget diagnostic history",
    )

    return normalized in reset_phrases


def _is_status_request(normalized):
    return normalized in (
        "planner status",
        "plannerstatus",
        "plan status",
        "status plan",
        "the status",
        "planner state",
        "diagnostic status",
        "stage 200 status",
        "stage 220 status",
    )


def _is_planning_request(normalized, outcome):
    planning_terms = (
        "how",
        "fix",
        "repair",
        "solve",
        "diagnose",
        "broken",
        "not working",
        "problem",
        "issue",
        "fails",
        "failure",
    )

    if outcome in ("failure", "partial"):
        return True

    return any(term in normalized for term in planning_terms)


def reset(subject=None):
    if subject is None:
        PLANNER_MEMORY.update({
            "last_input": None,
            "last_subject": None,
            "repeat_count": 0,
            "escalation_level": 0,
            "total_requests": 0,
            "last_outcome": "unknown",
            "last_plan_subject": None,
            "last_plan_level": 0,
            "last_plan_steps": [],
            "history": [],
            "subjects": {},
            "outcome_counts": {
                "success": 0,
                "failure": 0,
                "partial": 0,
                "not_attempted": 0,
                "unknown": 0,
            },
        })

        return {
            "reset": "all",
            "ok": True,
        }

    subject = _safe_subject(subject)
    PLANNER_MEMORY["subjects"].pop(subject, None)

    if PLANNER_MEMORY["last_subject"] == subject:
        PLANNER_MEMORY["last_input"] = None
        PLANNER_MEMORY["last_subject"] = None
        PLANNER_MEMORY["repeat_count"] = 0
        PLANNER_MEMORY["escalation_level"] = 0
        PLANNER_MEMORY["last_plan_subject"] = None
        PLANNER_MEMORY["last_plan_steps"] = []

    return {
        "reset": subject,
        "ok": True,
    }


def _planner_snapshot(subject=None):
    subject = _safe_subject(subject)
    subject_state = deepcopy(
        PLANNER_MEMORY["subjects"].get(subject, _new_subject_memory())
    )

    return {
        "subject": subject,
        "repeat_count": PLANNER_MEMORY["repeat_count"],
        "escalation_level": PLANNER_MEMORY["escalation_level"],
        "total_requests": PLANNER_MEMORY["total_requests"],
        "last_outcome": PLANNER_MEMORY["last_outcome"],
        "last_plan_level": PLANNER_MEMORY["last_plan_level"],
        "last_plan_steps": deepcopy(PLANNER_MEMORY["last_plan_steps"]),
        "subject_memory": subject_state,
        "outcome_counts": deepcopy(PLANNER_MEMORY["outcome_counts"]),
        "history_size": len(PLANNER_MEMORY["history"]),
    }


def process(text):
    original_text = "" if text is None else str(text)
    normalized = _normalize_input(original_text)

    if _is_reset_request(normalized):
        reset_result = reset()
        persistence_result = clear_persistent_memory()

        return {
            "response": "Stage 200 planner memory has been reset.",
            "context": {},
            "planner": {
                "reset": reset_result,
                "persistence": persistence_result,
                "subject": "general",
                "repeat_count": 0,
                "escalation_level": 0,
                "total_requests": 0,
            },
        }

    try:
        base = stage190_process(original_text)
    except Exception as exc:
        base = {
            "response": "",
            "stage190_error": f"{type(exc).__name__}: {exc}",
        }

    try:
        ctx = stage190_status()
    except Exception as exc:
        ctx = {
            "stage190_status_error": f"{type(exc).__name__}: {exc}",
        }

    if not isinstance(base, dict):
        base = {"response": str(base)}

    if not isinstance(ctx, dict):
        ctx = {}

    response = base.get("response", "")
    subject = _safe_subject(ctx.get("active_subject"))

    if _is_status_request(normalized):
        response = (
            f"Planner status: subject {subject}, "
            f"repeat count {PLANNER_MEMORY['repeat_count']}, "
            f"escalation level {PLANNER_MEMORY['escalation_level']}, "
            f"last outcome {PLANNER_MEMORY['last_outcome']}."
        )

        planner_data = _planner_snapshot(subject)
        planner_data["detected_outcome"] = "unknown"
        planner_data["detected_step_numbers"] = []
        planner_data["selected_steps"] = []
        planner_data["skipped_steps"] = []
        planner_data["persistence"] = {
            "ok": True,
            "saved": False,
            "reason": "read_only_status",
        }

        return {
            "response": response,
            "context": ctx,
            "planner": planner_data,
        }

    PLANNER_MEMORY["total_requests"] += 1

    outcome, step_numbers = _detect_outcome(original_text)

    _update_repeat_memory(original_text, subject)

    if outcome != "unknown":
        _apply_outcome(outcome, subject, step_numbers)

    selected_steps = []
    skipped_steps = []

    if outcome == "success" and not _is_planning_request(normalized, outcome):
        response = (
            "Good — that result is recorded as successful. "
            "The completed diagnostic step will not be recommended again "
            "for this subject."
        )

    elif outcome == "not_attempted" and not _is_planning_request(normalized, outcome):
        response = (
            "Understood. That step remains untested and has not been marked "
            "as either successful or failed."
        )

    elif _is_planning_request(normalized, outcome):
        response, selected_steps, skipped_steps = _build_plan(subject)

    planner_data = _planner_snapshot(subject)
    planner_data["detected_outcome"] = outcome
    planner_data["detected_step_numbers"] = step_numbers
    planner_data["selected_steps"] = deepcopy(selected_steps)
    planner_data["skipped_steps"] = deepcopy(skipped_steps)

    if "stage190_error" in base:
        planner_data["stage190_error"] = base["stage190_error"]

    if "stage190_status_error" in ctx:
        planner_data["stage190_status_error"] = ctx["stage190_status_error"]

    planner_data["persistence"] = save_memory()

    return {
        "response": response,
        "intent": base.get(
            "intent",
            ctx.get("last_intent", "conversation"),
        ),
        "action": base.get(
            "action",
            ctx.get("last_action", "conversation"),
        ),
        "context": ctx,
        "planner": planner_data,
    }


def status():
    return deepcopy(PLANNER_MEMORY)


# ============================================================
# STAGE 220 — PERSISTENT PLANNER MEMORY
# ============================================================

def _bounded_memory_copy(memory):
    bounded = deepcopy(memory)

    history = bounded.get("history")
    if not isinstance(history, list):
        history = []

    bounded["history"] = history[-MAX_HISTORY:]

    subjects = bounded.get("subjects")
    if not isinstance(subjects, dict):
        subjects = {}

    clean_subjects = {}

    for subject, subject_state in subjects.items():
        if not isinstance(subject_state, dict):
            continue

        clean_state = deepcopy(subject_state)

        events = clean_state.get("events")
        if not isinstance(events, list):
            events = []

        clean_state["events"] = events[-MAX_SUBJECT_EVENTS:]

        for key in ("completed_steps", "failed_steps"):
            values = clean_state.get(key)

            if not isinstance(values, list):
                values = []

            clean_state[key] = list(dict.fromkeys(values))

        clean_subjects[str(subject)] = clean_state

    bounded["subjects"] = clean_subjects

    return bounded


def _validate_loaded_memory(candidate):
    if not isinstance(candidate, dict):
        raise ValueError("planner memory is not a dictionary")

    restored = deepcopy(DEFAULT_PLANNER_MEMORY)

    scalar_keys = (
        "last_input",
        "last_subject",
        "repeat_count",
        "escalation_level",
        "total_requests",
        "last_outcome",
        "last_plan_subject",
        "last_plan_level",
    )

    for key in scalar_keys:
        if key in candidate:
            restored[key] = candidate[key]

    for key in (
        "last_plan_steps",
        "history",
        "subjects",
        "outcome_counts",
    ):
        value = candidate.get(key)

        if isinstance(value, type(restored[key])):
            restored[key] = deepcopy(value)

    if not isinstance(restored["repeat_count"], int):
        restored["repeat_count"] = 0

    if not isinstance(restored["escalation_level"], int):
        restored["escalation_level"] = 0

    if not isinstance(restored["total_requests"], int):
        restored["total_requests"] = 0

    restored["repeat_count"] = max(0, restored["repeat_count"])
    restored["escalation_level"] = min(
        2,
        max(0, restored["escalation_level"]),
    )
    restored["total_requests"] = max(0, restored["total_requests"])

    return _bounded_memory_copy(restored)


def _persistence_payload():
    return {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "saved_at_unix": int(time.time()),
        "planner_memory": _bounded_memory_copy(PLANNER_MEMORY),
    }


def save_memory(path=None):
    memory_path = Path(path) if path is not None else MEMORY_FILE
    backup_path = (
        memory_path.with_name(memory_path.name + ".last_good")
        if path is not None
        else MEMORY_BACKUP_FILE
    )

    temporary_path = memory_path.with_name(
        f".{memory_path.name}.tmp.{os.getpid()}"
    )

    try:
        memory_path.parent.mkdir(parents=True, exist_ok=True)

        payload = _persistence_payload()

        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(
                payload,
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        if memory_path.exists():
            shutil.copy2(memory_path, backup_path)

        os.replace(temporary_path, memory_path)

        return {
            "ok": True,
            "action": "saved",
            "path": str(memory_path),
            "schema_version": MEMORY_SCHEMA_VERSION,
        }

    except Exception as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except Exception:
            pass

        return {
            "ok": False,
            "action": "save_failed",
            "path": str(memory_path),
            "error": f"{type(exc).__name__}: {exc}",
        }


def _quarantine_corrupt_file(memory_path):
    stamp = time.strftime("%Y%m%d_%H%M%S")
    corrupt_path = memory_path.with_name(
        f"{memory_path.name}.corrupt.{stamp}"
    )

    try:
        memory_path.replace(corrupt_path)
        return str(corrupt_path)
    except Exception:
        return None


def load_memory(path=None):
    memory_path = Path(path) if path is not None else MEMORY_FILE

    if not memory_path.exists():
        return {
            "ok": True,
            "action": "defaults",
            "reason": "memory_file_missing",
            "path": str(memory_path),
        }

    try:
        with memory_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if not isinstance(payload, dict):
            raise ValueError("persistence payload is not a dictionary")

        schema_version = payload.get("schema_version")

        if schema_version != MEMORY_SCHEMA_VERSION:
            raise ValueError(
                "unsupported memory schema "
                f"{schema_version!r}; expected "
                f"{MEMORY_SCHEMA_VERSION}"
            )

        candidate = payload.get("planner_memory")
        restored = _validate_loaded_memory(candidate)

        PLANNER_MEMORY.clear()
        PLANNER_MEMORY.update(restored)

        return {
            "ok": True,
            "action": "loaded",
            "path": str(memory_path),
            "schema_version": schema_version,
        }

    except Exception as exc:
        quarantined_path = _quarantine_corrupt_file(memory_path)

        PLANNER_MEMORY.clear()
        PLANNER_MEMORY.update(deepcopy(DEFAULT_PLANNER_MEMORY))

        return {
            "ok": False,
            "action": "corrupt_fallback",
            "path": str(memory_path),
            "quarantined_path": quarantined_path,
            "error": f"{type(exc).__name__}: {exc}",
        }


def clear_persistent_memory(path=None):
    memory_path = Path(path) if path is not None else MEMORY_FILE
    backup_path = (
        memory_path.with_name(memory_path.name + ".last_good")
        if path is not None
        else MEMORY_BACKUP_FILE
    )

    removed = []

    for candidate in (memory_path, backup_path):
        try:
            if candidate.exists():
                candidate.unlink()
                removed.append(str(candidate))
        except Exception as exc:
            return {
                "ok": False,
                "action": "clear_failed",
                "error": f"{type(exc).__name__}: {exc}",
                "removed": removed,
            }

    return {
        "ok": True,
        "action": "cleared",
        "removed": removed,
    }


def persistence_status():
    return {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "memory_path": str(MEMORY_FILE),
        "backup_path": str(MEMORY_BACKUP_FILE),
        "memory_exists": MEMORY_FILE.exists(),
        "backup_exists": MEMORY_BACKUP_FILE.exists(),
        "history_size": len(PLANNER_MEMORY.get("history", [])),
        "subject_count": len(PLANNER_MEMORY.get("subjects", {})),
    }


PERSISTENCE_LOAD_RESULT = load_memory()
