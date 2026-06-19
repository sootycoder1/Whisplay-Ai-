# =========================
# COGNITIVE CORE — STAGE 250 BRIDGE
# Routes ALL input through incoming_3 personality engine
# =========================

# -------------------------
# DEBUG SAFE
# -------------------------
try:
    from debug import log, error
except:
    def log(x): print(x)
    def error(x): print(x)

# -------------------------
# IMPORT MAIN PERSONALITY ENGINE
# -------------------------
try:
    from incoming_3_STAGE250 import process as personality_process
    log("[COG] Using Stage 250 personality engine")
except Exception as e:
    personality_process = None
    error(f"[COG ERROR] Failed to load personality engine: {e}")


# =========================
# MAIN ENTRY POINT
# =========================

def process_input(text):
    try:
        if not text or not str(text).strip():
            return ""

        # -------------------------
        # ROUTE THROUGH PERSONALITY ENGINE
        # -------------------------
        if personality_process:
            result = personality_process(text)

            # full structured return
            if isinstance(result, dict):
                return result.get("response", "")

            # fallback if string
            return str(result)

        # -------------------------
        # FAILSAFE
        # -------------------------
        return "Brain link missing."

    except Exception as e:
        error(f"[COG PROCESS ERROR] {e}")
        return "Something went wrong."
