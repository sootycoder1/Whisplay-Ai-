# ============================================================
# GOAL ENGINE
# STAGE 8000
# Persistent adaptive objective + priority system
# ============================================================

import time
import threading


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENGINE_NAME = "goal_engine"

ENGINE_STAGE = 8000


# ============================================================
# GLOBAL STATE
# ============================================================

STATE = {
    "mode": "adaptive",
    "status": "online",
    "active_goal": None,
    "goal_count": 0,
    "completed_goals": 0,
    "failed_goals": 0,
    "priority_shift_count": 0,
    "pressure": 0.0,
    "focus": 1.0,
    "stability": 1.0,
    "runtime_cycles": 0,
    "last_goal": None,
    "last_update": time.time(),
}


# ============================================================
# GOAL STORE
# ============================================================

GOALS = {
    "active": [],
    "completed": [],
    "failed": [],
    "priority": [],
}


# ============================================================
# FLAGS
# ============================================================

FLAGS = {
    "goal_tracking": True,
    "adaptive_priority": True,
    "pressure_awareness": True,
    "goal_memory": True,
    "continuity_mode": True,
    "safe_execution": True,
}


# ============================================================
# LOCK
# ============================================================

goal_lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def now():

    return time.time()


def clamp(
    value,
    minimum=0.0,
    maximum=1.0,
):

    return max(
        minimum,
        min(maximum, value)
    )


# ============================================================
# GOAL OBJECT
# ============================================================

def create_goal(
    name,
    priority=0.5,
    metadata=None,
):

    return {
        "name": str(name),
        "priority": clamp(priority),
        "created": now(),
        "updated": now(),
        "status": "active",
        "progress": 0.0,
        "metadata": metadata or {},
    }


# ============================================================
# ADD GOAL
# ============================================================

def add_goal(
    name,
    priority=0.5,
    metadata=None,
):

    with goal_lock:

        goal = create_goal(
            name,
            priority,
            metadata,
        )

        GOALS["active"].append(goal)

        GOALS["priority"] = sorted(
            GOALS["active"],
            key=lambda g: g["priority"],
            reverse=True,
        )

        STATE["goal_count"] += 1

        STATE["active_goal"] = goal["name"]

        STATE["last_goal"] = goal["name"]

        STATE["last_update"] = now()

        print(
            f"[GOAL] added "
            f"{goal['name']}"
        )

        return goal


# ============================================================
# COMPLETE GOAL
# ============================================================

def complete_goal(name):

    with goal_lock:

        for goal in GOALS["active"]:

            if goal["name"] == name:

                goal["status"] = "completed"

                goal["progress"] = 1.0

                GOALS["completed"].append(
                    goal
                )

                GOALS["active"].remove(
                    goal
                )

                STATE["completed_goals"] += 1

                STATE["last_update"] = now()

                print(
                    f"[GOAL] completed "
                    f"{name}"
                )

                return True

    return False


# ============================================================
# FAIL GOAL
# ============================================================

def fail_goal(name):

    with goal_lock:

        for goal in GOALS["active"]:

            if goal["name"] == name:

                goal["status"] = "failed"

                GOALS["failed"].append(
                    goal
                )

                GOALS["active"].remove(
                    goal
                )

                STATE["failed_goals"] += 1

                STATE["last_update"] = now()

                print(
                    f"[GOAL] failed "
                    f"{name}"
                )

                return True

    return False


# ============================================================
# PRIORITY ENGINE
# ============================================================

def rebalance_priorities():

    with goal_lock:

        pressure = STATE["pressure"]

        for goal in GOALS["active"]:

            priority = goal["priority"]

            if pressure > 0.7:

                priority *= 0.92

            else:

                priority *= 1.02

            goal["priority"] = clamp(
                priority
            )

        GOALS["priority"] = sorted(
            GOALS["active"],
            key=lambda g: g["priority"],
            reverse=True,
        )

        STATE["priority_shift_count"] += 1

        return GOALS["priority"]


# ============================================================
# ACTIVE GOAL
# ============================================================

def current_goal():

    if not GOALS["priority"]:
        return None

    return GOALS["priority"][0]


# ============================================================
# PROGRESS
# ============================================================

def update_progress(
    name,
    progress,
):

    with goal_lock:

        for goal in GOALS["active"]:

            if goal["name"] == name:

                goal["progress"] = clamp(
                    progress
                )

                goal["updated"] = now()

                return True

    return False


# ============================================================
# PROCESS
# ============================================================

def process():

    with goal_lock:

        STATE["runtime_cycles"] += 1

        rebalance_priorities()

        active = current_goal()

        if active:

            STATE["active_goal"] = (
                active["name"]
            )

        STATE["last_update"] = now()

        return {
            "active_goal": STATE["active_goal"],
            "goal_count": STATE["goal_count"],
            "completed": STATE["completed_goals"],
            "failed": STATE["failed_goals"],
        }


# ============================================================
# SNAPSHOT
# ============================================================

def snapshot():

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "goals": dict(GOALS),
        "flags": dict(FLAGS),
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return (
        "\n"
        "==============================\n"
        " GOAL ENGINE STAGE 8000\n"
        "==============================\n"
        f"STATUS:        {STATE['status']}\n"
        f"ACTIVE GOAL:   {STATE['active_goal']}\n"
        f"GOALS:         {STATE['goal_count']}\n"
        f"COMPLETED:     {STATE['completed_goals']}\n"
        f"FAILED:        {STATE['failed_goals']}\n"
        f"PRIORITY OPS:  {STATE['priority_shift_count']}\n"
        f"CYCLES:        {STATE['runtime_cycles']}\n"
        "==============================\n"
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" GOAL ENGINE STAGE 8000")
    print("================================\n")

    add_goal(
        "optimize runtime",
        priority=0.9,
    )

    add_goal(
        "improve speech latency",
        priority=0.8,
    )

    add_goal(
        "display synchronization",
        priority=0.6,
    )

    update_progress(
        "optimize runtime",
        0.45,
    )

    process()

    print(status())

    print(current_goal())

    complete_goal(
        "optimize runtime"
    )

    process()

    print(status())

    print("\n[GOAL ENGINE COMPLETE]")
