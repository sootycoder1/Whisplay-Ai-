(venv) pi@pocketchat:~/whisplay-ai $ cat sys1123.py

-------------------------

CORE SYSTEM IMPORTS (IMPORTANT)

-------------------------

from state_engine import statefrom brain import process_input, generate_response, update_mood, flavor_text, status as brain_status

input

try:from input_layer_stage11_5 import get_inputexcept:def get_input():return input(">> ")

display

try:from display_ui import show_idle, show_listening, show_thinking, show_speaking, show_errorexcept:def show_idle(x=""): print("[IDLE]", x)def show_listening(): print("[LISTENING]")def show_thinking(): print("[THINKING]")def show_speaking(x): print("[SPEAK]", x)def show_error(x): print("[ERROR]", x)

audio

try:from speak import speak, stop, is_speakingexcept:def speak(x): print("[VOICE]", x)def stop(): passdef is_speaking(): return False

-------------------------

CONTROLLER

-------------------------

class SystemController:

def __init__(self):
    self.running = True
    self.last_input = ""
    self.last_response = ""
    self.last_time = time.time()

    self.interaction_count = 0
    self.cooldown = 0.6

# =========================
# MAIN LOOP
# =========================
def run(self):
    log("[SYSTEM] Stage 170 controller online")

    show_idle("System Ready")

    while self.running:
        try:
            # -------------------------
            # LISTEN
            # -------------------------
            state.set("listening")
            show_listening()

            text = get_input()

            if not text or not text.strip():
                continue

            self.last_input = text
            self.interaction_count += 1

            # -------------------------
            # MOOD UPDATE (CRITICAL)
            # -------------------------
            update_mood(text)

            # -------------------------
            # THINK
            # -------------------------
            state.set("thinking")

            time.sleep(random.uniform(0.08, 0.22))

            response = self.think(text)

            print("[AI]", response)

            # TEMP OUTPUT (no audio yet)
            print("[AI]", response)

            time.sleep(self.cooldown)

        except KeyboardInterrupt:
            self.running = False

        except Exception as e:
            self.register_error("MAIN LOOP", e)

=========================

WHISPLAY SYSTEM CONTROLLER — STAGE 220

Offline Companion Runtime

State + Brain Loader + Mood + Display + Speech + Recovery + Turn Context

=========================

import timeimport randomimport traceback

=========================

DEBUG SAFE

=========================

try:from debug import log, errorexcept Exception:def log(msg): print(msg)def error(msg): print(msg)

=========================

FEATURE SWITCHES

=========================

FEATURES = {"brain_loader": True,"mood_tracking": True,"personality_flavor": True,"display_sync": True,"speech_sync": True,"speech_wait": True,"anti_repeat": True,"turn_memory": True,"idle_hooks": True,"controller_commands": True,"status_report": True,"error_recovery": True,"keyboard_fallback": True,}

=========================

IMPORTS

=========================

try:from state_engine import stateexcept Exception:class DummyState:def init(self):self._state = "idle"def set(self, s):self._state = sprint("[STATE]", s)def get(self):return self._statestate = DummyState()

try:from brain import process_input, generate_response, update_mood, flavor_text, status as brain_statusexcept Exception as e:error(f"[BRAIN LOADER IMPORT ERROR] {e}")

def process_input(text):
    return "Brain loader unavailable."

def generate_response(text):
    return process_input(text)

def update_mood(text):
    return None

def flavor_text(text):
    return text

def brain_status():
    return {"brain": "offline"}

try:from input_layer_stage11_5 import get_inputexcept Exception:def get_input():return input("YOU > ")

try:from display_ui import show_idle, show_listening, show_thinking, show_speaking, show_errorexcept Exception:def show_idle(text=""): print("[DISPLAY idle]", text)def show_listening(): print("[DISPLAY listening]")def show_thinking(): print("[DISPLAY thinking]")def show_speaking(text): print("[DISPLAY speaking]", text)def show_error(text): print("[DISPLAY error]", text)

try:from speak import speak, speak_now, stop, is_speakingexcept Exception:def speak(text): print("[VOICE]", text)def speak_now(text): print("[VOICE NOW]", text)def stop(): passdef is_speaking(): return False

=========================

CONTROLLER STATE

=========================

class SystemController:

def __init__(self):
    self.running = True
    self.mode = "NORMAL"

    self.turn_count = 0
    self.empty_turns = 0
    self.error_count = 0

    self.last_input = ""
    self.last_response = ""
    self.last_intent = ""
    self.last_error = ""

    self.start_time = time.time()
    self.last_turn_time = time.time()

    self.history = []
    self.max_history = 20

    self.cooldown = 0.35
    self.max_speech_wait = 18

# =========================
# STATE / DISPLAY
# =========================

def set_state(self, name, display_text=None):
    try:
        state.set(name)
    except Exception as e:
        self.register_error("STATE", e)

    if not FEATURES["display_sync"]:
        return

    try:
        if name == "idle":
            show_idle(display_text or "Ready")
        elif name == "listening":
            show_listening()
        elif name == "thinking":
            show_thinking()
        elif name == "speaking":
            show_speaking(display_text or "")
        elif name == "error":
            show_error(display_text or "Error")
    except Exception as e:
        self.register_error("DISPLAY", e)

# =========================
# COMMANDS
# =========================

def handle_controller_command(self, text):
    if not FEATURES["controller_commands"]:
        return None

    t = text.lower().strip()

    if t in ["exit", "quit", "stop controller", "shutdown controller"]:
        self.running = False
        return "Controller stopping cleanly."

    if t in ["status", "system status", "show status"]:
        return self.status_text()

    if t in ["brain status", "show brain"]:
        return str(brain_status())

    if t in ["stop", "stop speaking", "stop talking", "shut up"]:
        stop()
        return "Speech stopped."

    if t == "normal mode":
        self.mode = "NORMAL"
        return "Normal mode enabled."

    if t == "silent mode":
        self.mode = "SILENT"
        return "Silent mode enabled."

    if t == "command mode":
        self.mode = "COMMAND"
        return "Command mode enabled."

    if t == "reset turn memory":
        self.history = []
        self.turn_count = 0
        return "Turn memory reset."

    return None

# =========================
# TURN HOOKS
# =========================

def pre_turn(self, text):
    if FEATURES["mood_tracking"]:
        try:
            update_mood(text)
        except Exception as e:
            self.register_error("MOOD", e)

    if FEATURES["anti_repeat"] and text == self.last_input:
        return random.choice([
            "Same input again — I’ll keep it tight.",
            "You just said that. We can pivot or go deeper.",
            "Repeating detected. Give me the next move.",
        ])

    return None

def post_turn(self, response):
    if not response:
        return "I heard you, but the response came back empty."

    response = str(response).strip()

    if FEATURES["personality_flavor"]:
        try:
            response = flavor_text(response)
        except Exception as e:
            self.register_error("FLAVOR", e)

    if FEATURES["turn_memory"] and len(self.history) >= 3:
        if random.random() < 0.12:
            response += " We’ve got a thread going here."

    return response

# =========================
# BRAIN PIPELINE
# =========================

def think(self, text):
    command = self.handle_controller_command(text)
    if command:
        return command

    pre = self.pre_turn(text)
    if pre:
        return pre

    response = None

try:
    from incoming_3_STAGE301 import process as brain_process
    result = brain_process(text)
    response = result.get("response", "")
except Exception as e:
    self.register_error("BRAIN PROCESS", e)
    response = "Brain error."

    return self.post_turn(response)

# =========================
# OUTPUT
# =========================

def output(self, response):
    if self.mode == "SILENT":
        self.set_state("speaking", response)
        return

    self.set_state("speaking", response)

    if FEATURES["speech_sync"]:
        try:
            speak(response)
        except Exception as e:
            self.register_error("SPEAK", e)

    if FEATURES["speech_wait"]:
        self.wait_for_speech()

def wait_for_speech(self):
    start = time.time()

    try:
        while is_speaking():
            if time.time() - start > self.max_speech_wait:
                break
            time.sleep(0.05)
    except Exception as e:
        self.register_error("SPEECH WAIT", e)

# =========================
# RECORD / STATUS
# =========================

def record_turn(self, user_text, response):
    self.turn_count += 1
    self.last_input = user_text
    self.last_response = response
    self.last_turn_time = time.time()

    self.history.append({
        "turn": self.turn_count,
        "user": user_text,
        "response": response,
        "time": self.last_turn_time,
    })

    while len(self.history) > self.max_history:
        self.history.pop(0)

def uptime(self):
    return int(time.time() - self.start_time)

def status_text(self):
    return (
        f"Mode: {self.mode}. "
        f"State: {state.get()}. "
        f"Turns: {self.turn_count}. "
        f"Errors: {self.error_count}. "
        f"Uptime: {self.uptime()} seconds."
    )

def register_error(self, label, exc):
    self.error_count += 1
    self.last_error = f"{label}: {exc}"
    error(f"[{label} ERROR] {exc}")

# =========================
# IDLE BEHAVIOUR
# =========================

def idle_tick(self):
    if not FEATURES["idle_hooks"]:
        return

    self.empty_turns += 1

    if self.empty_turns >= 5:
        self.set_state("idle", random.choice([
            "Ready",
            "Still here",
            "Listening when you are",
            "System steady",
        ]))
        self.empty_turns = 0

# =========================
# MAIN LOOP
# =========================

def run(self):
    log("[SYSTEM] Stage 220 online")
    self.set_state("idle", "Stage 220 Ready")

    while self.running:
        try:
            self.set_state("listening")

            heard = get_input()

            if not heard or not str(heard).strip():
                self.idle_tick()
                continue

            heard = str(heard).strip()
            self.empty_turns = 0

            print("[HEARD]", heard)

            self.set_state("thinking")

            time.sleep(random.uniform(0.08, 0.22))

            response = self.think(heard)

            print("[AI]", response)

            self.record_turn(heard, response)

            time.sleep(self.cooldown)

            if self.running:
                self.set_state("idle", "Ready")

        except KeyboardInterrupt:
            self.running = False

        except Exception as e:
            self.register_error("MAIN LOOP", e)
            traceback.print_exc()

            if FEATURES["error_recovery"]:
                self.set_state("error", "Recovered")
                try:
                    speak_now("I hit an error, but I recovered.")
                except Exception:
                    pass
                time.sleep(1)
                self.set_state("idle", "Recovered")
            else:
                raise

    stop()
    self.set_state("idle", "Stopped")
    log("[SYSTEM] Stage 220 stopped")

=========================

RUN

=========================

if name == "main":SystemController().run()
