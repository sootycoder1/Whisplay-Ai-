# =========================
# WHISPLAY COGNITIVE CORE — STAGE 150 (FULL)
# =========================

import time


# -------------------------
# DEBUG SAFE
# -------------------------
try:
    from debug import log, error
except Exception:
    def log(x): print(x)
    def error(x): print(x)


# -------------------------
# IMPORTS
# -------------------------
try:
    from brain.router import route
except Exception:
    route = None

try:
    from brain.generate_response import generate_response
except Exception:
    def generate_response(text):
        return "I can't respond right now."


# -------------------------
# CONFIG
# -------------------------
MAX_INPUT_LENGTH = 500
CONFIDENCE_DEFAULT = 0.7


# -------------------------
# STATE
# -------------------------
AWARENESS = {"pressure": 0.0, "ambiguity": 0.0, "stability": 1.0}
MUTATION = {"verbosity_bias": 0.0, "confidence_bias": 0.0, "clarity_bias": 0.0}

IDENTITY = {"tone": "neutral", "consistency": 1.0, "engagement": 0.5}
SESSION = {"last_intent": None, "interaction_count": 0}

FAIL_COUNT = 0


# =========================
# MAIN PROCESS
# =========================
def process_input(text):

    global FAIL_COUNT

    try:
        if not text:
            return ""

        text = _sanitize(text)
        log(f"[COG] Input: {text}")

        _update_awareness(text)
        _identity_update(text)

        decision = _route_input(text)
        _continuity_update(decision)

        if not decision:
            return _fallback(text)

        intent = decision.get("intent", "conversation")
        confidence = decision.get("confidence", CONFIDENCE_DEFAULT)

        try:
            confidence = float(confidence)
        except:
            confidence = CONFIDENCE_DEFAULT

        # EXECUTION
        if intent == "conversation":
            response = _handle_conversation(text)
        else:
            response = _handle_other(decision)

        # MUTATION
        response = _apply_mutation(response, confidence)

        # EVALUATION
        score = _evaluate_response(text, response, confidence)
        _update_from_evaluation(score)

        if score < 0.2:
            FAIL_COUNT += 1

        # IDENTITY (FINAL)
        response = _apply_identity(response)

        # OUTPUT
        return _safe_output(response)

    except Exception as e:
        error(f"[COG CRASH] {e}")
        return _emergency_response()

# =========================
# CORE HELPERS
# =========================

def _sanitize(text):
    return str(text).strip()[:MAX_INPUT_LENGTH]


def _route_input(text):
    try:
        if route:
            return route(text)
    except Exception as e:
        error(f"[ROUTER ERROR] {e}")
    return {"intent": "conversation", "confidence": 0.5}


def _handle_conversation(text):
    try:
        return generate_response(text)
    except:
        return "Thinking error."


def _handle_other(decision):
    return "Unhandled intent."


def _fallback(text):
    return generate_response(text)


def _safe_output(text):
    return str(text or "").strip()


def _emergency_response():
    return "Something went wrong — but I’m still here."


# =========================
# MUTATION
# =========================

def _apply_mutation(response, confidence):

    try:
        confidence = float(confidence)
    except:
        confidence = CONFIDENCE_DEFAULT

    words = response.split()

    if MUTATION["verbosity_bias"] < -0.5:
        response = " ".join(words[:8])

    if MUTATION["confidence_bias"] + confidence < 0.4:
        response = f"I think {response}"

    if MUTATION["clarity_bias"] > 0.6:
        response = f"{response} — can you expand on that?"

    return response

# =========================
# AWARENESS
# =========================

def _update_awareness(text):

    if len(text.split()) <= 2:
        AWARENESS["ambiguity"] += 0.1
    else:
        AWARENESS["ambiguity"] *= 0.9

    AWARENESS["pressure"] *= 0.95
    AWARENESS["stability"] = min(1.0, AWARENESS["stability"] + 0.02)

    _clamp(AWARENESS)


# =========================
# EVALUATION
# =========================

def _evaluate_response(input_text, response, confidence):

    try:
        confidence = float(confidence)
    except:
        confidence = CONFIDENCE_DEFAULT

    score = 1.0

    if len(response.split()) < 2:
        score -= 0.3

    if input_text.lower() in response.lower():
        score -= 0.2

    if confidence > 0.8 and "I think" in response:
        score -= 0.2

    if confidence < 0.4 and not response.startswith("I think"):
        score -= 0.2

    if AWARENESS["ambiguity"] > 0.6 and "?" not in response:
        score -= 0.2

    return max(0.0, min(1.0, score))

# =========================
# IDENTITY + CONTINUITY
# =========================
def _identity_update(text):

    SESSION["interaction_count"] += 1

    if len(text.split()) <= 2:
        IDENTITY["engagement"] += 0.05
    else:
        IDENTITY["engagement"] *= 0.98

    _clamp(IDENTITY)

def _continuity_update(decision):

    intent = decision.get("intent", "unknown")

    if intent == SESSION["last_intent"]:
        IDENTITY["consistency"] += 0.02
    else:
        IDENTITY["consistency"] *= 0.95

    SESSION["last_intent"] = intent

    _clamp(IDENTITY)


def _apply_identity(response):

    if not response:
        return ""

    if IDENTITY["consistency"] < 0.4:
        response = f"I might be off, but {response}"

    return response


# =========================
# UTIL
# =========================

def _clamp(state):
    for k in state:
        state[k] = max(0.0, min(1.0, state[k]))

# =========================
# IDENTITY UPDATE
# =========================
def _apply_identity(response):

    if not response:
        return ""

    if IDENTITY["consistency"] < 0.4:
        response = f"I might be off, but {response}"

    return response


# =========================
# UTIL
# =========================

def _clamp(state):
    for k in state:
        state[k] = max(0.0, min(1.0, state[k]))
