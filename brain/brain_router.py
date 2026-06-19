# =========================
# BRAIN ROUTER — STAGE 50 UPGRADED
# INTENT + TOOL + MEMORY + LAYER AWARE
# =========================

try:
    from debug import log
except:
    def log(x): print(x)


# =========================
# KEYWORD BANKS
# =========================

TOOLS = ["shutdown", "restart", "status"]
MEMORY_WORDS = ["remember", "save", "store"]
RECALL_WORDS = ["what is my", "who am i", "recall"]
DEBUG_WORDS = ["error", "broken", "failed", "missing"]
BUILD_WORDS = ["build", "merge", "create", "upgrade"]
SYSTEM_WORDS = ["state", "mode", "status"]


# =========================
# MAIN ROUTER
# =========================

def route(text):
    text = text.lower().strip()

    log(f"[ROUTER] {text}")

    # -------------------------
    # TOOL COMMANDS
    # -------------------------
    for tool in TOOLS:
        if tool in text:
            return {"intent": "tool", "tool": tool}

    # -------------------------
    # MEMORY STORE
    # -------------------------
    if any(word in text for word in MEMORY_WORDS):
        try:
            parts = text.split("remember")[-1].strip()
            if "is" in parts:
                key, value = parts.split("is", 1)
                return {
                    "intent": "memory_store",
                    "key": key.strip(),
                    "value": value.strip()
                }
        except:
            pass

    # -------------------------
    # MEMORY RECALL
    # -------------------------
    if any(word in text for word in RECALL_WORDS):
        key = text.replace("what is my", "").strip()
        return {
            "intent": "memory_recall",
            "key": key
        }

    # -------------------------
    # DEBUG INTENT
    # -------------------------
    if any(word in text for word in DEBUG_WORDS):
        return {"intent": "debug"}

    # -------------------------
    # BUILD INTENT
    # -------------------------
    if any(word in text for word in BUILD_WORDS):
        return {"intent": "build"}

    # -------------------------
    # SYSTEM INTENT
    # -------------------------
    if any(word in text for word in SYSTEM_WORDS):
        return {"intent": "system"}

    # -------------------------
    # SHORT INPUT
    # -------------------------
    if len(text.split()) <= 1:
        return {"intent": "unclear"}

    # -------------------------
    # DEFAULT
    # -------------------------
    return {"intent": "conversation"}
