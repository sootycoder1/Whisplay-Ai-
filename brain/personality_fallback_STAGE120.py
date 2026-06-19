# =========================
# WHISPLAY PERSONALITY + FALLBACK — STAGE 120
# Cohesive companion layer for brain_core_STAGE100/120
# =========================

import random
import re

STATE = {
    "last_topic": "",
    "last_responses": [],
    "mood": "neutral",
    "energy": 1.0,
}

MAX_RESPONSES = 12

HOOK_START = [
    "Alright…", "Okay —", "Right —", "Interesting…", "Yeah —",
    "Look —", "Let me think…", "Here’s the thing —",
    "Okay, so —", "I’ve got you —"
]

HOOK_MID = [
    "that’s the key part",
    "that’s where it matters",
    "that’s the bit to focus on",
    "that’s where it shifts",
    "that’s the core of it",
]

HOOK_END = [
    "That’s the clean version.",
    "That’s where I’d start.",
    "That should keep it stable.",
    "That’s the safer move.",
    "That’s the important part.",
]

FALLBACK_SHORT = [
    "Bit short — give me more.",
    "What exactly do you mean?",
    "Need a bit more detail.",
    "That’s too vague — expand it.",
]

FALLBACK_PARTIAL = [
    "I get part of that — what’s the goal?",
    "What are you trying to do with it?",
    "Give me the outcome you want.",
    "Tell me the result you're aiming for.",
]

FALLBACK_CONTEXT = [
    "Still about {}?",
    "You mean {}?",
    "Same thing — {}?",
]


def clean(text):
    return re.sub(r"\s+", " ", str(text)).strip() if text else ""


def pick(options):
    return random.choice(options) if options else ""


def update_topic(text):
    text = clean(text)

    if text and len(text.split()) > 3:
        STATE["last_topic"] = text


def set_mood(mood="neutral", energy=1.0):
    STATE["mood"] = mood or "neutral"
    STATE["energy"] = float(energy or 1.0)


def fallback(text=""):
    text = clean(text)

    if not text:
        return "Say that again."

    words = text.lower().split()

    if len(words) <= 2:
        return pick(FALLBACK_SHORT)

    if STATE["last_topic"] and random.random() < 0.45:
        return pick(FALLBACK_CONTEXT).format(STATE["last_topic"])

    return pick(FALLBACK_PARTIAL)


def style(text, mood=None, energy=None):
    text = clean(text)

    if mood is not None or energy is not None:
        set_mood(mood or STATE["mood"], energy if energy is not None else STATE["energy"])

    if not text:
        text = fallback(text)

    response = text

    if random.random() < 0.6:
        response = f"{pick(HOOK_START)} {response}"

    if random.random() < 0.22 and len(response.split()) > 7:
        parts = response.split()
        parts.insert(len(parts) // 2, pick(HOOK_MID))
        response = " ".join(parts)

    if random.random() < 0.38:
        response = f"{response} {pick(HOOK_END)}"

    if STATE["mood"] == "supportive":
        response = response.replace("—", "...")

    elif STATE["mood"] == "focused":
        response = response.replace("…", ".")

    if STATE["energy"] > 1.1:
        response = response.replace(".", "!")

    elif STATE["energy"] < 0.8:
        response = response.lower()

    if response in STATE["last_responses"][-3:]:
        response += " Let me say that cleaner."

    STATE["last_responses"].append(response)

    if len(STATE["last_responses"]) > MAX_RESPONSES:
        STATE["last_responses"].pop(0)

    return response


def shape_response(response, user_text="", mood="neutral", energy=1.0):
    update_topic(user_text)
    set_mood(mood, energy)

    if not response:
        response = fallback(user_text)

    return style(response)
