# ============================================================
# WHISPLAY — INCOMING_3 STAGE 250
# Adaptive Personality Engine
# Anti-Repeat / Energy System / Conversation Flow
# ============================================================

import random
import time

from datetime import datetime

from brain import think


# ============================================================
# STATE
# ============================================================

MODE = "casual"

ENERGY = 1.0

MOOD = "neutral"

_last_response = ""

_memory = []

MAX_MEMORY = 20

REPEAT_GUARD_TIME = 1.2

_last_time = 0


# ============================================================
# PERSONALITY BANK
# ============================================================

HOOK_START = [

    "Yeah—",
    "Alright—",
    "Right—",
    "Okay—",
    "Look—",
    "Mate—",
    "",
]


HOOK_END = [

    "",
    "—done.",
    "easy.",
    "sorted.",
    "that’s it.",
]


FILLERS = [

    "yeah nah",
    "nah yeah",
    "to be fair",
    "bit of both really",
    "depends how you look at it",
]


QUESTION_BACKS = [

    "What’s the move?",
    "You building that or testing it?",
    "Where are you taking this?",
    "What’s the end goal?",
]


FALLBACKS = [

    "That didn’t land. Try again.",
    "Say that cleaner.",
    "I’m close but not there yet.",
    "Run that again properly.",
]


# ============================================================
# CLEAN
# ============================================================

def clean(text):

    return " ".join(

        str(text).strip().split()

    ) if text else ""


# ============================================================
# INTENT
# ============================================================

def detect_intent(text):

    t = clean(text).lower()


    if not t:
        return "empty"


    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if any(

        w in t

        for w in [
            "hello",
            "hey",
            "hi",
        ]
    ):
        return "greeting"


    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    if "time" in t:
        return "time"

    if "who are you" in t:
        return "identity"

    if "system" in t:
        return "system"

    if "remember" in t:
        return "memory"


    # --------------------------------------------------------
    # MODE SWITCHING
    # --------------------------------------------------------

    if "serious" in t:
        return "mode_serious"

    if "calm" in t:
        return "mode_casual"

    if "edge" in t or "blunt" in t:
        return "mode_edge"


    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    if "?" in t:
        return "question"


    # --------------------------------------------------------
    # SHORT INPUT
    # --------------------------------------------------------

    if len(t.split()) <= 2:
        return "short"


    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "conversation"


# ============================================================
# MEMORY
# ============================================================

def remember(user, response, intent):

    _memory.append({

        "u": user,

        "r": response,

        "i": intent,
    })


    if len(_memory) > MAX_MEMORY:

        _memory.pop(0)


def topic_loop():

    if len(_memory) < 5:
        return False


    words = []


    for m in _memory[-5:]:

        words += m["u"].lower().split()


    unique = set([

        w for w in words

        if len(w) > 4

    ])


    return len(unique) < 5


# ============================================================
# RESPONSE MUTATION
# ============================================================

def mutate(text):

    variants = [

        text,

        text.replace("you", "ya"),

        text.replace(
            "that",
            "that thing"
        ),

        text + ".",

        text.replace(
            "is",
            "is kinda"
        ),
    ]


    return random.choice(variants)


# ============================================================
# PERSONALITY ENGINE
# ============================================================

def apply_personality(text, intent):

    global MODE
    global ENERGY


    text = clean(text)


    # --------------------------------------------------------
    # SERIOUS MODE
    # --------------------------------------------------------

    if MODE == "serious":

        return text


    # --------------------------------------------------------
    # HOOK SCALING
    # --------------------------------------------------------

    if random.random() < (

        0.4 + ENERGY * 0.3

    ):

        start = random.choice(
            HOOK_START
        )

        if start:

            text = f"{start} {text}"


    # --------------------------------------------------------
    # FILLERS
    # --------------------------------------------------------

    if random.random() < (

        0.15 + ENERGY * 0.2

    ):

        text = (

            f"{random.choice(FILLERS)}, "
            f"{text}"

        )


    # --------------------------------------------------------
    # QUESTION CHAINING
    # --------------------------------------------------------

    if random.random() < 0.35:

        text += (
            " "
            + random.choice(
                QUESTION_BACKS
            )
        )


    # --------------------------------------------------------
    # EDGE MODE
    # --------------------------------------------------------

    if (

        MODE == "edge"

        and random.random() < 0.3

    ):

        text += " Don’t overthink it."


    # --------------------------------------------------------
    # ENDING
    # --------------------------------------------------------

    if random.random() < 0.3:

        text += (
            " "
            + random.choice(
                HOOK_END
            )
        )


    return text.strip()


# ============================================================
# GENERATE
# ============================================================

def generate(text):

    global MODE


    intent = detect_intent(text)


    # --------------------------------------------------------
    # BUILT-IN RESPONSES
    # --------------------------------------------------------

    if intent == "greeting":

        return (
            "Yeah I’m here.",
            intent
        )


    if intent == "time":

        return (
            datetime.now().strftime(
                "It’s %H:%M."
            ),
            intent
        )


    if intent == "identity":

        return (
            "I’m Whisplay. Local. No cloud.",
            intent
        )


    if intent == "system":

        return (
            "Everything’s running.",
            intent
        )


    # --------------------------------------------------------
    # MODE CHANGES
    # --------------------------------------------------------

    if intent == "mode_serious":

        MODE = "serious"

        return (
            "Serious mode.",
            intent
        )


    if intent == "mode_casual":

        MODE = "casual"

        return (
            "Back to casual.",
            intent
        )


    if intent == "mode_edge":

        MODE = "edge"

        return (
            "Alright. I’ll be blunt.",
            intent
        )


    # --------------------------------------------------------
    # SHORT INPUT
    # --------------------------------------------------------

    if intent == "short":

        return (
            random.choice(FALLBACKS),
            intent
        )


    # --------------------------------------------------------
    # MAIN THINK
    # --------------------------------------------------------

    base = think(text)


    if not base:

        base = (
            f"I heard {text}. "
            f"Keep going."
        )


    return base, intent


# ============================================================
# MAIN PROCESS
# ============================================================

def process(text):

    global _last_response
    global _last_time
    global ENERGY
    global MOOD


    now = time.time()

    text = clean(text)


    # --------------------------------------------------------
    # EMPTY INPUT
    # --------------------------------------------------------

    if not text:

        return {

            "action": "ignore"
        }


    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    base, intent = generate(text)


    # --------------------------------------------------------
    # ENERGY SYSTEM
    # --------------------------------------------------------

    if intent == "short":

        ENERGY *= 0.95

    else:

        ENERGY *= 1.05


    ENERGY = max(

        0.6,

        min(1.6, ENERGY)
    )


    # --------------------------------------------------------
    # TOPIC LOOP DETECTION
    # --------------------------------------------------------

    if topic_loop():

        base += (
            " You’re circling "
            "the same thing."
        )


    # --------------------------------------------------------
    # ANTI-REPEAT
    # --------------------------------------------------------

    recent = [

        m["r"]

        for m in _memory[-5:]
    ]


    if base in recent:

        base = mutate(base)


    if (

        base == _last_response

        and

        (now - _last_time)
        < REPEAT_GUARD_TIME
    ):

        base = mutate(base)


    # --------------------------------------------------------
    # PERSONALITY LAYER
    # --------------------------------------------------------

    final = apply_personality(
        base,
        intent
    )


    remember(
        text,
        final,
        intent
    )


    _last_response = final

    _last_time = now


    return {

        "action": "respond",

        "response": final,

        "intent": intent,

        "mode": MODE,

        "energy": round(
            ENERGY,
            2
        ),

        "time": now,
    }
