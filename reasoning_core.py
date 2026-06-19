# ============================================================
# REASONING CORE — STAGE 3600
# Runtime reasoning + analytical cognition layer
# ============================================================

import time
import random


STAGE = 3600

ENGINE_NAME = "REASONING_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# REASONING STATE
# ============================================================

REASONING = {
    "enabled": True,
    "mode": "balanced",
    "depth": 0.55,
    "confidence": 0.50,
    "ambiguity": 0.0,
    "pressure": 0.0,
    "last_input": "",
    "last_output": "",
    "last_path": "",
    "cycles": 0,
    "failures": 0,
    "last_reason_time": 0.0,
}


# ============================================================
# REASONING MODES
# ============================================================

MODES = {

    "fast": {
        "depth": 0.25,
        "exploration": 0.15,
        "verification": 0.20,
    },

    "balanced": {
        "depth": 0.55,
        "exploration": 0.42,
        "verification": 0.55,
    },

    "deep": {
        "depth": 0.90,
        "exploration": 0.72,
        "verification": 0.88,
    },

    "recovery": {
        "depth": 0.35,
        "exploration": 0.10,
        "verification": 0.92,
    },

    "guarded": {
        "depth": 0.42,
        "exploration": 0.05,
        "verification": 0.96,
    },
}


# ============================================================
# REASONING MEMORY
# ============================================================

THOUGHT_HISTORY = []

MAX_HISTORY = 300


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[REASONING] {message}")


def remember(event, details=None):

    THOUGHT_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(THOUGHT_HISTORY) > MAX_HISTORY:
        THOUGHT_HISTORY.pop(0)


def clean(text):

    return " ".join(
        str(text or "").strip().split()
    )


def clamp(value, low, high):

    return max(
        low,
        min(high, value),
    )


# ============================================================
# MODE CONTROL
# ============================================================

def set_mode(mode):

    if mode not in MODES:
        return False

    REASONING["mode"] = mode

    REASONING["depth"] = MODES[mode][
        "depth"
    ]

    remember("mode_change", {
        "mode": mode,
    })

    log(f"mode: {mode}")

    return mode


# ============================================================
# AUTO MODE
# ============================================================

def auto_mode(runtime_state=None):

    runtime_state = runtime_state or {}

    pressure = runtime_state.get(
        "pressure",
        0.0,
    )

    recovery = runtime_state.get(
        "recovery",
        False,
    )

    ambiguity = runtime_state.get(
        "ambiguity",
        0.0,
    )

    if recovery:
        return set_mode("recovery")

    if pressure >= 0.90:
        return set_mode("guarded")

    if ambiguity >= 0.72:
        return set_mode("deep")

    if pressure <= 0.20:
        return set_mode("deep")

    return set_mode("balanced")


# ============================================================
# INPUT ANALYSIS
# ============================================================

def analyze(text):

    t = clean(text).lower()

    profile = {
        "technical": 0.0,
        "complexity": 0.0,
        "emotion": 0.0,
        "ambiguity": 0.0,
        "risk": 0.0,
    }

    if any(w in t for w in [
        "runtime",
        "module",
        "system",
        "memory",
        "router",
        "state",
        "adapter",
    ]):
        profile["technical"] += 0.8

    if len(t.split()) >= 20:
        profile["complexity"] += 0.6

    if any(w in t for w in [
        "maybe",
        "idk",
        "unsure",
        "confused",
    ]):
        profile["ambiguity"] += 0.7

    if any(w in t for w in [
        "angry",
        "frustrated",
        "annoyed",
    ]):
        profile["emotion"] += 0.65

    if any(w in t for w in [
        "delete",
        "wipe",
        "shutdown",
        "override",
    ]):
        profile["risk"] += 0.8

    return profile


# ============================================================
# THOUGHT PATH
# ============================================================

def build_path(
    text,
    runtime_state=None,
):

    runtime_state = runtime_state or {}

    analysis = analyze(text)

    path = []

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    path.append(
        "input_analysis"
    )

    # --------------------------------------------------------
    # TECHNICAL
    # --------------------------------------------------------

    if analysis["technical"] >= 0.6:

        path.append(
            "technical_reasoning"
        )

    # --------------------------------------------------------
    # COMPLEXITY
    # --------------------------------------------------------

    if analysis["complexity"] >= 0.5:

        path.append(
            "deep_analysis"
        )

    # --------------------------------------------------------
    # AMBIGUITY
    # --------------------------------------------------------

    if analysis["ambiguity"] >= 0.5:

        path.append(
            "clarification_bias"
        )

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    if analysis["risk"] >= 0.5:

        path.append(
            "safety_validation"
        )

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    if runtime_state.get("recovery"):

        path.append(
            "recovery_reasoning"
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    path.append(
        "response_generation"
    )

    return path


# ============================================================
# CONFIDENCE
# ============================================================

def confidence(
    analysis,
    runtime_state=None,
):

    runtime_state = runtime_state or {}

    confidence_score = 0.55

    confidence_score += (
        analysis["technical"] * 0.15
    )

    confidence_score -= (
        analysis["ambiguity"] * 0.25
    )

    confidence_score -= (
        runtime_state.get(
            "pressure",
            0.0,
        ) * 0.20
    )

    confidence_score += (
        runtime_state.get(
            "stability",
            1.0,
        ) * 0.15
    )

    return round(
        clamp(
            confidence_score,
            0.0,
            1.0,
        ),
        3,
    )


# ============================================================
# REASON
# ============================================================

def reason(
    text,
    runtime_state=None,
):

    runtime_state = runtime_state or {}

    REASONING["cycles"] += 1

    REASONING["last_input"] = text

    REASONING["last_reason_time"] = now()

    auto_mode(runtime_state)

    analysis = analyze(text)

    thought_path = build_path(
        text,
        runtime_state,
    )

    confidence_score = confidence(
        analysis,
        runtime_state,
    )

    REASONING["confidence"] = (
        confidence_score
    )

    REASONING["ambiguity"] = (
        analysis["ambiguity"]
    )

    REASONING["pressure"] = runtime_state.get(
        "pressure",
        0.0,
    )

    REASONING["last_path"] = (
        " -> ".join(thought_path)
    )

    summary = {
        "technical": analysis[
            "technical"
        ] >= 0.5,

        "complex": analysis[
            "complexity"
        ] >= 0.5,

        "ambiguous": analysis[
            "ambiguity"
        ] >= 0.5,

        "risky": analysis[
            "risk"
        ] >= 0.5,
    }

    REASONING["last_output"] = str(
        summary
    )

    remember("reason", {
        "text": text[:120],
        "mode": REASONING["mode"],
        "confidence": confidence_score,
    })

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "mode": REASONING["mode"],
        "confidence": confidence_score,
        "analysis": analysis,
        "thought_path": thought_path,
        "summary": summary,
    }


# ============================================================
# PROCESS
# ============================================================

def process(
    text,
    runtime_state=None,
):

    return reason(
        text,
        runtime_state,
    )


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "reasoning": dict(
            REASONING
        ),
        "available_modes": list(
            MODES.keys()
        ),
        "history_size": len(
            THOUGHT_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def think(
    text,
    runtime_state=None,
):

    return process(
        text,
        runtime_state,
    )


def reasoning(
    text,
    runtime_state=None,
):

    return process(
        text,
        runtime_state,
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" REASONING CORE STAGE3600")
    print("================================\n")

    runtime_state = {
        "pressure": 0.32,
        "stability": 0.92,
        "ambiguity": 0.18,
    }

    print(
        process(
            "assistant analyze runtime recovery architecture",
            runtime_state,
        )
    )

    print(status())
