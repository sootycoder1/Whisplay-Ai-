# ============================================================
# ANALYSIS CORE
# STAGE 11500
# Deep runtime interpretation + multi-pass cognition
# ============================================================

import time
import random
import threading


ENGINE_NAME = "analysis_core"

ENGINE_STAGE = 11500


STATE = {
    "mode": "adaptive",
    "status": "online",
    "analysis_cycles": 0,
    "multi_pass_cycles": 0,
    "pressure": 0.0,
    "confidence": 0.5,
    "stability": 1.0,
    "focus": 1.0,
    "active_analysis": None,
    "last_input": "",
    "last_intent": "",
    "last_topic": "",
    "last_conclusion": "",
    "last_strategy": "",
    "contradictions": 0,
    "runtime_cycles": 0,
    "created": time.time(),
    "updated": time.time(),
}


MEMORY = {
    "inputs": [],
    "intent_history": [],
    "topic_history": [],
    "analysis_history": [],
    "strategy_history": [],
    "conclusions": [],
    "runtime_events": [],
}


FLAGS = {
    "multi_pass_analysis": True,
    "pressure_awareness": True,
    "adaptive_reasoning": True,
    "continuity_tracking": True,
    "contradiction_detection": True,
    "strategic_synthesis": True,
    "confidence_regulation": True,
}


analysis_lock = threading.Lock()


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
    limit=40,
):

    if category not in MEMORY:
        return

    MEMORY[category].append(value)

    MEMORY[category] = (
        MEMORY[category][-limit:]
    )


# ============================================================
# PASS 1
# INTENT
# ============================================================

def analyze_intent(text):

    t = text.lower()

    if any(
        x in t
        for x in [
            "why",
            "explain",
            "reason",
        ]
    ):
        return "analysis"

    if any(
        x in t
        for x in [
            "optimize",
            "improve",
            "upgrade",
        ]
    ):
        return "optimization"

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
            "build",
            "create",
            "design",
        ]
    ):
        return "construction"

    return "general"


# ============================================================
# PASS 2
# TOPIC
# ============================================================

def analyze_topic(text):

    t = text.lower()

    if "speech" in t:
        return "speech"

    if "runtime" in t:
        return "runtime"

    if "display" in t:
        return "display"

    if "memory" in t:
        return "memory"

    if "reasoning" in t:
        return "reasoning"

    if "goal" in t:
        return "goal"

    return "general"


# ============================================================
# PASS 3
# PRESSURE
# ============================================================

def analyze_pressure():

    pressure = STATE["pressure"]

    if pressure > 0.8:
        return "critical"

    if pressure > 0.5:
        return "elevated"

    return "stable"


# ============================================================
# PASS 4
# CONTRADICTIONS
# ============================================================

def analyze_contradictions(text):

    recent = MEMORY["inputs"][-5:]

    contradictions = 0

    for item in recent:

        if text.lower() == item.lower():
            contradictions += 1

    STATE["contradictions"] += contradictions

    return contradictions


# ============================================================
# PASS 5
# STRATEGY
# ============================================================

def synthesize_strategy(
    intent,
    topic,
    pressure,
):

    if pressure == "critical":

        return (
            "reduce runtime load and "
            "simplify response generation"
        )

    if intent == "optimization":

        return (
            "prioritize convergence and "
            "runtime stabilization"
        )

    if topic == "speech":

        return (
            "reduce latency and maintain "
            "persistent speech flow"
        )

    if topic == "runtime":

        return (
            "maintain orchestration and "
            "pressure regulation"
        )

    return (
        "continue adaptive analysis "
        "and runtime synthesis"
    )


# ============================================================
# PASS 6
# CONCLUSION
# ============================================================

def conclude(
    intent,
    topic,
    strategy,
):

    hooks = [
        "Look.",
        "Alright.",
        "See,",
        "Honestly.",
        "Right.",
    ]

    hook = random.choice(hooks)

    return (
        f"{hook} analysis indicates "
        f"{topic} systems are aligned "
        f"with {intent} objectives. "
        f"Recommended strategy: "
        f"{strategy}."
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze(text):

    with analysis_lock:

        STATE["runtime_cycles"] += 1

        STATE["analysis_cycles"] += 1

        STATE["multi_pass_cycles"] += 1

        STATE["last_input"] = text

        remember(
            "inputs",
            text,
        )

        intent = analyze_intent(
            text
        )

        topic = analyze_topic(
            text
        )

        pressure = analyze_pressure()

        contradictions = (
            analyze_contradictions(
                text
            )
        )

        strategy = synthesize_strategy(
            intent,
            topic,
            pressure,
        )

        conclusion = conclude(
            intent,
            topic,
            strategy,
        )

        STATE["last_intent"] = intent
        STATE["last_topic"] = topic
        STATE["last_strategy"] = strategy
        STATE["last_conclusion"] = conclusion

        remember(
            "intent_history",
            intent,
        )

        remember(
            "topic_history",
            topic,
        )

        remember(
            "strategy_history",
            strategy,
        )

        remember(
            "conclusions",
            conclusion,
        )

        STATE["confidence"] = clamp(
            1.0 - (STATE["pressure"] * 0.4)
        )

        STATE["updated"] = now()

        return {
            "intent": intent,
            "topic": topic,
            "pressure": pressure,
            "contradictions": contradictions,
            "strategy": strategy,
            "conclusion": conclusion,
            "confidence": STATE[
                "confidence"
            ],
        }


def process(text=None):

    if not text:
        return None

    return analyze(text)


def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "memory": dict(MEMORY),
        "flags": dict(FLAGS),
    }


def status():

    return (
        "\n"
        "==============================\n"
        " ANALYSIS CORE STAGE 11500\n"
        "==============================\n"
        f"STATUS:         {STATE['status']}\n"
        f"CONFIDENCE:     {STATE['confidence']:.2f}\n"
        f"PRESSURE:       {STATE['pressure']:.2f}\n"
        f"ANALYSIS:       {STATE['analysis_cycles']}\n"
        f"MULTI PASS:     {STATE['multi_pass_cycles']}\n"
        f"CONTRADICTIONS: {STATE['contradictions']}\n"
        f"LAST INTENT:    {STATE['last_intent']}\n"
        f"LAST TOPIC:     {STATE['last_topic']}\n"
        f"CYCLES:         {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


if __name__ == "__main__":

    print("\n================================")
    print(" ANALYSIS CORE STAGE 11500")
    print("================================\n")

    tests = [
        "optimize runtime speech",
        "explain runtime pressure",
        "improve reasoning systems",
        "display runtime health",
        "optimize runtime speech",
    ]

    for text in tests:

        print(f"\n[INPUT] {text}")

        result = analyze(text)

        print(result)

        print(status())

        time.sleep(1)

    print("\n[ANALYSIS CORE COMPLETE]")
