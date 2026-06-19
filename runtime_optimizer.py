# ============================================================
# RUNTIME OPTIMIZER
# STAGE 4500
# Runtime stabilization + adaptive regulation layer
# ============================================================

import os
import time
import queue
import threading


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "idle",
    "pressure": 0.0,
    "cpu_load": 0.0,
    "queue_pressure": 0.0,
    "speech_pressure": 0.0,
    "overflow_count": 0,
    "recovery_count": 0,
    "loop_iterations": 0,
    "cooldown": 0.0,
    "last_tick": time.time(),
    "last_overflow": 0.0,
    "last_recovery": 0.0,
    "runtime_health": 1.0,
    "stability": 1.0,
}


# ============================================================
# RUNTIME FLAGS
# ============================================================

FLAGS = {
    "adaptive_mode": True,
    "overflow_protection": True,
    "speech_throttle": True,
    "queue_recovery": True,
    "dynamic_cooldown": True,
    "cpu_protection": True,
    "loop_stabilizer": True,
    "display_regulation": True,
    "reasoning_regulation": True,
    "adapter_control": True,
}


# ============================================================
# LIMITS
# ============================================================

LIMITS = {
    "max_pressure": 1.0,
    "max_queue_pressure": 25,
    "max_speech_pressure": 10,
    "max_cooldown": 3.0,
    "overflow_reset_time": 8.0,
    "recovery_delay": 2.0,
}


# ============================================================
# INTERNAL LOCK
# ============================================================

runtime_lock = threading.Lock()


# ============================================================
# PRESSURE HELPERS
# ============================================================

def clamp(value, minimum=0.0, maximum=1.0):

    return max(
        minimum,
        min(maximum, value)
    )


def compute_pressure():

    queue_pressure = (
        STATE["queue_pressure"] * 0.35
    )

    speech_pressure = (
        STATE["speech_pressure"] * 0.35
    )

    overflow_pressure = (
        STATE["overflow_count"] * 0.12
    )

    cpu_pressure = (
        STATE["cpu_load"] * 0.18
    )

    total = (
        queue_pressure
        + speech_pressure
        + overflow_pressure
        + cpu_pressure
    )

    STATE["pressure"] = clamp(total)

    return STATE["pressure"]


# ============================================================
# MODE CONTROL
# ============================================================

def set_mode(mode):

    with runtime_lock:

        STATE["mode"] = str(mode)

        STATE["last_tick"] = time.time()


def mode():

    return STATE["mode"]


# ============================================================
# COOLDOWN CONTROL
# ============================================================

def adaptive_cooldown():

    pressure = compute_pressure()

    cooldown = (
        pressure * 2.2
    )

    cooldown = min(
        cooldown,
        LIMITS["max_cooldown"]
    )

    STATE["cooldown"] = cooldown

    return cooldown


# ============================================================
# LOOP STABILIZER
# ============================================================

def stabilize_loop():

    STATE["loop_iterations"] += 1

    cooldown = adaptive_cooldown()

    if cooldown > 0:
        time.sleep(cooldown * 0.15)

    return cooldown


# ============================================================
# OVERFLOW CONTROL
# ============================================================

def register_overflow():

    STATE["overflow_count"] += 1

    STATE["last_overflow"] = time.time()

    compute_pressure()

    print(
        f"[OPTIMIZER] overflow "
        f"{STATE['overflow_count']}"
    )


def recover_overflow():

    now = time.time()

    if (
        now - STATE["last_overflow"]
        > LIMITS["overflow_reset_time"]
    ):

        if STATE["overflow_count"] > 0:

            STATE["overflow_count"] -= 1

            STATE["last_recovery"] = now

            STATE["recovery_count"] += 1

            compute_pressure()

            print(
                "[OPTIMIZER] overflow recovered"
            )


# ============================================================
# QUEUE REGULATION
# ============================================================

def regulate_queue(q):

    try:

        size = q.qsize()

    except:
        size = 0

    STATE["queue_pressure"] = size

    if (
        FLAGS["queue_recovery"]
        and size > LIMITS["max_queue_pressure"]
    ):

        print(
            "[OPTIMIZER] queue recovery"
        )

        try:

            while q.qsize() > 5:
                q.get_nowait()

        except:
            pass

        register_overflow()


# ============================================================
# SPEECH REGULATION
# ============================================================

def regulate_speech(
    speaking=False,
    speech_queue_size=0,
):

    pressure = 0.0

    if speaking:
        pressure += 0.5

    pressure += (
        speech_queue_size * 0.08
    )

    STATE["speech_pressure"] = clamp(
        pressure
    )


# ============================================================
# CPU LOAD
# ============================================================

def update_cpu_load():

    try:

        load = os.getloadavg()[0]

        normalized = (
            float(load) / 4.0
        )

        STATE["cpu_load"] = clamp(
            normalized
        )

    except:

        STATE["cpu_load"] = 0.0


# ============================================================
# HEALTH SCORE
# ============================================================

def update_health():

    pressure = compute_pressure()

    health = (
        1.0 - pressure
    )

    health = clamp(health)

    STATE["runtime_health"] = health

    STATE["stability"] = health

    return health


# ============================================================
# MAIN UPDATE
# ============================================================

def tick(
    queue_object=None,
    speaking=False,
    speech_queue_size=0,
):

    with runtime_lock:

        update_cpu_load()

        if queue_object is not None:
            regulate_queue(queue_object)

        regulate_speech(
            speaking=speaking,
            speech_queue_size=speech_queue_size,
        )

        recover_overflow()

        compute_pressure()

        update_health()

        stabilize_loop()

    return snapshot()


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return dict(STATE)


# ============================================================
# STATUS
# ============================================================

def status():

    s = snapshot()

    return (
        "\n"
        "==============================\n"
        " RUNTIME OPTIMIZER\n"
        "==============================\n"
        f"MODE:            {s['mode']}\n"
        f"PRESSURE:        {s['pressure']:.2f}\n"
        f"CPU LOAD:        {s['cpu_load']:.2f}\n"
        f"QUEUE PRESSURE:  {s['queue_pressure']}\n"
        f"SPEECH PRESSURE: {s['speech_pressure']:.2f}\n"
        f"OVERFLOWS:       {s['overflow_count']}\n"
        f"RECOVERIES:      {s['recovery_count']}\n"
        f"HEALTH:          {s['runtime_health']:.2f}\n"
        f"STABILITY:       {s['stability']:.2f}\n"
        "==============================\n"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" RUNTIME OPTIMIZER STAGE 4500")
    print("================================\n")

    test_queue = queue.Queue()

    set_mode("test")

    for i in range(12):
        test_queue.put(i)

    for i in range(15):

        if i % 4 == 0:
            register_overflow()

        tick(
            queue_object=test_queue,
            speaking=(i % 2 == 0),
            speech_queue_size=(i % 5),
        )

        print(status())

        time.sleep(1)

    print("\n[OPTIMIZER TEST COMPLETE]")
