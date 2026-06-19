# ============================================================
# QUEUE CORE — STAGE 3600
# Runtime queue + task flow management layer
# ============================================================

import time
from collections import deque


STAGE = 3600

ENGINE_NAME = "QUEUE_CORE"
ENGINE_VERSION = "3600.1-STABLE"

DEBUG = True


# ============================================================
# QUEUE STORAGE
# ============================================================

QUEUES = {
    "runtime": deque(),
    "signals": deque(),
    "events": deque(),
    "speech": deque(),
    "tasks": deque(),
    "priority": deque(),
}


# ============================================================
# LIMITS
# ============================================================

LIMITS = {
    "max_queue_size": 120,
    "max_history": 300,
}


# ============================================================
# HISTORY
# ============================================================

QUEUE_HISTORY = []


# ============================================================
# HELPERS
# ============================================================

def now():
    return time.time()


def log(message):

    if DEBUG:
        print(f"[QUEUE] {message}")


def remember(event, details=None):

    QUEUE_HISTORY.append({
        "event": event,
        "details": details or {},
        "time": now(),
    })

    while len(QUEUE_HISTORY) > LIMITS["max_history"]:
        QUEUE_HISTORY.pop(0)


# ============================================================
# CREATE QUEUE
# ============================================================

def create(name):

    if name in QUEUES:
        return False

    QUEUES[name] = deque()

    remember("create_queue", {
        "queue": name,
    })

    log(f"created: {name}")

    return True


# ============================================================
# PUSH
# ============================================================

def push(
    queue_name,
    item,
    source="runtime",
):

    if queue_name not in QUEUES:
        create(queue_name)

    entry = {
        "item": item,
        "source": source,
        "time": now(),
    }

    queue = QUEUES[queue_name]

    queue.append(entry)

    while len(queue) > LIMITS["max_queue_size"]:
        queue.popleft()

    remember("push", {
        "queue": queue_name,
    })

    return entry


# ============================================================
# PRIORITY PUSH
# ============================================================

def priority(
    item,
    source="runtime",
):

    entry = {
        "item": item,
        "source": source,
        "time": now(),
    }

    QUEUES["priority"].appendleft(
        entry
    )

    remember("priority_push", {
        "source": source,
    })

    return entry


# ============================================================
# POP
# ============================================================

def pop(queue_name):

    if queue_name not in QUEUES:
        return None

    queue = QUEUES[queue_name]

    if not queue:
        return None

    item = queue.popleft()

    remember("pop", {
        "queue": queue_name,
    })

    return item


# ============================================================
# PEEK
# ============================================================

def peek(queue_name):

    if queue_name not in QUEUES:
        return None

    queue = QUEUES[queue_name]

    if not queue:
        return None

    return queue[0]


# ============================================================
# CLEAR
# ============================================================

def clear(queue_name=None):

    if queue_name is None:

        for queue in QUEUES.values():
            queue.clear()

        remember("clear_all")

        log("all queues cleared")

        return True

    if queue_name not in QUEUES:
        return False

    QUEUES[queue_name].clear()

    remember("clear", {
        "queue": queue_name,
    })

    log(f"cleared: {queue_name}")

    return True


# ============================================================
# SIZE
# ============================================================

def size(queue_name=None):

    if queue_name is None:

        return {
            name: len(queue)
            for name, queue in QUEUES.items()
        }

    if queue_name not in QUEUES:
        return 0

    return len(QUEUES[queue_name])


# ============================================================
# EMPTY
# ============================================================

def empty(queue_name):

    return size(queue_name) == 0


# ============================================================
# FETCH
# ============================================================

def fetch(
    queue_name,
    limit=10,
):

    if queue_name not in QUEUES:
        return []

    queue = list(QUEUES[queue_name])

    return queue[:limit]


# ============================================================
# PROCESS
# ============================================================

def process():

    runtime = size("runtime")
    tasks = size("tasks")
    priority_queue = size("priority")

    overloaded = False

    if runtime >= 100:
        overloaded = True

    if tasks >= 100:
        overloaded = True

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "overloaded": overloaded,
        "runtime_queue": runtime,
        "task_queue": tasks,
        "priority_queue": priority_queue,
    }


# ============================================================
# STATUS
# ============================================================

def status():

    return {
        "engine": ENGINE_NAME,
        "stage": STAGE,
        "version": ENGINE_VERSION,
        "queues": size(),
        "history_size": len(
            QUEUE_HISTORY
        ),
    }


# ============================================================
# COMPATIBILITY
# ============================================================

def queue():
    return process()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" QUEUE CORE STAGE3600")
    print("================================\n")

    push(
        "runtime",
        "runtime_boot",
    )

    push(
        "tasks",
        "initialize_display",
    )

    priority(
        "critical_recovery",
    )

    print(process())

    print(status())
