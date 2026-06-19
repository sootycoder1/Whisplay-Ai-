# ============================================================
# WHISPLAY COGNITIVE CORE BRIDGE
# Compatibility shim for display_orchestrator_STAGE9500.py
# ============================================================
#
# Purpose:
# - display_orchestrator_STAGE9500.py imports:
#       from cognitive_core import process
#
# - The real cognition engine currently lives at:
#       brain/brain_cognitive_STAGE150_MERGED.py
#
# This bridge keeps old imports working without renaming or moving
# the real cognition file.

try:
    from brain.brain_cognitive_STAGE150_MERGED import process, process_input, think
except Exception as e:
    _COGNITIVE_IMPORT_ERROR = e

    def process(text):
        return f"[cognitive_core unavailable: {_COGNITIVE_IMPORT_ERROR}]"

    def process_input(text):
        return process(text)

    def think(text):
        return process(text)
