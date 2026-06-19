# ============================================================
# CONTEXT MANAGER
# STAGE 6500
# Runtime context synthesis + continuity engine
# ============================================================

import time
import threading


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "context_manager"

ENGINE_STAGE = 6500


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "adaptive",
    "active_context": "general",
    "conversation_depth": 0,
    "continuity_score": 1.0,
    "pressure": 0.0,
    "focus": 1.0,
    "last_input": "",
    "last_topic": "general",
    "last_intent": "general",
    "context_switches": 0,
    "runtime_cycles": 0,
    "created": time.time(),
    "updated": time.time(),
}


# ============================================================
# CONTEXT MEMORY
# ============================================================

CONTEXT = {
    "recent_inputs": [],
    "recent_topics": [],
    "recent_intents": [],
    "recent_contexts": [],
    "runtime_events": [],
}


# ============================================================
# FLAGS
# ============================================================

FLAGS = {
    "context_tracking": True,
    "continuity_tracking": True,
    "adaptive_focus": True,
    "pressure_awareness": True,
    "topic_memory": True,
    "intent_memory": True,
}


# ============================================================
# LOCK
# ============================================================

context_lock = threading.Lock()


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


# ============================================================
# MEMORY
# ============================================================

def remember(
    category,
    value,
    limit=20,
):

    if category not in CONTEXT:
        return

    CONTEXT[category].append(value)

    CONTEXT[category] = (
        CONTEXT[category][-limit:]
    )


# ============================================================
# TOPIC DETECTION
# ============================================================

def detect_topic(text):

    t = text.lower()

    if any(
        x in t
        for x in [
            "music",
            "song",
            "audio",
        ]
    ):
        return "music"

    if any(
        x in t
        for x in [
            "runtime",
            "optimizer",
            "system",
        ]
    ):
        return "runtime"

    if any(
        x in t
        for x in [
            "display",
            "screen",
            "ui",
        ]
    ):
        return "display"

    if any(
        x in t
        for x in [
            "voice",
            "speech",
            "piper",
        ]
    ):
        return "speech"

    return "general"


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):

    t = text.lower()

    if any(
        x in t
        for x in [
            "status",
            "health",
            "runtime",
        ]
    ):
        return "status"

    if any(
        x in t
        for x in [
            "stop",
            "shutdown",
            "exit",
        ]
    ):
        return "shutdown"

    if any(
        x in t
        for x in [
            "who are you",
            "your name",
        ]
    ):
        return "identity"

    return "general"


# ============================================================
# CONTINUITY ENGINE
# ============================================================

def update_continuity(topic):

    previous = STATE["last_topic"]

    if topic != previous:

        STATE["context_switches"] += 1

        continuity = (
            STATE["continuity_score"] - 0.08
        )

    else:

        continuity = (
            STATE["continuity_score"] + 0.03
        )

    STATE["continuity_score"] = clamp(
        continuity
    )

    return STATE["continuity_score"]


# ============================================================
# FOCUS REGULATION
# ============================================================

def regulate_focus():

    switches = STATE["context_switches"]

    focus = (
        1.0 - (switches * 0.03)
    )

    STATE["focus"] = clamp(focus)

    return STATE["focus"]


# ============================================================
# CONTEXT SYNTHESIS
# ============================================================

def synthesize_context(text):

    with context_lock:

        STATE["runtime_cycles"] += 1

        STATE["last_input"] = str(text)

        remember(
            "recent_inputs",
            text,
        )

        topic = detect_topic(text)

        intent = detect_intent(text)

        continuity = update_continuity(
            topic
        )

        regulate_focus()

        STATE["last_topic"] = topic

        STATE["last_intent"] = intent

        STATE["active_context"] = topic

        STATE["conversation_depth"] += 1

        remember(
            "recent_topics",
            topic,
        )

        remember(
            "recent_intents",
            intent,
        )

        remember(
            "recent_contexts",
            topic,
        )

        STATE["updated"] = now()

        return {
            "topic": topic,
            "intent": intent,
            "continuity": continuity,
            "focus": STATE["focus"],
            "depth": STATE["conversation_depth"],
            "active_context": STATE["active_context"],
        }


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "context": dict(CONTEXT),
        "flags": dict(FLAGS),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return (
        "\n"
        "==============================\n"
        " CONTEXT MANAGER STAGE 6500\n"
        "==============================\n"
        f"ACTIVE:       {STATE['active_context']}\n"
        f"TOPIC:        {STATE['last_topic']}\n"
        f"INTENT:       {STATE['last_intent']}\n"
        f"FOCUS:        {STATE['focus']:.2f}\n"
        f"CONTINUITY:   {STATE['continuity_score']:.2f}\n"
        f"DEPTH:        {STATE['conversation_depth']}\n"
        f"SWITCHES:     {STATE['context_switches']}\n"
        f"CYCLES:       {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" CONTEXT MANAGER STAGE 6500")
    print("================================\n")

    tests = [
        "play music",
        "runtime status",
        "display online",
        "voice system active",
        "play another song",
    ]

    for text in tests:

        print(f"\n[INPUT] {text}")

        result = synthesize_context(
            text
        )

        print(result)

        print(status())

        time.sleep(1)

    print("\n[CONTEXT MANAGER COMPLETE]")
