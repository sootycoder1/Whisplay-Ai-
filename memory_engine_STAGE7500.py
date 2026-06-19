# ============================================================
# MEMORY ENGINE
# STAGE 7500
# Persistent runtime memory + adaptive recall system
# ============================================================

import os
import json
import time
import threading


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "memory_engine"

ENGINE_STAGE = 7500


# ============================================================
# MEMORY FILE
# ============================================================

MEMORY_FILE = (
    "/home/pi/whisplay-ai/"
    "runtime_memory.json"
)


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "adaptive",
    "status": "online",
    "memory_entries": 0,
    "recall_count": 0,
    "save_count": 0,
    "load_count": 0,
    "failures": 0,
    "pressure": 0.0,
    "runtime_cycles": 0,
    "last_save": 0.0,
    "last_load": 0.0,
    "created": time.time(),
    "updated": time.time(),
}


# ============================================================
# MEMORY STORE
# ============================================================

MEMORY = {
    "short_term": [],
    "long_term": [],
    "runtime_events": [],
    "topics": [],
    "intents": [],
    "goals": [],
}


# ============================================================
# FLAGS
# ============================================================

FLAGS = {
    "memory_enabled": True,
    "persistent_storage": True,
    "adaptive_memory": True,
    "goal_tracking": True,
    "topic_tracking": True,
    "runtime_tracking": True,
    "safe_save": True,
}


# ============================================================
# LOCK
# ============================================================

memory_lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def now():

    return time.time()


def remember(
    category,
    value,
    limit=50,
):

    if category not in MEMORY:
        return

    MEMORY[category].append(value)

    MEMORY[category] = (
        MEMORY[category][-limit:]
    )

    STATE["memory_entries"] += 1

    STATE["updated"] = now()


# ============================================================
# SAVE MEMORY
# ============================================================

def save_memory():

    with memory_lock:

        try:

            data = {
                "engine": ENGINE_NAME,
                "stage": ENGINE_STAGE,
                "state": STATE,
                "memory": MEMORY,
                "timestamp": now(),
            }

            with open(
                MEMORY_FILE,
                "w"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                )

            STATE["save_count"] += 1

            STATE["last_save"] = now()

            print(
                "[MEMORY] saved"
            )

            return True

        except Exception as e:

            STATE["failures"] += 1

            print(
                f"[MEMORY ERROR] {e}"
            )

            return False


# ============================================================
# LOAD MEMORY
# ============================================================

def load_memory():

    with memory_lock:

        if not os.path.exists(
            MEMORY_FILE
        ):

            print(
                "[MEMORY] no file"
            )

            return False

        try:

            with open(
                MEMORY_FILE,
                "r"
            ) as f:

                data = json.load(f)

            loaded = data.get(
                "memory",
                {}
            )

            for key in MEMORY:

                if key in loaded:

                    MEMORY[key] = loaded[key]

            STATE["load_count"] += 1

            STATE["last_load"] = now()

            print(
                "[MEMORY] loaded"
            )

            return True

        except Exception as e:

            STATE["failures"] += 1

            print(
                f"[MEMORY LOAD ERROR] {e}"
            )

            return False


# ============================================================
# RECALL
# ============================================================

def recall(
    category=None,
    limit=5,
):

    STATE["recall_count"] += 1

    if category:

        return MEMORY.get(
            category,
            []
        )[-limit:]

    result = {}

    for key in MEMORY:

        result[key] = (
            MEMORY[key][-limit:]
        )

    return result


# ============================================================
# GOALS
# ============================================================

def add_goal(goal):

    remember(
        "goals",
        str(goal),
    )


# ============================================================
# RUNTIME EVENT
# ============================================================

def runtime_event(event):

    remember(
        "runtime_events",
        str(event),
    )


# ============================================================
# PROCESS
# ============================================================

def process(
    text=None,
    topic=None,
    intent=None,
):

    with memory_lock:

        STATE["runtime_cycles"] += 1

        if text:
            remember(
                "short_term",
                text,
            )

        if topic:
            remember(
                "topics",
                topic,
            )

        if intent:
            remember(
                "intents",
                intent,
            )

        STATE["updated"] = now()

        return {
            "stored": True,
            "text": text,
            "topic": topic,
            "intent": intent,
        }


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "memory": dict(MEMORY),
        "flags": dict(FLAGS),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return (
        "\n"
        "==============================\n"
        " MEMORY ENGINE STAGE 7500\n"
        "==============================\n"
        f"STATUS:       {STATE['status']}\n"
        f"ENTRIES:      {STATE['memory_entries']}\n"
        f"SAVES:        {STATE['save_count']}\n"
        f"LOADS:        {STATE['load_count']}\n"
        f"RECALLS:      {STATE['recall_count']}\n"
        f"FAILURES:     {STATE['failures']}\n"
        f"CYCLES:       {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" MEMORY ENGINE STAGE 7500")
    print("================================\n")

    process(
        text="runtime online",
        topic="runtime",
        intent="status",
    )

    process(
        text="play music",
        topic="music",
        intent="general",
    )

    add_goal(
        "improve runtime speed"
    )

    runtime_event(
        "speech initialized"
    )

    print(recall())

    save_memory()

    load_memory()

    print(status())

    print("\n[MEMORY ENGINE COMPLETE]")
