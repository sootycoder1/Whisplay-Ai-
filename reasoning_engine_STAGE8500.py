# ============================================================
# REASONING ENGINE
# STAGE 8500
# Strategic reasoning + synthesis + adaptive cognition
# ============================================================

import time
import random
import threading


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "reasoning_engine"

ENGINE_STAGE = 8500


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "adaptive",
    "status": "online",
    "reasoning_cycles": 0,
    "analysis_count": 0,
    "synthesis_count": 0,
    "fallback_count": 0,
    "contradictions_detected": 0,
    "confidence": 0.5,
    "focus": 1.0,
    "pressure": 0.0,
    "stability": 1.0,
    "active_problem": None,
    "last_input": "",
    "last_output": "",
    "last_reasoning": "",
    "runtime_cycles": 0,
    "created": time.time(),
    "updated": time.time(),
}


# ============================================================
# REASONING MEMORY
# ============================================================

MEMORY = {
    "inputs": [],
    "outputs": [],
    "topics": [],
    "intents": [],
    "reasoning_paths": [],
    "contradictions": [],
    "runtime_events": [],
}


# ============================================================
# FLAGS
# ============================================================

FLAGS = {
    "adaptive_reasoning": True,
    "context_synthesis": True,
    "fallback_logic": True,
    "contradiction_detection": True,
    "pressure_awareness": True,
    "continuity_tracking": True,
    "goal_alignment": True,
    "response_shaping": True,
}


# ============================================================
# LOCK
# ============================================================

reasoning_lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def now():

    return time.time()


def clamp(
    value,
    minimum=0.0,
    maximum=1.0,
):

    return max(
        minimum,
        min(maximum, value)
    )


def remember(
    category,
    value,
    limit=30,
):

    if category not in MEMORY:
        return

    MEMORY[category].append(value)

    MEMORY[category] = (
        MEMORY[category][-limit:]
    )


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):

    t = text.lower()

    if any(
        x in t
        for x in [
            "status",
            "runtime",
            "health",
        ]
    ):
        return "status"

    if any(
        x in t
        for x in [
            "why",
            "reason",
            "explain",
        ]
    ):
        return "analysis"

    if any(
        x in t
        for x in [
            "how",
            "strategy",
            "improve",
        ]
    ):
        return "strategy"

    if any(
        x in t
        for x in [
            "stop",
            "shutdown",
        ]
    ):
        return "shutdown"

    return "general"


# ============================================================
# TOPIC DETECTION
# ============================================================

def detect_topic(text):

    t = text.lower()

    if "runtime" in t:
        return "runtime"

    if "speech" in t:
        return "speech"

    if "display" in t:
        return "display"

    if "memory" in t:
        return "memory"

    if "goal" in t:
        return "goal"

    return "general"


# ============================================================
# CONTRADICTION DETECTION
# ============================================================

def detect_contradiction(text):

    recent = MEMORY["inputs"][-5:]

    for item in recent:

        if (
            text.lower() == item.lower()
        ):

            STATE[
                "contradictions_detected"
            ] += 1

            remember(
                "contradictions",
                text,
            )

            return True

    return False


# ============================================================
# CONFIDENCE ENGINE
# ============================================================

def regulate_confidence():

    pressure = STATE["pressure"]

    confidence = (
        1.0 - (pressure * 0.5)
    )

    STATE["confidence"] = clamp(
        confidence
    )

    return STATE["confidence"]


# ============================================================
# REASONING PATH
# ============================================================

def build_reasoning_path(
    text,
    intent,
    topic,
):

    path = {
        "input": text,
        "intent": intent,
        "topic": topic,
        "confidence": STATE["confidence"],
        "timestamp": now(),
    }

    remember(
        "reasoning_paths",
        path,
    )

    STATE["last_reasoning"] = (
        f"{intent}:{topic}"
    )

    return path


# ============================================================
# RESPONSE SYNTHESIS
# ============================================================

def synthesize_response(
    text,
    intent,
    topic,
):

    STATE["synthesis_count"] += 1

    if intent == "status":

        return (
            "Runtime systems appear "
            "stable and operational."
        )

    if intent == "analysis":

        return (
            "Analysis suggests runtime "
            "coordination is improving."
        )

    if intent == "strategy":

        return (
            "Priority should remain on "
            "optimization and convergence."
        )

    if intent == "shutdown":

        return (
            "Shutdown intent detected."
        )

    fallback = [
        f"You said {text}",
        "Continue the reasoning.",
        "Expand on that idea.",
        "Interesting runtime input.",
        "Context processing active.",
    ]

    STATE["fallback_count"] += 1

    return random.choice(
        fallback
    )


# ============================================================
# MAIN REASONING
# ============================================================

def reason(text):

    with reasoning_lock:

        STATE["runtime_cycles"] += 1

        STATE["reasoning_cycles"] += 1

        STATE["analysis_count"] += 1

        STATE["last_input"] = text

        remember(
            "inputs",
            text,
        )

        intent = detect_intent(
            text
        )

        topic = detect_topic(
            text
        )

        remember(
            "topics",
            topic,
        )

        remember(
            "intents",
            intent,
        )

        detect_contradiction(
            text
        )

        regulate_confidence()

        build_reasoning_path(
            text,
            intent,
            topic,
        )

        response = synthesize_response(
            text,
            intent,
            topic,
        )

        STATE["last_output"] = response

        remember(
            "outputs",
            response,
        )

        STATE["updated"] = now()

        return {
            "response": response,
            "intent": intent,
            "topic": topic,
            "confidence": STATE["confidence"],
            "reasoning": STATE["last_reasoning"],
        }


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "memory": dict(MEMORY),
        "flags": dict(FLAGS),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return (
        "\n"
        "==============================\n"
        " REASONING ENGINE STAGE 8500\n"
        "==============================\n"
        f"STATUS:         {STATE['status']}\n"
        f"CONFIDENCE:     {STATE['confidence']:.2f}\n"
        f"REASONING:      {STATE['reasoning_cycles']}\n"
        f"ANALYSIS:       {STATE['analysis_count']}\n"
        f"SYNTHESIS:      {STATE['synthesis_count']}\n"
        f"FALLBACKS:      {STATE['fallback_count']}\n"
        f"CONTRADICTIONS: {STATE['contradictions_detected']}\n"
        f"LAST PATH:      {STATE['last_reasoning']}\n"
        f"CYCLES:         {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" REASONING ENGINE STAGE 8500")
    print("================================\n")

    tests = [
        "runtime status",
        "how do we optimize speech",
        "explain runtime pressure",
        "improve memory coordination",
        "runtime status",
    ]

    for text in tests:

        print(f"\n[INPUT] {text}")

        result = reason(text)

        print(result)

        print(status())

        time.sleep(1)

    print("\n[REASONING ENGINE COMPLETE]")

