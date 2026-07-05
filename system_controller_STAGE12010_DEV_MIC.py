# ============================================================
# WHISPLAY SYSTEM CONTROLLER — STAGE 12000 CORE
# Stable Runtime Backbone + Clean Orchestration
# ============================================================

import os
import sys
import threading
import time
import traceback

BASE_DIR = os.path.expanduser("~/whisplay-ai")
sys.path.append(BASE_DIR)

ENGINE_NAME = "system_controller"
ENGINE_STAGE = 12000
ENGINE_VERSION = "12.0.0"

# ============================================================
# DEBUG SAFE
# ============================================================

try:
    from debug import log, error
except Exception:
    def log(msg):
        print(msg)

    def error(msg):
        print(msg)

GPIO_ENABLED = False

# GPIO governance:
# - Allow display driver to use normal GPIO setup/PWM for rendering/backlight.
# - Block GPIO edge interrupts so buttons cannot arm/control the system.
# - gpiozero remains blocked.
if not GPIO_ENABLED:
    try:
        import RPi.GPIO as _REAL_GPIO

        def _blocked_event_detect(*args, **kwargs):
            print("[GPIO EDGE BLOCKED] controller blocked add_event_detect")
            return None

        _REAL_GPIO.add_event_detect = _blocked_event_detect
        sys.modules['RPi.GPIO'] = _REAL_GPIO
    except Exception:
        class _GPIO_BLOCK:
            def __getattr__(self, name):
                raise RuntimeError("GPIO is LOCKED — access blocked")
        sys.modules['RPi.GPIO'] = _GPIO_BLOCK()

    class _GPIOZERO_BLOCK:
        def __getattr__(self, name):
            raise RuntimeError("gpiozero is LOCKED — access blocked")

    sys.modules['gpiozero'] = _GPIOZERO_BLOCK()
# ============================================================
# SAFE RUNTIME CONTRACT
# ============================================================

try:
    from runtime_contract_STAGE6000 import RuntimeState, Event, EventPriority
except Exception:
    class RuntimeState:
        BOOTING = "booting"
        IDLE = "idle"
        LISTENING = "listening"
        THINKING = "thinking"
        SPEAKING = "speaking"
        RECOVERING = "recovering"
        ERROR = "error"
        SHUTDOWN = "shutdown"

    class Event:
        SYSTEM_BOOT = "system.boot"
        SYSTEM_READY = "system.ready"
        SYSTEM_ERROR = "system.error"
        SYSTEM_HEARTBEAT = "system.heartbeat"
        SYSTEM_SHUTDOWN = "system.shutdown"
        SPEECH_HEARD = "speech.heard"
        SPEECH_OUTPUT = "speech.output"

    class EventPriority:
        HIGH = type("", (), {"value": 1})()
        NORMAL = type("", (), {"value": 2})()


# ============================================================
# EVENT COMPATIBILITY PATCH
# ============================================================

if not hasattr(Event, "SPEECH_OUTPUT"):
    Event.SPEECH_OUTPUT = "speech.output"


# ============================================================
# SAFE RUNTIME BUS
# ============================================================

try:
    import runtime_bus_STAGE7000 as runtime_bus
except Exception as e:
    runtime_bus = None
    print("[SYS12000] runtime bus unavailable:", e)


# ============================================================
# SAFE STATE ENGINE
# ============================================================

try:
    from state_engine_STAGE220 import state
except Exception:
    try:
        from state_engine import state
    except Exception:
        class DummyState:
            def __init__(self):
                self.current = "idle"

            def set(self, value):
                print(f"[STATE] {self.current} -> {value}")
                self.current = value

            def get(self):
                return self.current

        state = DummyState()

# ============================================================
# SAFE BRAIN ENGINE
# ============================================================

try:
    from brain.brain_cognitive_STAGE220_COMBINED_CANDIDATE import process as brain_process
except Exception as e:
    error(f"[BRAIN IMPORT ERROR] {e}")

    def brain_process(text):
        return {
            "action": "respond",
            "response": "Brain unavailable.",
            "intent": "error",
            "mood": "neutral",
            "energy": 1.0,
        }


# ============================================================
# SAFE SPEECH ENGINE
# ============================================================

try:
    from speak import speak, stop, is_speaking
except Exception:
    def speak(text):
        print("[VOICE]", text)

    def stop():
        pass

    def is_speaking():
        return False


# ============================================================
# SAFE SUBSYSTEM IMPORTS
# ============================================================

SUBSYSTEM_IMPORTS = {}

for name, module_name in [
    ("context_manager", "context_manager_STAGE6500"),
    ("memory_engine", "memory_engine_STAGE7500"),
    ("goal_engine", "goal_engine_STAGE8000"),
    ("reasoning_engine", "reasoning_engine_STAGE8500"),
    ("adapter_manager", "adapter_manager_STAGE9000"),
    ("display_orchestrator", "display_orchestrator_STAGE9550_RECOVERED"),
    ("persistent_speech_worker", "persistent_speech_worker_STAGE10500"),
    ("analysis_core", "analysis_core_STAGE11500"),
]:
    try:
        SUBSYSTEM_IMPORTS[name] = __import__(module_name)
    except Exception as e:
        print(f"[SYS12000] {name} unavailable:", e)


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "status": "offline",
    "runtime_state": RuntimeState.BOOTING,
    "running": False,
    "booting": False,
    "recovering": False,

    "heartbeat": 0,
    "runtime_cycles": 0,

    "subsystems_online": 0,
    "subsystems_failed": 0,

    "turns": 0,
    "errors": 0,

    "last_input": "",
    "last_response": "",
    "last_intent": "",
    "last_event": None,
    "last_error": None,

    "mood": "neutral",
    "energy": 1.0,

    "boot_time": 0.0,
    "created": time.time(),
    "updated": time.time(),
}

MEMORY = {
    "events": [],
    "errors": [],
    "turns": [],
    "subsystems": [],
}

SYSTEMS = {}


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def remember(category, value, limit=100):
    if category not in MEMORY:
        return

    MEMORY[category].append(value)
    MEMORY[category] = MEMORY[category][-limit:]


def emit_event(event_name, payload=None, priority=None):
    if runtime_bus is None:
        return False

    try:
        if hasattr(event_name, "value"):
            event_name = event_name.value

        if priority is None:
            priority = EventPriority.NORMAL.value

        try:
            runtime_bus.emit(
                event_name,
                payload=payload or {},
                source=ENGINE_NAME,
                target="broadcast",
                priority=priority,
            )

        except TypeError:
            runtime_bus.emit(
                event_name,
                payload=payload or {},
                source=ENGINE_NAME,
                target="broadcast",
            )

        STATE["last_event"] = event_name
        remember("events", event_name)

        return True

    except Exception as e:
        STATE["last_error"] = str(e)
        remember("errors", str(e))
        return False

# =========================
# AUTONOMY200 BRIDGE START
# Read-only observer bridge.
# Stage 200 may observe/suggest only.
# It must not control GPIO, SPI, audio, display, SSH, brain mutation, or controller replacement.
# =========================
try:
    import autonomy_supervisor_STAGE200 as _autonomy200
    try:
        _autonomy200.start()
    except Exception:
        pass
    print("[AUTONOMY200] observe-only bridge loaded")
except Exception as _autonomy200_error:
    _autonomy200 = None
    print("[AUTONOMY200] bridge unavailable:", _autonomy200_error)

def autonomy200_observe(kind, value=""):
    """Send safe read-only observations to Stage 200. Never executes actions."""
    try:
        if _autonomy200 is None:
            return None

        if kind == "runtime":
            return _autonomy200.observe_runtime(str(value))

        if kind == "input":
            return _autonomy200.observe_input(str(value))

        if kind == "output":
            return _autonomy200.observe_output(str(value))

        if kind == "error":
            return _autonomy200.observe_error(str(value))

        return None

    except Exception as e:
        print("[AUTONOMY200] observe failed:", e)
        return None

def autonomy200_status():
    """Return Stage 200 status read-only. Never executes actions."""
    try:
        if _autonomy200 is None:
            return {"online": False, "stage": 200, "status": "unavailable"}
        return _autonomy200.status()
    except Exception as e:
        return {"online": False, "stage": 200, "status": "error", "error": str(e)}

# =========================
# AUTONOMY200 BRIDGE END
# =========================



def stage200_core_status():
    """Read-only Stage 200 core law/bus/state visibility. Never executes actions."""
    out = {
        "ok": True,
        "controller_role": "orchestration_only",
        "safe_point": "STAGE200_CORE_LAW_BUS_STATE_VISIBLE_OK",
        "controller_can_reason": False,
        "controller_can_replace_brain": False,
        "controller_can_apply_autonomy": False,
        "gpio_enabled": GPIO_ENABLED,
    }

    try:
        import runtime_contract_STAGE6000 as contract
        out["contract"] = contract.stage200_contract_status()
    except Exception as e:
        out["contract"] = {"ok": False, "error": str(e)}

    try:
        import runtime_bus_STAGE7000 as bus
        out["bus"] = bus.stage200_bus_status()
    except Exception as e:
        out["bus"] = {"ok": False, "error": str(e)}

    try:
        import state_core as state
        out["state"] = state.stage200_state_status()
    except Exception as e:
        out["state"] = {"ok": False, "error": str(e)}

    return out

class SystemController:

    def __init__(self):
        self.cooldown = 0.02
        self.max_history = 20
        self.safe_mode = False

        STATE["boot_time"] = now()
        STATE["booting"] = True
        STATE["runtime_state"] = RuntimeState.BOOTING

        log("[SYS12000] controller initialized")

    # ========================================================
    # BOOT
    # ========================================================

    def boot(self):
        log("[SYS12000] boot sequence started")

        try:
            # ------------------------------------------------
            # CONTRACT AUTHORITY GATE
            # Contract must validate before bus/subsystems boot.
            # ------------------------------------------------
            import runtime_contract_STAGE6000 as contract

            validation = contract.validate_contract()
            authority = contract.stage200_contract_status()

            if validation.get("ok") is not True:
                raise RuntimeError(
                    f"contract validation failed: "
                    f"{validation.get('errors', [])}"
                )

            if authority.get("final_authority") != "user":
                raise RuntimeError(
                    "contract authority violation: user is not final authority"
                )

            if authority.get("autonomy_readonly") is not True:
                raise RuntimeError(
                    "contract authority violation: autonomy is not read-only"
                )

            if authority.get("autonomy_controls_hardware") is not False:
                raise RuntimeError(
                    "contract authority violation: autonomy hardware control enabled"
                )

            if authority.get("gpio_global_control") is not False:
                raise RuntimeError(
                    "contract authority violation: GPIO global control enabled"
                )

            if authority.get("spi_global_control") is not False:
                raise RuntimeError(
                    "contract authority violation: SPI global control enabled"
                )

            log(
                "[SYS12000] contract authority verified: "
                f"{validation.get('version')}"
            )

            try:
                from mic_input_adapter import warm_model

                threading.Thread(
                    target=warm_model,
                    name="vosk-model-warm",
                    daemon=True,
                ).start()

                log("[SYS12000] microphone model warm-up started")
            except Exception as e:
                log(f"[SYS12000] microphone warm-up unavailable: {e}")

            if runtime_bus:
                runtime_bus.start()
                emit_event(Event.SYSTEM_BOOT, priority=EventPriority.HIGH.value)

            self.load_subsystems()

            STATE["running"] = True
            STATE["booting"] = False
            STATE["status"] = "online"
            STATE["runtime_state"] = RuntimeState.IDLE

            emit_event(Event.SYSTEM_READY, priority=EventPriority.HIGH.value)

            log("[SYS12000] runtime online")

            self.run()

        except Exception as e:
            self.register_error("BOOT", e)
            traceback.print_exc()

    # ========================================================
    # SUBSYSTEMS
    # ========================================================

    def load_subsystems(self):
        log("[SYS12000] loading subsystems")

        for name, module in SUBSYSTEM_IMPORTS.items():
            try:
                SYSTEMS[name] = module
                MEMORY["subsystems"].append(name)
                STATE["subsystems_online"] += 1
                log(f"[SYS12000] subsystem loaded: {name}")

            except Exception as e:
                STATE["subsystems_failed"] += 1
                self.register_error(f"SUBSYSTEM {name}", e)

    # ========================================================
    # STATUS
    # ========================================================

    def uptime(self):
        return int(now() - STATE["boot_time"])

    def status(self):
        return {
            "engine": ENGINE_NAME,
            "stage": ENGINE_STAGE,
            "version": ENGINE_VERSION,
            "status": STATE["status"],
            "runtime_state": STATE["runtime_state"],
            "turns": STATE["turns"],
            "errors": STATE["errors"],
            "heartbeat": STATE["heartbeat"],
            "cycles": STATE["runtime_cycles"],
            "subsystems_online": STATE["subsystems_online"],
            "subsystems_failed": STATE["subsystems_failed"],
            "autonomy200": autonomy200_status(),
            "stage200_core": stage200_core_status(),
            "mood": STATE["mood"],
            "energy": STATE["energy"],
            "uptime": self.uptime(),
        }

    # ========================================================
    # ERRORS / RECOVERY
    # ========================================================

    def register_error(self, label, exc):
        STATE["errors"] += 1
        STATE["last_error"] = f"{label}: {exc}"

        remember("errors", STATE["last_error"])

        error(f"[{label} ERROR] {exc}")

        if STATE["errors"] >= 25:
            self.recover("too many errors")

    def recover(self, reason="unknown"):
        STATE["recovering"] = True
        STATE["runtime_state"] = RuntimeState.RECOVERING

        log(f"[SYS12000] recovery triggered: {reason}")

    # --------------------------------------------------------
    # 1. CLASSIFY ERROR TYPE
    # --------------------------------------------------------
    error_text = str(STATE.get("last_error", "")).lower()

    if "mic" in error_text or "audio" in error_text:
        recovery_type = "audio"
    elif "display" in error_text:
        recovery_type = "display"
    elif "brain" in error_text:
        recovery_type = "brain"
    elif "bus" in error_text or "event" in error_text:
        recovery_type = "runtime"
    else:
        recovery_type = "general"

    log(f"[RECOVERY] type: {recovery_type}")

    # --------------------------------------------------------
    # 2. TARGETED RESPONSE
    # --------------------------------------------------------

    try:
        if recovery_type == "audio":
            log("[RECOVERY] resetting audio state")
            try:
                stop()
            except:
                pass

        elif recovery_type == "display":
            log("[RECOVERY] display issue - skipping frame")
            # do nothing, avoid crash loop

        elif recovery_type == "brain":
            log("[RECOVERY] brain fallback engaged")
            STATE["last_response"] = "System stabilising."

        elif recovery_type == "runtime":
            log("[RECOVERY] restarting runtime bus")
            try:
                if runtime_bus:
                    runtime_bus.stop()
                    runtime_bus.start()
            except Exception as e:
                log(f"[RECOVERY] bus restart failed: {e}")

    except Exception as e:
        log(f"[RECOVERY ERROR] {e}")

    # --------------------------------------------------------
    # 3. STABILISE SYSTEM
    # --------------------------------------------------------

    # reset volatile state
    STATE["recovering"] = False
    STATE["runtime_state"] = RuntimeState.IDLE

    # prevent runaway loops
    time.sleep(0.01)

    log("[SYS12000] recovery complete")

    # ========================================================
    # INPUT
    # ========================================================

    def get_input(self):
        #Dual-mode input (battery-friendly):
        #- Typed input always works
        #- Push-to-talk: type m/mic/ptt to listen once
        #- Hands-free (blank Enter): listen once but require wake aliases  
        WAKE_ALIASES = [
            "whisplay",
            "whis play",
            "wisplay",
            "wis play",
            "we play",
            "was play",
            "with play",
            "with boy",
            "with ploy",
            "wiz play",
            "whisply",
        ]

        try:
            cmd = input("YOU > ").strip()

            # Push-to-talk override flag
            force_accept = False
            if cmd.lower() in ["m", "mic", "ptt"]:
                force_accept = True
                cmd = ""  # fall through to mic listen
                print("[MIC] listening...")

            # If they typed normal text/command, return it immediately
            if cmd:
                return cmd

            # Mic listen path (blank Enter OR m/mic/ptt)
            try:
                from mic_input_adapter import listen_once
                heard = (listen_once(timeout_s=8.0) or "").strip()

                if not heard:
                    print("[MIC] nothing heard")
                    return ""

                # Drop tiny junk (TV noise often returns 1 word like "with")
                if len(heard.split()) < 2:
                    print("[MIC] too short:", repr(heard))
                    return ""

                print("YOU(MIC) >", heard)

                # PTT override: accept whatever was heard (no wake gate)
                if force_accept:
                    return heard

                # Wake word gate (aliases) for blank-enter hands-free mode
                heard_l = heard.lower()
                if any(w in heard_l for w in WAKE_ALIASES):
                    cleaned = heard_l
                    for w in WAKE_ALIASES:
                        cleaned = cleaned.replace(w, "")
                    cleaned = cleaned.strip(" ,.!?")
                    return cleaned if cleaned else ""

                return ""

            except Exception:
                return ""

        except EOFError:
            return ""
        except KeyboardInterrupt:
            STATE["running"] = False
            return ""

    # ========================================================
    # COMMANDS
    # ========================================================

    def handle_command(self, text):
        t = str(text).lower().strip()

        if t in ["quit", "exit", "shutdown", "stop controller"]:
            STATE["running"] = False
            return "Controller shutting down cleanly."

        if t in ["status", "system status", "runtime status"]:
            return str(self.status())

        if t == "safe mode":
            self.safe_mode = True
            return "Safe mode enabled."

        if t == "runtime mode":
            self.safe_mode = False
            return "Runtime mode enabled."

        return None

    # ========================================================
    # BRAIN EXECUTION
    # ========================================================

    def execute_brain(self, text):

        # AUTONOMY200_EXECUTE_BRAIN_INPUT

        autonomy200_observe('input', text)

        autonomy200_observe('runtime', 'thinking')
        try:
            result = brain_process(text)

            if not isinstance(result, dict):
                return "Invalid brain response."

            response = result.get("response", "")

            STATE["last_intent"] = result.get("intent", "unknown")
            STATE["mood"] = result.get("mood", "neutral")
            STATE["energy"] = result.get("energy", 1.0)

            return response

        except Exception as e:
            self.register_error("BRAIN", e)
            traceback.print_exc()
            return "Brain execution failure."

    # ========================================================
    # OUTPUT
    # ========================================================

    def output(self, response):
        print("[AI]", response)
        # AUTONOMY200_AI_OUTPUT
        autonomy200_observe('output', response)
        autonomy200_observe('runtime', 'speaking')

        emit_event(
            Event.SPEECH_OUTPUT,
            payload={"text": response},
        )

        # DISPLAY BYPASS:
        # GPIO is locked by governance. Do not initialise Whisplay HAT display here.
        # Brain/controller proof run continues without display hardware.
        try:
            display = SYSTEMS.get("display_orchestrator")

            if display and hasattr(display, "show_speaking"):
                display.show_speaking(response)

        except Exception as e:
            self.register_error("DISPLAY OUTPUT", e)

        try:
            speak(response)
        except Exception as e:
            self.register_error("SPEAK", e)

    # ========================================================
    # MEMORY
    # ========================================================

    def remember_turn(self, user, response):
        turn = {
            "user": user,
            "response": response,
            "intent": STATE["last_intent"],
            "time": now(),
        }

        remember("turns", turn, limit=self.max_history)

    # ========================================================
    # HEARTBEAT / MONITORING
    # ========================================================

    def heartbeat(self):
        STATE["heartbeat"] += 1
        STATE["runtime_cycles"] += 1
        STATE["updated"] = now()

        if STATE["heartbeat"] % 50 == 0:
            emit_event(
                Event.SYSTEM_HEARTBEAT,
                payload={
                    "heartbeat": STATE["heartbeat"],
                    "uptime": self.uptime(),
                },
            )

    def monitor_runtime(self):
        if STATE["errors"] >= 25:
            self.recover("error threshold reached")

    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):
        while STATE["running"]:
            try:
                self.heartbeat()
                self.monitor_runtime()

                state.set(RuntimeState.LISTENING)

                text = self.get_input()

                if not text:
                    continue

                STATE["last_input"] = text

                emit_event(
                    Event.SPEECH_HEARD,
                    payload={"text": text},
                )

                command = self.handle_command(text)

                if command:
                    state.set(RuntimeState.SPEAKING)
                    self.output(command)
                    continue

                # ----------------------------
                # THINK / BRAIN EXECUTION
                # ----------------------------
                state.set(RuntimeState.THINKING)

                response = self.execute_brain(text)

                if not response:
                    response = "No response generated."

                # ----------------------------
                # OUTPUT
                # ----------------------------
                state.set(RuntimeState.SPEAKING)
                self.output(response)

                # ----------------------------
                # MEMORY / STATE UPDATE
                # ----------------------------
                self.remember_turn(text, response)

                STATE["last_response"] = response
                STATE["turns"] += 1

                # ----------------------------
                # FAST LOOP CONTROL
                # ----------------------------
                time.sleep(0.01)

                state.set(RuntimeState.IDLE)

            except KeyboardInterrupt:
                STATE["running"] = False

            except Exception as e:
                self.register_error("MAIN LOOP", e)
                traceback.print_exc()
                self.recover("main loop failure")

        self.shutdown()

    # ========================================================
    # SHUTDOWN
    # ========================================================

    def shutdown(self):
        log("[SYS12000] shutdown started")

        STATE["running"] = False
        STATE["status"] = "offline"
        STATE["runtime_state"] = RuntimeState.SHUTDOWN

        emit_event(Event.SYSTEM_SHUTDOWN, priority=EventPriority.HIGH.value)

        try:
            stop()
        except Exception:
            pass

        try:
            if runtime_bus:
                runtime_bus.stop()
        except Exception as e:
            self.register_error("BUS STOP", e)

        log("[SYS12000] runtime offline")

# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():
    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "version": ENGINE_VERSION,
        "state": dict(STATE),
        "memory": dict(MEMORY),
        "systems": list(SYSTEMS.keys()),
    }

def status():
    return snapshot()

# ============================================================
# BOOT
# ============================================================

if __name__ == "__main__":
    print("\n================================")
    print(" WHISPLAY SYSTEM CONTROLLER")
    print("        STAGE 12000 CORE")
    print("================================\n")

    controller = SystemController()
    controller.boot()
