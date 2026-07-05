# =========================
# WHISPLAY BRAIN + COGNITIVE CORE — STAGE 150 MERGED
# Offline Companion Intelligence Engine
# Decision + Response + Personality + Fallback + Memory + Tools + Status
# =========================

import random
import re
import time
from datetime import datetime

try:
    from debug import log, error
except Exception:
    def log(x): print(x)
    def error(x): print(x)


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
    "growth_engine": True,
    "multi_response": True,
    "response_scoring": True,
    "conversation_chaining": True,
    "personality_hooks": True,
    "mid_hooks": True,
    "end_hooks": True,
    "mood_engine": True,
    "energy_engine": True,
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
    "active_subject": "",
    "previous_subject": "",
    "last_dialogue_act": "",
    "follow_up_count": 0,
    "context_frames": [],
    "mood": "neutral",
    "last_mood": "neutral",
    "energy": 1.0,
    "history": [],
    "responses": [],
    "topics": [],
    "user_patterns": {},
    "tool_calls": [],
    "errors": [],
}

MAX_INPUT_LENGTH = 700
MAX_HISTORY = 24
MAX_RESPONSES = 24
MAX_TOPICS = 14
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


# =========================
# HOOK BANKS
# =========================

HOOK_START = [
    "Alright…",
    "Okay —",
    "Right —",
    "Yeah —",
    "Look —",
    "Interesting…",
    "I’ve got you —",
    "Here’s the thing —",
    "Let me frame it properly —",
    "That makes sense —",
    "Good, now we’re on the right layer —",
    "Clean move —",
    "Smart move —",
]

HOOK_MID = [
    "that’s the key part",
    "that’s where it matters",
    "that’s the clean path",
    "that’s the stable point",
    "that’s where the system gets control",
    "that’s the useful piece",
]

HOOK_END = [
    "That’s the clean version.",
    "That’s where I’d start.",
    "That keeps it stable.",
    "That’s the safer move.",
    "That gives us control.",
    "That’s the important bit.",
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
    "We build this as a new staged file first. Once it imports cleanly, then we wire it into the active core.",
    "Clean render first, integration second. That keeps the old files safe and gives us a rollback path.",
    "This should be built broad, but connected narrow. Big capability, simple runtime path.",
    "We can go big here, but the safe move is one new file, one test, then one wire-in.",
]

RESP_SUPPORT = [
    "You’re not behind. This is the part where the project stops being loose files and becomes a controlled system.",
    "Pause for a second. You’ve got the pieces — now we choose what runs and keep everything else safe.",
    "That frustration makes sense. We slow it down and move one clean layer at a time.",
    "You’re not lost. The system just needs one active path instead of ten possible ones.",
]

RESP_MEMORY = [
    "That should become a checkpoint, not just a comment. Save it as a staged file or backup before moving on.",
    "That sounds like a baseline. The safe move is to lock it before adding more behavior.",
    "Good point. If it matters later, we name it clearly and keep it separate.",
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
    "The brain should decide, shape, and recover — but the assistant core should stay simple.",
    "This is exactly where a merged offline companion brain makes sense.",
]

RESP_CONVERSATION = [
    "Yeah, that tracks. The trick is keeping the active path clean while leaving all the older work untouched.",
    "Makes sense. We treat this like layers, not one giant pile of files.",
    "Right. The useful move is control: one active stack, everything else archived or staged.",
    "I’m with you. Big features are fine as long as they are switchable and contained.",
]

FALLBACK_SHORT = [
    "Bit short — give me more.",
    "Need a little more detail.",
    "What exactly do you mean?",
    "Say that again with the file or goal.",
]

FALLBACK_PARTIAL = [
    "I get part of that — what’s the outcome you want?",
    "Tell me whether this is brain, display, audio, core, or memory.",
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


def record_error(label, exc):
    msg = f"{label}: {exc}"
    STATE["errors"].append(msg)
    trim_list(STATE["errors"], MAX_ERRORS)
    error(msg)


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

    for key in ["file", "stage", "display", "audio", "brain", "memory"]:
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
# STAGE 190 CONTEXT ENGINE
# =========================

CONTEXT_SUBJECTS = {
    "audio": (
        "audio", "sound", "speaker", "speech", "voice",
        "microphone", "mic", "piper", "vosk",
    ),
    "display": (
        "display", "screen", "pixels", "tft",
        "render", "backlight",
    ),
    "brain": (
        "brain", "reasoning", "cognitive", "intent",
        "response", "language", "personality",
    ),
    "memory": (
        "memory", "remember", "recall", "stored",
        "checkpoint", "history",
    ),
    "runtime": (
        "runtime", "controller", "contract", "bus",
        "state", "subsystem", "boot",
    ),
    "build": (
        "build", "file", "stage", "candidate",
        "compile", "patch", "upgrade",
    ),
}


def detect_subject(text, intent=""):
    low = clean_text(text).lower()

    for subject, words in CONTEXT_SUBJECTS.items():
        if any(word in low for word in words):
            return subject

    if intent in CONTEXT_SUBJECTS:
        return intent

    return ""


def detect_dialogue_act(text):
    low = clean_text(text).lower().strip()
    words = [
        word.strip(".,!?;:")
        for word in low.split()
    ]
    first = words[0] if words else ""

    if not low:
        return "empty"

    if low in {"hello", "hi", "hey", "hello there"}:
        return "greeting"

    if low in {"thanks", "thank you", "cheers"}:
        return "thanks"

    if low.startswith(
        ("yes", "yeah", "yep", "correct", "exactly", "that one")
    ):
        return "confirmation"

    if low.startswith(("no ", "no,", "not that", "i meant", "sorry, i meant")):
        return "correction"

    if low.startswith(("what about", "how about", "and the", "and what")):
        return "topic_shift"

    if first in QUESTION_WORDS or low.endswith("?"):
        refers_back = any(
            word in words
            for word in ("it", "that", "this", "one", "they", "them")
        )

        if len(words) <= 4 or refers_back:
            return "follow_up_question"

        return "question"

    if low in {"why", "why?", "how", "how?", "what", "what?"}:
        return "follow_up_question"

    return "statement"


def build_context_frame(text, intent):
    dialogue_act = detect_dialogue_act(text)
    previous_subject = STATE.get("active_subject", "")

    explicit_subject = detect_subject(text, "")

    if dialogue_act in {"confirmation", "follow_up_question"}:
        subject = explicit_subject or previous_subject
    else:
        subject = explicit_subject or detect_subject(text, intent)

    if subject and subject != previous_subject:
        STATE["previous_subject"] = previous_subject
        STATE["active_subject"] = subject

    elif not subject:
        subject = previous_subject

    if dialogue_act in {
        "follow_up_question",
        "confirmation",
        "correction",
        "topic_shift",
    }:
        STATE["follow_up_count"] += 1
    else:
        STATE["follow_up_count"] = 0

    STATE["last_dialogue_act"] = dialogue_act

    frame = {
        "text": clean_text(text),
        "intent": intent,
        "dialogue_act": dialogue_act,
        "subject": subject,
        "previous_subject": STATE.get("previous_subject", ""),
        "turn": STATE.get("turn_count", 0),
    }

    STATE["context_frames"].append(frame)
    trim_list(STATE["context_frames"], 12)

    return frame


def generate_context_response(text, intent):
    low = clean_text(text).lower().strip()
    frame = build_context_frame(text, intent)

    act = frame["dialogue_act"]
    subject = frame["subject"]
    previous = frame["previous_subject"]

    if act == "correction":
        if subject:
            return f"Understood. You mean the {subject} side."
        return "Understood. Tell me the corrected subject."

    if act == "topic_shift":
        if subject:
            return f"Okay. We’re switching to the {subject} side."
        return "Okay. Which part do you want to switch to?"

    if act == "confirmation":
        if subject:
            return f"Good. We’re staying with the {subject} side."
        return "Good. I’m following."

    if act == "follow_up_question":
        if low.startswith("why") and subject:
            return (
                f"For the {subject} side, I need the last result or error "
                "before I can give the exact cause."
            )

        if low.startswith("how") and subject:
            return (
                f"For the {subject} side, we should inspect the active path "
                "and change one verified layer at a time."
            )

        if low.startswith("what") and subject:
            return f"We’re currently talking about the {subject} side."

        if subject:
            return f"Your follow-up is still about the {subject} side."

        if previous:
            return f"Are you continuing with the {previous} side?"

        return "Which part are you referring to?"

    if act == "statement" and subject:
        refers_back = any(
            word in low.split()
            for word in ("it", "that", "this", "they", "them")
        )

        if refers_back:
            return f"Understood. That update is about the {subject} side."

    return ""


# =========================
# INTENT DETECTION
# =========================

def detect_intent(text):
    if not FEATURES["intent_detection"]:
        return "conversation"

    t = text.lower().strip()

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

    first = t.split()[0] if t.split() else ""

    if first in QUESTION_WORDS:
        return "question"

    if len(t.split()) <= 1:
        return "unclear"

    return "conversation"


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

    elif intent == "unclear":
        STATE["mood"] = "curious"
        STATE["energy"] = 0.8

    else:
        STATE["mood"] = "neutral"
        STATE["energy"] = 1.0


def update_context(text, intent):
    STATE["last_intent"] = intent

    if FEATURES["context_tracking"]:
        update_topic(text, intent)
        learn_pattern(text, intent)

    update_mood_energy(intent)


# =========================
# COGNITIVE ROUTING
# =========================

def route_input(text):
    intent = detect_intent(text)
    normalized = " ".join(str(text or "").lower().split())

    status_commands = {
        "status",
        "check status",
        "system status",
        "check system status",
        "runtime status",
        "check runtime status",
    }

    if normalized in status_commands:
        return {
            "intent": "system_status",
            "action": "system_status",
        }

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

        STATE["tool_calls"].append({"tool": tool, "args": args, "time": time.time()})
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

DIRECT_PREFIX = "[[DIRECT]]"


def generate_direct_response(text, intent):
    cleaned = clean_text(text)
    low = cleaned.lower().strip()

    if not low:
        return ""

    context_response = generate_context_response(cleaned, intent)
    if context_response:
        return DIRECT_PREFIX + context_response

    if low in {"hello", "hi", "hey", "hello there"}:
        return DIRECT_PREFIX + "Hello. I’m ready."

    if low in {"thanks", "thank you", "cheers"}:
        return DIRECT_PREFIX + "You’re welcome."

    if low in {"ok", "okay", "done", "ready"}:
        return DIRECT_PREFIX + "Good. I’m ready for the next step."

    if "how are you" in low:
        return DIRECT_PREFIX + "I’m running normally."

    if "what controls your brain" in low or "what file controls the brain" in low:
        return DIRECT_PREFIX + "The cognitive brain file handles my reasoning and responses."

    if "why is the microphone slow" in low:
        return DIRECT_PREFIX + "The microphone can be slow while the speech model loads or waits for clear audio."

    if "make you faster" in low or "response faster" in low:
        return DIRECT_PREFIX + "Preloading the speech model makes my first response faster."

    if "display" in low and any(word in low for word in ("not", "broken", "stuck", "update")):
        return DIRECT_PREFIX + "The display path needs checking separately from the brain and audio."

    if "audio" in low and any(word in low for word in ("slow", "delay", "broken", "not")):
        return DIRECT_PREFIX + "The audio path needs checking from recognition through speech output."

    if intent == "debug":
        return DIRECT_PREFIX + "Show me the exact error and the active file."

    if intent == "build":
        return DIRECT_PREFIX + "Build it in a candidate file, compile it, then test it."

    if intent == "support":
        return DIRECT_PREFIX + "We’ll handle it one safe step at a time."

    return ""


def generate_base_response(text, intent):
    direct = generate_direct_response(text, intent)
    if direct:
        return direct
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

    if intent == "unclear":
        return fallback(text)

    return pick(RESP_CONVERSATION)


RESP_QUESTION = [
    "Start from the file you actually run. That file decides the whole chain.",
    "The clean answer is to follow the active path downward, not inspect every file at once.",
    "The safe way is staged copies first, then import tests, then wiring.",
    "If we keep old files untouched and only point imports at the new file, nothing gets lost.",
]


def generate_candidates(text, intent):
    direct = generate_direct_response(text, intent)
    if direct:
        return [direct]

    if not FEATURES["multi_response"]:
        return [generate_base_response(text, intent)]

    candidates = []

    for _ in range(4):
        candidates.append(generate_base_response(text, intent))

    if FEATURES["conversation_chaining"] and STATE["last_topic"] and intent in ["conversation", "unclear"]:
        candidates.append(
            f"Still connected to {STATE['last_topic']} — we keep that thread alive and make the next move clean."
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

    if 6 <= len(words) <= 34:
        score += 3

    if len(words) > 45:
        score -= 2

    if "file" in response.lower() and intent in ["debug", "build"]:
        score += 2

    if "clean" in response.lower():
        score += 1

    if "safe" in response.lower() or "stable" in response.lower():
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
# PERSONALITY SHAPING
# =========================

def prevent_repeat(response):
    if not FEATURES["anti_repeat"]:
        return response

    if response == STATE["last_response"]:
        return response + " Same direction, cleaner version."

    if response in STATE["responses"][-3:]:
        return response + " Let me say that another way."

    return response


def apply_mood_shape(response):
    mood = STATE["mood"]
    energy = STATE["energy"]

    if mood == "supportive":
        response = response.replace(" — ", "... ")

    elif mood == "focused":
        response = response.replace("…", ".")
        response = response.replace("Okay —", "Okay.")

    elif mood == "creative":
        if random.random() < 0.35:
            response = "Big picture: " + response

    if energy > 1.1:
        response = response.replace(". ", "! ")

    elif energy < 0.8:
        response = response.replace("!", ".")
        response = response.lower()

    return response


def shape_response(response):
    if not response:
        response = fallback(STATE["last_input"])

    if response.startswith(DIRECT_PREFIX):
        return clean_text(response[len(DIRECT_PREFIX):])

    response = clean_text(response)
    response = prevent_repeat(response)

    if FEATURES["personality_hooks"] and random.random() < 0.58:
        response = f"{pick(HOOK_START)} {response}"

    if FEATURES["mid_hooks"]:
        words = response.split()
        if 8 <= len(words) <= 25 and random.random() < 0.16:
            words.insert(len(words) // 2, pick(HOOK_MID))
            response = " ".join(words)

    if FEATURES["end_hooks"] and random.random() < 0.3:
        response = f"{response} {pick(HOOK_END)}"

    response = apply_mood_shape(response)
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
        "response": response,
        "text": text,
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
        "active_subject": STATE["active_subject"],
        "previous_subject": STATE["previous_subject"],
        "last_dialogue_act": STATE["last_dialogue_act"],
        "follow_up_count": STATE["follow_up_count"],
        "context_frames": STATE["context_frames"][-5:],
        "mood": STATE["mood"],
        "energy": STATE["energy"],
        "memory_available": MEMORY_AVAILABLE,
        "tools_available": TOOLS_AVAILABLE,
        "topics": STATE["topics"][-5:],
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
        "ok",
    ]

    for item in tests:
        print("USER:", item)
        print("BOT :", think(item))
        print()

    print("STATUS:", status())
