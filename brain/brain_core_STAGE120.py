# =========================
# WHISPLAY BRAIN — STAGE 120
# LIMITLESS + FEATURE-DRIVEN
# =========================

import random
import re

# =========================
# FEATURES (TOGGLE SYSTEM)
# =========================

FEATURES = {
    "hooks": True,
    "mid_hooks": True,
    "end_hooks": True,
    "intent_detection": True,
    "context_tracking": True,
    "mood_engine": True,
    "energy_engine": True,
    "fallback": True,
    "anti_repeat": True,
    "memory_lite": True,
    "multi_response": True,
    "response_scoring": True,
    "conversation_chaining": True,
}

# =========================
# STATE
# =========================

STATE = {
    "last_input": "",
    "last_response": "",
    "last_topic": "",
    "last_intent": "",
    "history": [],
    "responses": [],
    "mood": "neutral",
    "energy": 1.0,
}

MAX_HISTORY = 12

# =========================
# HOOK BANKS
# =========================

HOOK_START = ["Alright…", "Okay —", "Right —", "Interesting…", "Yeah —", "Look —"]
HOOK_MID = ["that’s the key part", "that’s where it matters", "that’s the shift"]
HOOK_END = ["That’s the clean version.", "That’s the move.", "That’s the safe play."]

# =========================
# UTILS
# =========================

def clean(text):
    return re.sub(r"\s+", " ", str(text)).strip()

def pick(arr):
    return random.choice(arr) if arr else ""

# =========================
# INTENT
# =========================

def detect_intent(text):
    if not FEATURES["intent_detection"]:
        return "conversation"

    t = text.lower()

    if len(t.split()) <= 2:
        return "unclear"

    if any(w in t for w in ["error", "failed", "broken"]):
        return "debug"

    if any(w in t for w in ["build", "make", "add", "upgrade"]):
        return "build"

    if any(w in t for w in ["stuck", "confused"]):
        return "support"

    return "conversation"

# =========================
# CONTEXT
# =========================

def update_context(text, intent):
    if not FEATURES["context_tracking"]:
        return

    STATE["last_intent"] = intent

    if len(text.split()) > 3:
        STATE["last_topic"] = text

    if FEATURES["mood_engine"]:
        if intent == "support":
            STATE["mood"] = "supportive"
        elif intent == "debug":
            STATE["mood"] = "focused"
        else:
            STATE["mood"] = "neutral"

    if FEATURES["energy_engine"]:
        if intent == "build":
            STATE["energy"] = 1.1
        else:
            STATE["energy"] = 1.0

# =========================
# RESPONSE GENERATION
# =========================

def generate_base(text, intent):

    if intent == "debug":
        return pick([
            "That’s likely a file or import issue.",
            "We isolate the error point first.",
        ])

    if intent == "build":
        return pick([
            "Build it as a new staged file.",
            "Clean render first, then integrate.",
        ])

    if intent == "support":
        return pick([
            "You’re not off — just need structure.",
            "Pause — we simplify and go step by step.",
        ])

    return pick([
        "Yeah, that tracks — keep control of the system.",
        "Makes sense — keep the active path clean.",
    ])

# =========================
# MULTI RESPONSE ENGINE
# =========================

def generate_candidates(text, intent):
    if not FEATURES["multi_response"]:
        return [generate_base(text, intent)]

    return [generate_base(text, intent) for _ in range(3)]

# =========================
# RESPONSE SCORING
# =========================

def score_response(r):
    score = 0

    if len(r.split()) > 4:
        score += 1

    if "—" in r or "…" in r:
        score += 1

    return score

def select_best(candidates):
    if not FEATURES["response_scoring"]:
        return candidates[0]

    scored = sorted(candidates, key=score_response, reverse=True)
    return scored[0]

# =========================
# FALLBACK
# =========================

def fallback(text):
    if not FEATURES["fallback"]:
        return "..."

    if len(text.split()) <= 2:
        return pick([
            "Bit short — give me more.",
            "Need more detail.",
        ])

    if STATE["last_topic"]:
        return f"Still about {STATE['last_topic']}?"

    return pick([
        "What’s the goal?",
        "Give me the outcome.",
    ])

# =========================
# PERSONALITY
# =========================

def apply_personality(r):

    if not r:
        return fallback("")

    if FEATURES["hooks"] and random.random() < 0.6:
        r = f"{pick(HOOK_START)} {r}"

    if FEATURES["mid_hooks"] and random.random() < 0.25:
        parts = r.split()
        parts.insert(len(parts)//2, pick(HOOK_MID))
        r = " ".join(parts)

    if FEATURES["end_hooks"] and random.random() < 0.4:
        r = f"{r} {pick(HOOK_END)}"

    if FEATURES["anti_repeat"]:
        if r in STATE["responses"][-3:]:
            r += " Let me say that cleaner."

    STATE["responses"].append(r)

    if len(STATE["responses"]) > MAX_HISTORY:
        STATE["responses"].pop(0)

    return r

# =========================
# MAIN
# =========================

def think(text):

    text = clean(text)

    if not text:
        return "Say that again."

    STATE["last_input"] = text

    intent = detect_intent(text)
    update_context(text, intent)

    try:
        candidates = generate_candidates(text, intent)
        response = select_best(candidates)

        if not response:
            response = fallback(text)

    except Exception:
        response = fallback(text)

    response = apply_personality(response)

    STATE["last_response"] = response

    return response

# =========================
# COMPATIBILITY
# =========================

def get_response(text):
    return think(text)

def process(text):
    return {
        "action": "respond",
        "response": think(text),
        "intent": STATE["last_intent"],
        "mood": STATE["mood"],
        "energy": STATE["energy"],
    }
