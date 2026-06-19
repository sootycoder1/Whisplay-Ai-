# =========================
# WHISPLAY BRAIN + COGNITIVE CORE — STAGE 150 MERGED PLUS
# Offline Companion Intelligence Engine
# Decision + Response + Personality + Fallback + Memory + Tools + Status
# Melbourne Personality + Focus + Continuity + Confidence + Mutation Control
# =========================

import random
import re
import time
from datetime import datetime

try:
    from debug import log, error
except Exception:
    def log(x):
        print(x)

    def error(x):
        print(x)


# =========================
# FEATURE NOTES
# =========================

FEATURE_NOTES = {
    "offline_only": "No internet required. All responses are local rule/context based.",
    "cognitive_layer": "Routes input into tool, memory, debug, build, support, display, audio, brain, or conversation paths.",
    "brain_layer": "Generates candidate replies and selects the strongest one.",
    "personality_layer": "Adds hooks, mood, energy, anti-repeat, and natural companion phrasing.",
    "fallback_layer": "Handles unclear, short, broken, or unsupported input.",
    "memory_lite": "Keeps session context, topics, response history, and user patterns.",
    "focus_tracking": "Tracks active subsystem/focus to reduce drift across long sessions.",
    "continuity_tracking": "Keeps a lightweight session direction so responses stay connected.",
    "confidence_weighting": "Uses simple confidence scoring to reduce overconfident or chaotic replies.",
    "mutation_control": "Adds safe variation without changing technical meaning.",
    "tool_hooks": "Optional hooks for tools.registry if available.",
    "status_debug": "status() and cognitive_status() expose system state.",
}


FEATURES = {
    "offline_mode": True,
    "intent_detection": True,
    "routing": True,
    "tools": True,
    "memory_lite": True,
    "context_tracking": True,
    "topic_tracking": True,
    "focus_tracking": True,
    "continuity_tracking": True,
    "confidence_weighting": True,
    "growth_engine": True,
    "multi_response": True,
    "response_scoring": True,
    "conversation_chaining": True,
    "personality_hooks": True,
    "mid_hooks": True,
    "end_hooks": True,
    "fillers": True,
    "mood_engine": True,
    "energy_engine": True,
    "mutation_control": True,
    "response_evaluation": True,
    "anti_repeat": True,
    "fallback": True,
    "debug_safe": True,
}


# =========================
# OPTIONAL TOOL / MEMORY IMPORTS
# =========================

try:
    from tools.registry import run as run_tool
    TOOLS_AVAILABLE = True
except Exception:
    TOOLS_AVAILABLE = False

    def run_tool(name, *args, **kwargs):
        return None


try:
    from brain import memory
    MEMORY_AVAILABLE = True
except Exception:
    memory = None
    MEMORY_AVAILABLE = False


# =========================
# STATE
# =========================

STATE = {
    "started": time.time(),
    "turn_count": 0,
    "last_input": "",
    "last_response": "",
    "last_topic": "",
    "last_intent": "",
    "last_action": "",
    "mood": "neutral",
    "last_mood": "neutral",
    "energy": 1.0,
    "focus": "general",
    "last_focus": "general",
    "continuity": "idle",
    "active_objective": "",
    "confidence": 0.65,
    "pressure": 0.0,
    "loop_level": 0,
    "history": [],
    "responses": [],
    "topics": [],
    "focus_history": [],
    "user_patterns": {},
    "tool_calls": [],
    "errors": [],
}

MAX_INPUT_LENGTH = 700
MAX_HISTORY = 24
MAX_RESPONSES = 24
MAX_TOPICS = 14
MAX_FOCUS_HISTORY = 12
MAX_ERRORS = 10


# =========================
# WORD BANKS
# =========================

QUESTION_WORDS = [
    "what", "why", "how", "when", "where", "who",
    "can", "could", "should", "would", "is", "are", "do", "does",
]

BUILD_WORDS = [
    "build", "make", "create", "add", "upgrade", "supercharge",
    "render", "wire", "connect", "setup", "stage", "merge",
    "combine", "integrate", "design", "feature", "features",
]

DEBUG_WORDS = [
    "error", "failed", "broken", "traceback", "indent",
    "import", "missing", "not found", "crash", "syntax",
    "empty", "lost", "wrong", "mangled", "corrupt",
]

SUPPORT_WORDS = [
    "stuck", "confused", "lost", "frustrated", "rough",
    "tired", "annoyed", "hard", "stall", "stress",
    "panic", "worried", "trust",
]

CONTROL_WORDS = [
    "stop", "quit", "exit", "shutdown", "pause", "cancel",
]

MEMORY_WORDS = [
    "remember", "save", "keep", "checkpoint", "baseline",
    "recall", "memory", "stored",
]

DISPLAY_WORDS = [
    "screen", "display", "pixels", "backlight", "st7789",
    "ui", "render", "hat", "lcd", "tft",
]

AUDIO_WORDS = [
    "audio", "voice", "speaker", "mic", "microphone",
    "piper", "vosk", "sound", "talk", "tts",
]

BRAIN_WORDS = [
    "brain", "personality", "fallback", "cognitive",
    "router", "conversation", "intent", "think",
]

STATE_WORDS = [
    "state", "mood", "energy", "strategy", "runtime",
    "condition", "focus", "pressure",
]

RUNTIME_WORDS = [
    "controller", "orchestrator", "orchestration", "bus",
    "contract", "adapter", "runtime", "core", "system",
]


# =========================
# PERSONALITY / HOOK BANKS
# =========================

HOOK_START = [
    "Yeah—",
    "Alright—",
    "Right—",
    "Look—",
    "Mate—",
    "Listen—",
    "Here’s the thing—",
    "Straight up—",
    "",
]

HOOK_MID = [
    "—real talk—",
    "—quick note—",
    "—this matters—",
    "—keep it clean—",
    "—don’t overcook it—",
]

HOOK_END = [
    "",
    "—done.",
    "easy.",
    "sorted.",
    "that’s it.",
    "your move.",
    "go on.",
    "what’s next?",
]

FILLERS = [
    "yeah nah",
    "nah yeah",
    "to be fair",
    "honestly",
    "real talk",
    "bit of both really",
]

FOLLOW_UPS = [
    "What’s the move?",
    "You building that or testing it?",
    "Where are you taking this?",
    "What’s the end goal?",
    "Want me to push that further?",
]

FALLBACKS = [
    "Say that cleaner.",
    "That didn’t land properly.",
    "Run that again.",
    "Give me the goal, not the noise.",
    "I’m close, but I need one cleaner pass.",
]


# =========================
# RESPONSE BANKS
# =========================

RESP_DEBUG = [
    "That looks like a file, import, path, or paste issue. We isolate the active file first, then fix only that point.",
    "That error is useful. It tells us where the system is breaking instead of making us guess.",
    "This is probably not the whole build failing. It is likely one file calling the wrong layer.",
    "We should not rebuild everything for that. We trace the running file, then follow the import chain.",
]

RESP_BUILD = [
    "We build this as a staged file first. Once it imports cleanly, then we wire it into the active core.",
    "Clean render first, integration second. That keeps the old files safe and gives us a rollback path.",
    "This should be built broad, but connected narrow. Big capability, simple runtime path.",
    "We can go big here, but the safe move is one file, one test, then one wire-in.",
]

RESP_SUPPORT = [
    "Pause for a second. You have the pieces — now we choose what runs and keep everything else safe.",
    "That frustration makes sense. We slow it down and move one clean layer at a time.",
    "The system needs one active path instead of ten possible ones.",
    "We keep it contained: current file, current function, current fix.",
]

RESP_MEMORY = [
    "That should become a checkpoint, not just a comment. Save it as a staged file or backup before moving on.",
    "That sounds like a baseline. The safe move is to lock it before adding more behavior.",
    "If it matters later, we name it clearly and keep it separate.",
]

RESP_DISPLAY = [
    "Display issues should stay in the display layer. The brain should send clean text, mood, and state only.",
    "The screen path needs one owner. Too many display files touching the HAT will make it feel random.",
    "For the UI, keep the brain expressive but send short clean strings to the display.",
]

RESP_AUDIO = [
    "Audio should stay simple. The brain gives text, the speak layer handles Piper and playback.",
    "If speech is working, we do not disturb that layer while upgrading intelligence.",
    "Voice stability matters more than fancy output. Keep the response clean and Pi-safe.",
]

RESP_BRAIN = [
    "This belongs in the brain layer. Intent, context, fallback, and personality should live together cleanly.",
    "The brain should decide, shape, and recover — but orchestration should stay separate.",
    "This is where a merged offline companion brain makes sense.",
]

RESP_STATE = [
    "State belongs in the nervous system layer. The brain can read it, but it should not become the whole controller.",
    "Mood, energy, focus, and pressure should inform cognition without taking over response generation.",
    "State should hold runtime truth. The brain should use that truth to shape the next response.",
]

RESP_RUNTIME = [
    "Runtime control belongs above the brain. Orchestration coordinates; cognition thinks.",
    "The clean path is controller above, brain in the middle, state underneath.",
    "Runtime wiring should be narrow and testable. One import path, one active call, one payload shape.",
]

RESP_QUESTION = [
    "Start from the file you actually run. That file decides the whole chain.",
    "The clean answer is to follow the active path downward, not inspect every file at once.",
    "The safe way is staged copies first, then import tests, then wiring.",
    "If we keep old files untouched and only point imports at the new file, nothing gets lost.",
]

RESP_CONVERSATION = [
    "That tracks. The trick is keeping the active path clean while leaving older work untouched.",
    "Makes sense. Treat this like layers, not one giant pile of files.",
    "Right. The useful move is control: one active stack, everything else archived or staged.",
    "Big features are fine as long as they are switchable and contained.",
]

FALLBACK_SHORT = [
    "Bit short — give me more.",
    "Need a little more detail.",
    "What exactly do you mean?",
    "Say that again with the file or goal.",
]

FALLBACK_PARTIAL = [
    "I get part of that — what’s the outcome you want?",
    "Tell me whether this is brain, display, audio, core, state, or memory.",
    "Give me the target and I’ll line it up.",
    "That’s a bit loose. Give me the file name or the layer.",
]

FALLBACK_CONTEXT = [
    "Still about {}?",
    "You mean the {} layer?",
    "Same direction — {}?",
    "Are we still working around {}?",
]


# =========================
# UTILS
# =========================

def clean_text(text):
    if not text:
        return ""

    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)

    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]

    return text


def pick(options):
    return random.choice(options) if options else ""


def contains_any(text, words):
    return any(word in text for word in words)


def trim_list(items, limit):
    while len(items) > limit:
        items.pop(0)


def clamp(value, minimum=0.0, maximum=1.0):
    try:
        value = float(value)
    except Exception:
        value = minimum

    return max(minimum, min(maximum, value))


def record_error(label, exc):
    msg = f"{label}: {exc}"
    STATE["errors"].append(msg)
    trim_list(STATE["errors"], MAX_ERRORS)
    error(msg)


def word_count(text):
    return len(clean_text(text).split())


# =========================
# MEMORY-LITE / GROWTH
# =========================

def remember_input(text):
    STATE["last_input"] = text
    STATE["turn_count"] += 1

    if FEATURES["memory_lite"]:
        STATE["history"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "text": text,
        })
        trim_list(STATE["history"], MAX_HISTORY)


def remember_response(response):
    STATE["last_response"] = response

    if FEATURES["anti_repeat"]:
        STATE["responses"].append(response)
        trim_list(STATE["responses"], MAX_RESPONSES)


def update_topic(text, intent):
    if not FEATURES["topic_tracking"]:
        return

    if len(text.split()) > 3:
        STATE["last_topic"] = text

        if intent not in ["unclear", "empty"]:
            STATE["topics"].append(text)
            trim_list(STATE["topics"], MAX_TOPICS)


def learn_pattern(text, intent):
    if not FEATURES["growth_engine"]:
        return

    patterns = STATE["user_patterns"]
    patterns[intent] = patterns.get(intent, 0) + 1

    low = text.lower()

    for key in [
        "file", "stage", "display", "audio", "brain",
        "memory", "state", "runtime", "controller",
    ]:
        if key in low:
            patterns[f"{key}_focused"] = patterns.get(f"{key}_focused", 0) + 1


def store_memory_key(key, value):
    if MEMORY_AVAILABLE and hasattr(memory, "store"):
        try:
            memory.store(key, value)
            return True
        except Exception as e:
            record_error("[MEMORY STORE ERROR]", e)

    return False


def recall_memory_key(key):
    if MEMORY_AVAILABLE and hasattr(memory, "recall"):
        try:
            return memory.recall(key)
        except Exception as e:
            record_error("[MEMORY RECALL ERROR]", e)

    return None


# =========================
# INTENT DETECTION
# =========================

def detect_intent(text):
    if not FEATURES["intent_detection"]:
        return "conversation"

    t = clean_text(text).lower()

    if not t:
        return "empty"

    if contains_any(t, CONTROL_WORDS):
        return "control"

    if contains_any(t, DEBUG_WORDS):
        return "debug"

    if contains_any(t, BUILD_WORDS):
        return "build"

    if contains_any(t, SUPPORT_WORDS):
        return "support"

    if contains_any(t, MEMORY_WORDS):
        return "memory"

    if contains_any(t, DISPLAY_WORDS):
        return "display"

    if contains_any(t, AUDIO_WORDS):
        return "audio"

    if contains_any(t, BRAIN_WORDS):
        return "brain"

    if contains_any(t, STATE_WORDS):
        return "state"

    if contains_any(t, RUNTIME_WORDS):
        return "runtime"

    first = t.split()[0] if t.split() else ""

    if first in QUESTION_WORDS or "?" in t:
        return "question"

    if len(t.split()) <= 1:
        return "unclear"

    return "conversation"


# =========================
# FOCUS / CONTINUITY / CONFIDENCE
# =========================

def infer_focus(text, intent):
    low = clean_text(text).lower()

    if intent in ["display"] or contains_any(low, DISPLAY_WORDS):
        return "display"

    if intent in ["audio"] or contains_any(low, AUDIO_WORDS):
        return "audio"

    if intent in ["brain"] or contains_any(low, BRAIN_WORDS):
        return "brain"

    if intent in ["state"] or contains_any(low, STATE_WORDS):
        return "state"

    if intent in ["runtime"] or contains_any(low, RUNTIME_WORDS):
        return "runtime"

    if intent in ["debug"]:
        return "debug"

    if intent in ["build"]:
        return "build"

    if intent in ["memory"]:
        return "memory"

    if intent in ["support"]:
        return "support"

    if STATE["focus"] and STATE["focus"] != "general":
        return STATE["focus"]

    return "general"


def update_focus(text, intent):
    if not FEATURES["focus_tracking"]:
        return

    new_focus = infer_focus(text, intent)
    old_focus = STATE["focus"]

    STATE["last_focus"] = old_focus
    STATE["focus"] = new_focus

    if new_focus != old_focus:
        STATE["focus_history"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "from": old_focus,
            "to": new_focus,
            "intent": intent,
        })
        trim_list(STATE["focus_history"], MAX_FOCUS_HISTORY)


def update_continuity(text, intent):
    if not FEATURES["continuity_tracking"]:
        return

    focus = STATE["focus"]

    if intent in ["debug", "build", "brain", "state", "runtime"]:
        STATE["continuity"] = f"{intent}:{focus}"
        STATE["active_objective"] = f"work_on_{focus}"

    elif intent == "support":
        STATE["continuity"] = "support"
        STATE["active_objective"] = "stabilise_user_and_runtime"

    elif intent == "memory":
        STATE["continuity"] = "memory"
        STATE["active_objective"] = "preserve_context"

    elif intent == "unclear":
        if STATE["continuity"] == "idle":
            STATE["continuity"] = "clarify"

    else:
        if STATE["continuity"] == "idle":
            STATE["continuity"] = "conversation"


def calculate_pressure(text, intent):
    low = clean_text(text).lower()
    pressure = 0.0

    if intent in ["debug", "support", "unclear"]:
        pressure += 0.25

    if any(w in low for w in ["lost", "broken", "wrong", "panic", "confused"]):
        pressure += 0.25

    if STATE["loop_level"] >= 2:
        pressure += 0.25

    if word_count(text) <= 2:
        pressure += 0.15

    return clamp(pressure)


def calculate_confidence(text, intent):
    if not FEATURES["confidence_weighting"]:
        return 0.65

    confidence = 0.65

    if intent in ["debug", "build", "display", "audio", "brain", "state", "runtime"]:
        confidence += 0.15

    if intent in ["unclear", "empty"]:
        confidence -= 0.35

    if word_count(text) <= 2:
        confidence -= 0.2

    if STATE["focus"] != "general":
        confidence += 0.1

    if STATE["loop_level"] >= 2:
        confidence -= 0.15

    return round(clamp(confidence), 2)


def detect_looping(text):
    recent = [item["text"].lower() for item in STATE["history"][-5:] if "text" in item]
    low = clean_text(text).lower()

    if not recent:
        return 0

    repeats = sum(1 for item in recent if item == low)

    if repeats >= 2:
        return STATE["loop_level"] + 1

    focus_hits = sum(1 for item in recent if STATE["focus"] != "general" and STATE["focus"] in item)

    if len(recent) >= 4 and focus_hits >= 3:
        return max(STATE["loop_level"], 1)

    return 0


# =========================
# MOOD / ENERGY ENGINE
# =========================

def update_mood_energy(intent):
    if not FEATURES["mood_engine"]:
        return

    STATE["last_mood"] = STATE["mood"]

    if intent == "support":
        STATE["mood"] = "supportive"
        STATE["energy"] = 0.75

    elif intent == "debug":
        STATE["mood"] = "focused"
        STATE["energy"] = 0.9

    elif intent == "build":
        STATE["mood"] = "active"
        STATE["energy"] = 1.12

    elif intent == "brain":
        STATE["mood"] = "creative"
        STATE["energy"] = 1.08

    elif intent == "state":
        STATE["mood"] = "focused"
        STATE["energy"] = 0.96

    elif intent == "runtime":
        STATE["mood"] = "technical"
        STATE["energy"] = 0.98

    elif intent == "unclear":
        STATE["mood"] = "curious"
        STATE["energy"] = 0.8

    else:
        STATE["mood"] = "neutral"
        STATE["energy"] = 1.0

    if STATE["pressure"] >= 0.55:
        STATE["energy"] = min(STATE["energy"], 0.86)

    STATE["energy"] = round(max(0.45, min(1.35, STATE["energy"])), 2)


def update_context(text, intent):
    STATE["last_intent"] = intent

    if FEATURES["context_tracking"]:
        update_topic(text, intent)
        learn_pattern(text, intent)
        update_focus(text, intent)

    STATE["loop_level"] = detect_looping(text)
    STATE["pressure"] = calculate_pressure(text, intent)
    STATE["confidence"] = calculate_confidence(text, intent)

    update_continuity(text, intent)
    update_mood_energy(intent)


# =========================
# COGNITIVE ROUTING
# =========================

def route_input(text):
    intent = detect_intent(text)

    if intent == "control":
        return {"intent": "control", "action": "control"}

    if intent == "memory":
        low = text.lower()

        if "remember" in low or "save" in low or "checkpoint" in low:
            return {
                "intent": "memory_store",
                "action": "memory_store",
                "key": "checkpoint" if "checkpoint" in low else "note",
                "value": text,
            }

        if "recall" in low or "what did" in low:
            return {
                "intent": "memory_recall",
                "action": "memory_recall",
                "key": "note",
            }

    return {"intent": intent, "action": "conversation"}


def handle_tool(decision):
    if not TOOLS_AVAILABLE or not FEATURES["tools"]:
        return "Tool system unavailable."

    try:
        tool = decision.get("tool")
        args = decision.get("args", [])

        log(f"[COG TOOL] {tool} {args}")
        result = run_tool(tool, *args)

        STATE["tool_calls"].append({
            "tool": tool,
            "args": args,
            "time": time.time(),
        })
        trim_list(STATE["tool_calls"], 10)

        return f"{tool} executed." if result is None else str(result)

    except Exception as e:
        record_error("[TOOL ERROR]", e)
        return "Tool execution failed."


def handle_memory_store(decision):
    key = decision.get("key", "note")
    value = decision.get("value", "")

    stored = store_memory_key(key, value)

    if stored:
        return "Got it. I’ll remember that."

    STATE["topics"].append(value)
    trim_list(STATE["topics"], MAX_TOPICS)
    return "Saved in session memory."


def handle_memory_recall(decision):
    key = decision.get("key", "note")
    recalled = recall_memory_key(key)

    if recalled:
        return str(recalled)

    if STATE["topics"]:
        return f"Last thing I have in session memory: {STATE['topics'][-1]}"

    return "I don’t have that stored yet."


# =========================
# RESPONSE GENERATION
# =========================

def generate_base_response(text, intent):
    if intent == "empty":
        return "Say that again."

    if intent == "control":
        return "Okay. I’ll keep it clean and stop the current direction."

    if intent == "debug":
        return pick(RESP_DEBUG)

    if intent == "build":
        return pick(RESP_BUILD)

    if intent == "support":
        return pick(RESP_SUPPORT)

    if intent == "question":
        return pick(RESP_QUESTION)

    if intent == "memory":
        return pick(RESP_MEMORY)

    if intent == "display":
        return pick(RESP_DISPLAY)

    if intent == "audio":
        return pick(RESP_AUDIO)

    if intent == "brain":
        return pick(RESP_BRAIN)

    if intent == "state":
        return pick(RESP_STATE)

    if intent == "runtime":
        return pick(RESP_RUNTIME)

    if intent == "unclear":
        return fallback(text)

    return pick(RESP_CONVERSATION)


def generate_candidates(text, intent):
    if not FEATURES["multi_response"]:
        return [generate_base_response(text, intent)]

    candidates = []

    for _ in range(4):
        candidates.append(generate_base_response(text, intent))

    if FEATURES["conversation_chaining"] and STATE["last_topic"] and intent in ["conversation", "unclear"]:
        candidates.append(
            f"Still connected to {STATE['last_topic']} — we keep that thread alive and make the next move clean."
        )

    if STATE["focus"] != "general" and intent in ["conversation", "question", "unclear"]:
        candidates.append(
            f"Still on the {STATE['focus']} path. The clean move is to keep that thread contained."
        )

    if STATE["confidence"] < 0.42:
        candidates.append(
            "I’m not fully confident from that input. Give me the file, the layer, or the exact goal."
        )

    return candidates


# =========================
# RESPONSE SCORING
# =========================

def score_response(response, intent):
    if not response:
        return -10

    score = 0
    words = response.split()
    low = response.lower()

    if 6 <= len(words) <= 34:
        score += 3

    if len(words) > 45:
        score -= 2

    if "file" in low and intent in ["debug", "build"]:
        score += 2

    if "clean" in low:
        score += 1

    if "safe" in low or "stable" in low:
        score += 1

    if STATE["focus"] != "general" and STATE["focus"] in low:
        score += 1

    if STATE["confidence"] < 0.45 and ("guess" in low or "maybe" in low):
        score += 1

    if response in STATE["responses"][-4:]:
        score -= 5

    return score


def select_best_response(candidates, intent):
    if not candidates:
        return ""

    if not FEATURES["response_scoring"]:
        return candidates[0]

    return sorted(candidates, key=lambda r: score_response(r, intent), reverse=True)[0]


# =========================
# FALLBACK
# =========================

def fallback(text=""):
    text = clean_text(text)

    if not text:
        return "Say that again."

    words = text.lower().split()

    if len(words) <= 1:
        return pick(FALLBACK_SHORT)

    if STATE["last_topic"] and random.random() < 0.5:
        return pick(FALLBACK_CONTEXT).format(STATE["last_topic"])

    return pick(FALLBACK_PARTIAL)


# =========================
# PERSONALITY / MUTATION SHAPING
# =========================

def prevent_repeat(response):
    if not FEATURES["anti_repeat"]:
        return response

    if response == STATE["last_response"]:
        return response + " Same direction, cleaner version."

    if response in STATE["responses"][-3:]:
        return response + " Let me say that another way."

    return response


def mutation_allowed():
    if not FEATURES["mutation_control"]:
        return False

    if STATE["confidence"] < 0.45:
        return False

    if STATE["pressure"] > 0.65:
        return False

    if STATE["last_intent"] in ["debug", "state", "runtime"]:
        return random.random() < 0.12

    return random.random() < 0.28


def mutate_response(response):
    response = clean_text(response)

    if not response or not mutation_allowed():
        return response

    variants = [response]

    if word_count(response) > 8:
        variants.append(response.replace("The clean", "Clean"))
        variants.append(response.replace("The safe", "Safe"))
        variants.append(response.replace("We should", "We"))
        variants.append(response.replace("You need to", "You need"))

    if STATE["mood"] in ["creative", "active"] and STATE["confidence"] >= 0.65:
        variants.append(f"{response} {pick(HOOK_END)}")

    if STATE["mood"] == "supportive":
        variants.append(response.replace(" — ", "... "))

    return pick(variants)


def apply_mood_shape(response):
    mood = STATE["mood"]
    energy = STATE["energy"]

    if mood == "supportive":
        response = response.replace(" — ", "... ")

    elif mood == "focused":
        response = response.replace("…", ".")
        response = response.replace("Okay —", "Okay.")

    elif mood == "technical":
        response = response.replace("Yeah—", "Right—")

    elif mood == "creative":
        if random.random() < 0.28:
            response = "Big picture: " + response

    if energy > 1.1:
        response = response.replace(". ", "! ")

    elif energy < 0.8:
        response = response.replace("!", ".")
        response = response.replace("Straight up—", "Right—")

    return response


def apply_personality_hooks(response):
    response = clean_text(response)

    if not response:
        return response

    confidence = STATE["confidence"]
    pressure = STATE["pressure"]
    intent = STATE["last_intent"]

    start_chance = 0.48
    mid_chance = 0.14
    end_chance = 0.24
    filler_chance = 0.08

    if intent in ["debug", "state", "runtime"]:
        start_chance *= 0.55
        mid_chance *= 0.5
        filler_chance = 0.0

    if pressure > 0.55:
        start_chance *= 0.45
        mid_chance = 0.0
        end_chance *= 0.5
        filler_chance = 0.0

    if confidence < 0.45:
        start_chance = 0.0
        mid_chance = 0.0
        filler_chance = 0.0

    if FEATURES["personality_hooks"] and random.random() < start_chance:
        hook = pick(HOOK_START)
        if hook:
            response = f"{hook} {response}"

    if FEATURES["fillers"] and random.random() < filler_chance:
        filler = pick(FILLERS)
        if filler:
            response = f"{filler}, {response}"

    if FEATURES["mid_hooks"]:
        words = response.split()
        if 8 <= len(words) <= 25 and random.random() < mid_chance:
            words.insert(len(words) // 2, pick(HOOK_MID))
            response = " ".join(words)

    if FEATURES["end_hooks"] and random.random() < end_chance:
        end = pick(HOOK_END)
        if end:
            response = f"{response} {end}"

    return clean_text(response)


def evaluate_response(response):
    if not FEATURES["response_evaluation"]:
        return response

    response = clean_text(response)

    if not response:
        return fallback(STATE["last_input"])

    if STATE["confidence"] < 0.35:
        return "I need one cleaner pass: file, layer, or exact goal."

    if STATE["loop_level"] >= 3:
        return "We’re looping. Give me the next exact file or stop this branch."

    if word_count(response) > 55 and STATE["pressure"] > 0.5:
        words = response.split()
        response = " ".join(words[:34]) + "."

    return clean_text(response)


def shape_response(response):
    if not response:
        response = fallback(STATE["last_input"])

    response = clean_text(response)
    response = prevent_repeat(response)
    response = mutate_response(response)
    response = apply_personality_hooks(response)
    response = apply_mood_shape(response)
    response = evaluate_response(response)

    return clean_text(response)


# =========================
# MAIN ENGINES
# =========================

def think(text):
    text = clean_text(text)

    if not text:
        return "Say that again."

    remember_input(text)

    decision = route_input(text)
    intent = decision.get("intent", detect_intent(text))
    action = decision.get("action", "conversation")

    STATE["last_action"] = action
    update_context(text, intent)

    try:
        if action == "tool":
            response = handle_tool(decision)

        elif action == "memory_store":
            response = handle_memory_store(decision)

        elif action == "memory_recall":
            response = handle_memory_recall(decision)

        elif action == "control":
            response = generate_base_response(text, "control")

        else:
            candidates = generate_candidates(text, intent)
            response = select_best_response(candidates, intent)

        if not response and FEATURES["fallback"]:
            response = fallback(text)

    except Exception as e:
        record_error("[BRAIN ERROR]", e)
        response = fallback(text)

    response = shape_response(response)
    remember_response(response)

    return response


def process_input(text):
    return think(text)


def get_response(text):
    return think(text)


def generate_response(text):
    return think(text)


def process(text):
    response = think(text)

    return {
        "action": STATE["last_action"],
        "intent": STATE["last_intent"],
        "mood": STATE["mood"],
        "energy": STATE["energy"],
        "focus": STATE["focus"],
        "continuity": STATE["continuity"],
        "active_objective": STATE["active_objective"],
        "confidence": STATE["confidence"],
        "pressure": STATE["pressure"],
        "loop_level": STATE["loop_level"],
        "response": response,
        "text": text,
        "time": time.time(),
    }


def status():
    return {
        "features": FEATURES,
        "feature_notes": FEATURE_NOTES,
        "turn_count": STATE["turn_count"],
        "last_input": STATE["last_input"],
        "last_response": STATE["last_response"],
        "last_topic": STATE["last_topic"],
        "last_intent": STATE["last_intent"],
        "last_action": STATE["last_action"],
        "mood": STATE["mood"],
        "energy": STATE["energy"],
        "focus": STATE["focus"],
        "last_focus": STATE["last_focus"],
        "continuity": STATE["continuity"],
        "active_objective": STATE["active_objective"],
        "confidence": STATE["confidence"],
        "pressure": STATE["pressure"],
        "loop_level": STATE["loop_level"],
        "memory_available": MEMORY_AVAILABLE,
        "tools_available": TOOLS_AVAILABLE,
        "topics": STATE["topics"][-5:],
        "focus_history": STATE["focus_history"][-5:],
        "patterns": STATE["user_patterns"],
        "errors": STATE["errors"],
    }


def cognitive_status():
    return status()


# =========================
# SELF TEST
# =========================

if __name__ == "__main__":
    tests = [
        "hello",
        "what file do I run",
        "this is broken",
        "build the brain bigger",
        "I'm stuck",
        "screen has no pixels",
        "audio is working",
        "remember this checkpoint",
        "state core",
        "runtime controller",
        "ok",
    ]

    for item in tests:
        print("USER:", item)
        print("BOT :", think(item))
        print()

    print("STATUS:", status())
