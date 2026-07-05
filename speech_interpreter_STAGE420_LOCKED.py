# ============================================================
# WHISPLAY SPEECH INTERPRETER
# STAGE 310 — SPEECH NORMALISATION AND SAFETY CANDIDATE
# ============================================================

import re
from copy import deepcopy
from time import time

from cognitive_router_STAGE300_UNIFIED_LOCKED import build_contract


ENGINE_NAME = "speech_interpreter"
ENGINE_STAGE = 310
ENGINE_VERSION = "310.0-candidate"

MIN_RECOGNIZER_CONFIDENCE = 0.45


PHRASE_REPAIRS = {
    "gonna": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "lemme": "let me",
    "kinda": "kind of",
    "sorta": "sort of",
    "ya": "you",
    "yep": "yes",
    "yeah": "yes",
    "nah": "no",
    "nope": "no",
    "whats": "what is",
    "wheres": "where is",
    "hows": "how is",
    "dont": "do not",
    "cant": "cannot",
    "wont": "will not",
}


STATE = {
    "requests": 0,
    "accepted": 0,
    "rejected_low_confidence": 0,
    "repairs_applied": 0,
    "last_raw_text": "",
    "last_clean_text": "",
    "updated": 0.0,
}


def now():
    return time()


def snapshot():
    return deepcopy(STATE)


def clean_raw_text(text):
    if not isinstance(text, str):
        return ""

    cleaned = text.strip().lower()
    cleaned = re.sub(r"[^a-z0-9'\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def repair_words(text):
    words = text.split()
    repaired = []
    repairs = []

    for word in words:
        replacement = PHRASE_REPAIRS.get(word, word)

        if replacement != word:
            repairs.append({
                "original": word,
                "replacement": replacement,
            })

        repaired.extend(replacement.split())

    return " ".join(repaired), repairs


def strip_command_fillers(text):
    words = text.split()

    ignored = {
        "some",
        "just",
        "really",
        "actually",
    }

    return " ".join(
        word for word in words
        if word not in ignored
    )


def strip_leading_fillers(text):
    phrases = (
        "yes mate ",
        "no mate ",
        "yes ",
        "no ",
        "mate ",
        "let me ",
        "please ",
    )

    cleaned = text

    changed = True
    while changed:
        changed = False

        for phrase in phrases:
            if cleaned.startswith(phrase):
                cleaned = cleaned[len(phrase):].strip()
                changed = True
                break

    return cleaned


def interpret_speech(text, recognizer_confidence=None):
    raw_text = text if isinstance(text, str) else ""
    cleaned_text = clean_raw_text(raw_text)
    repaired_text, repairs = repair_words(cleaned_text)
    repaired_text = strip_leading_fillers(repaired_text)
    repaired_text = strip_command_fillers(repaired_text)

    low_confidence = (
        recognizer_confidence is not None
        and recognizer_confidence < MIN_RECOGNIZER_CONFIDENCE
    )

    STATE["requests"] += 1
    STATE["repairs_applied"] += len(repairs)
    STATE["last_raw_text"] = raw_text
    STATE["last_clean_text"] = repaired_text
    STATE["updated"] = now()

    if low_confidence:
        STATE["rejected_low_confidence"] += 1

        return {
            "engine": ENGINE_NAME,
            "stage": ENGINE_STAGE,
            "version": ENGINE_VERSION,
            "timestamp": now(),
            "speech_interpretation": {
                "raw_text": raw_text,
                "cleaned_text": repaired_text,
                "recognizer_confidence": recognizer_confidence,
                "minimum_confidence": MIN_RECOGNIZER_CONFIDENCE,
                "repairs": repairs,
                "accepted": False,
                "reason": "recognizer_confidence_too_low",
            },
            "decision": {
                "route": "clarification",
                "clarification_required": True,
                "clarification": "I did not hear that clearly. Please say it again.",
            },
            "routing": {
                "memory": False,
                "planner": False,
                "safe_fallback": True,
            },
            "source_stages": {
                "speech_interpretation": 310,
            },
            "state_stage310": snapshot(),
        }

    result = build_contract(repaired_text)

    STATE["accepted"] += 1

    result["speech_interpretation"] = {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "raw_text": raw_text,
        "cleaned_text": repaired_text,
        "recognizer_confidence": recognizer_confidence,
        "minimum_confidence": MIN_RECOGNIZER_CONFIDENCE,
        "repairs": repairs,
        "accepted": True,
        "reason": "accepted",
    }

    result["source_stages"]["speech_interpretation"] = 310
    result["state_stage310"] = snapshot()

    return result


def status():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "status": "candidate",
        "state": snapshot(),
    }


if __name__ == "__main__":
    print(
        interpret_speech(
            "Yeah mate, lemme play some music!",
            recognizer_confidence=0.82,
        )
    )
