# =========================
# WHISPLAY STATE ENGINE — STAGE 700 STABLE
# CENTRAL NERVOUS SYSTEM
# State + Mode + Mood + Energy + Context + Hooks + Events + Safety
# Local-only / offline / controlled autonomy
# =========================

import time
import json
import traceback

try:
    from debug import log, error
except Exception:

    def log(x):
        print(x)

    def error(x):
        print(x)


# =========================
# FEATURE FLAGS
# =========================

FEATURES = {

    "validate_states": True,
    "history": True,
    "event_log": True,
    "hooks": True,
    "mood": True,
    "energy": True,
    "safe_mode": True,
    "context": True,
    "strategy": True,
    "decay": True,
    "snapshots": True,
    "guardrails": True,
    "debug_trace": True,
}


# =========================
# VALID MAPS
# =========================

VALID_STATES = [

    "booting",
    "idle",
    "listening",
    "thinking",
    "speaking",
    "acting",
    "error",
    "sleeping",
    "safe",
    "shutdown",
]

VALID_MODES = [

    "NORMAL",
    "COMMAND",
    "SILENT",
    "DEBUG",
    "RECOVERY",
    "SAFE",
    "FOCUS",
    "LOW_POWER",
]

VALID_MOODS = [

    "neutral",
    "calm",
    "focused",
    "sharp",
    "warm",
    "supportive",
    "alert",
    "tired",
    "guarded",
]

VALID_STRATEGIES = [

    "idle",
    "answer",
    "clarify",
    "command",
    "repair",
    "refuse",
    "safe_reply",
    "debug",
    "local_action",
]


# =========================
# STATE ENGINE
# =========================

class StateEngine:

    def __init__(self):

        self._state = "idle"

        self._mode = "NORMAL"

        self._mood = "neutral"

        self._energy = 1.0

        self._strategy = "idle"

        self._context = {

            "last_input": "",
            "last_output": "",
            "last_intent": "",
            "last_action": "",
            "topic": "",
            "confidence": 0.0,
            "turns": 0,
        }

        self._flags = {

            "safe_mode": False,
            "muted": False,
            "debug": False,
            "allow_actions": True,
            "allow_network": False,
            "allow_shell": False,
            "allow_file_write": False,
        }

        self._history = []

        self._events = []

        self._hooks = {}

        self._created_at = time.time()

        self._last_change = time.time()

        self._last_error = ""

        self._error_count = 0

        self._transition_count = 0


    # =========================
    # INTERNAL HELPERS
    # =========================

    def _now(self):

        return time.time()


    def _age(self):

        return round(
            self._now() - self._created_at,
            3
        )


    def _trim(self):

        self._history = self._history[-60:]

        self._events = self._events[-120:]


    def _safe_str(
        self,
        value,
        limit=300,
    ):

        try:
            value = str(value)

        except Exception:
            value = "<unprintable>"

        if len(value) > limit:

            return value[:limit] + "..."

        return value


    def _record_event(
        self,
        event_type,
        data=None,
    ):

        if not FEATURES.get(
            "event_log",
            True
        ):
            return False

        try:

            self._events.append({

                "time": self._now(),

                "age": self._age(),

                "type": self._safe_str(
                    event_type,
                    80
                ),

                "data": data or {},
            })

            self._trim()

            return True

        except Exception as e:

            self._register_error(
                "event_log",
                e
            )

            return False


    def _register_error(
        self,
        source,
        exc,
    ):

        self._error_count += 1

        self._last_error = f"{source}: {exc}"

        error(
            f"[STATE ERROR] {self._last_error}"
        )

        if FEATURES.get(
            "debug_trace",
            True
        ):

            try:
                error(
                    traceback.format_exc()
                )

            except Exception:
                pass

        self._safe_check()


    def _fire_hooks(
        self,
        event_type,
        payload,
    ):

        if not FEATURES.get(
            "hooks",
            True
        ):
            return True

        callbacks = list(
            self._hooks.get(
                event_type,
                []
            )
        )

        for fn in callbacks:

            try:
                fn(payload)

            except Exception as e:

                self._register_error(
                    "hook",
                    e
                )

        return True


    def _safe_check(self):

        if not FEATURES.get(
            "safe_mode",
            True
        ):
            return False

        if (
            self._error_count >= 5
            and not self._flags["safe_mode"]
        ):

            self.enable_safe_mode(
                "error threshold reached"
            )

            return True

        return False


    def _guard_transition(
        self,
        new_state,
    ):

        if not FEATURES.get(
            "guardrails",
            True
        ):
            return True

        if self._flags["safe_mode"]:

            allowed = [

                "idle",
                "error",
                "sleeping",
                "shutdown",
            ]

            if new_state not in allowed:

                error(
                    f"[STATE] SAFE blocked transition to {new_state}"
                )

                return False

        if (
            self._state == "shutdown"
            and new_state != "booting"
        ):

            error(
                "[STATE] shutdown locked; booting required"
            )

            return False

        return True


    # =========================
    # HOOKS
    # =========================

    def on(
        self,
        event_type,
        callback,
    ):

        if not callable(callback):

            self._register_error(
                "hook_register",
                "callback not callable"
            )

            return False

        event_type = self._safe_str(
            event_type,
            80
        )

        self._hooks.setdefault(
            event_type,
            []
        ).append(callback)

        return True


    def clear_hooks(
        self,
        event_type=None,
    ):

        if event_type is None:

            self._hooks = {}

        else:

            self._hooks.pop(
                str(event_type),
                None
            )

        return True


    # =========================
    # STATE CONTROL
    # =========================

    def set(
        self,
        new_state,
        reason="",
    ):

        try:

            new_state = str(
                new_state
            ).lower().strip()

            if (
                FEATURES.get(
                    "validate_states",
                    True
                )
                and new_state not in VALID_STATES
            ):

                self._register_error(
                    "state",
                    f"invalid state: {new_state}"
                )

                return False

            if not self._guard_transition(
                new_state
            ):
                return False

            if new_state == self._state:
                return True

            old = self._state

            if FEATURES.get(
                "history",
                True
            ):

                self._history.append({

                    "time": self._now(),

                    "from": old,

                    "to": new_state,

                    "reason": self._safe_str(
                        reason,
                        160
                    ),

                    "mode": self._mode,

                    "mood": self._mood,

                    "energy": self._energy,

                    "strategy": self._strategy,
                })

            self._state = new_state

            self._last_change = self._now()

            self._transition_count += 1

            payload = self.snapshot()

            payload["old"] = old

            payload["new"] = new_state

            payload["reason"] = reason

            log(
                f"[STATE] {old} -> {new_state}"
            )

            self._record_event(
                "state_change",
                payload
            )

            self._fire_hooks(
                "state_change",
                payload
            )

            self._fire_hooks(
                f"state:{new_state}",
                payload
            )

            self._trim()

            return True

        except Exception as e:

            self._register_error(
                "set_state",
                e
            )

            return False


    def get(self):

        return self._state


# ... render continues ...
