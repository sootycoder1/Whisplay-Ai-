# WHISPLAY UI SMOKE TEST — STAGE 150
# Local display test only.
# Does not start controller.
# Does not start autonomy.
# Does not enable wireless control.

import time
import traceback

print("[UI TEST] starting")

try:
    import display_orchestrator_STAGE9550_RECOVERED as display
    print("[UI TEST] display orchestrator imported")
    print("[UI TEST] module:", display.__file__ if hasattr(display, "__file__") else display)

    funcs = [
        "load_ui",
        "show_idle",
        "show_listening",
        "show_thinking",
        "show_speaking",
        "show_error",
        "status",
    ]

    print("[UI TEST] available display functions:")
    for f in funcs:
        print(" -", f, hasattr(display, f))

    if hasattr(display, "load_ui"):
        print("[UI TEST] calling load_ui()")
        display.load_ui()
        time.sleep(1)

    if hasattr(display, "show_idle"):
        print("[UI TEST] show_idle()")
        display.show_idle()
        time.sleep(1)

    if hasattr(display, "show_listening"):
        print("[UI TEST] show_listening()")
        display.show_listening()
        time.sleep(1)

    if hasattr(display, "show_thinking"):
        print("[UI TEST] show_thinking()")
        display.show_thinking()
        time.sleep(1)

    if hasattr(display, "show_speaking"):
        print("[UI TEST] show_speaking()")
        display.show_speaking("Stage 150 UI test online.")
        time.sleep(2)

    if hasattr(display, "show_idle"):
        print("[UI TEST] back to idle")
        display.show_idle()

    if hasattr(display, "status"):
        print("[UI TEST] status:", display.status())

    print("[UI TEST] PASS")

except Exception as e:
    print("[UI TEST] FAIL:", repr(e))
    traceback.print_exc()
