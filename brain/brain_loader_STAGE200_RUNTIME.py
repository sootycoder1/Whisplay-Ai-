# ============================================================
# WHISPLAY BRAIN LOADER — STAGE 200
# Safe Module Loader + Active Brain Selector
# ============================================================

import importlib
import time


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


# ============================================================
# LOAD ORDER
# ============================================================

LOAD_ORDER = {

    "brain_core": [

        "brain.brain_cognitive_STAGE150_MERGED",

        "brain.brain_core_STAGE120_MERGED",

        "brain.brain_core_STAGE120",

        "brain.brain_core_STAGE100",

        "brain.brain_core",
    ],


    "cognitive": [

        "brain.cognitive_core",
    ],


    "memory": [

        "brain.memory",
    ],


    "router": [

        "brain.brain_router",

        "brain.hybrid_router",
    ],


    "personality": [

        "brain.personality",

        "brain.personality_fallback_STAGE120",
    ],
}


# ============================================================
# RUNTIME STATE
# ============================================================

LOADED = {}

ERRORS = {}

ACTIVE = {

    "brain_core": None,

    "cognitive": None,

    "memory": None,

    "router": None,

    "personality": None,

    "loaded_at": time.time(),
}


# ============================================================
# SAFE MODULE IMPORT
# ============================================================

def _load_module(module_name):

    try:

        module = importlib.import_module(
            module_name
        )

        log(
            f"[BRAIN LOADER] loaded "
            f"{module_name}"
        )

        return module


    except Exception as e:

        ERRORS[module_name] = str(e)

        error(
            f"[BRAIN LOADER ERROR] "
            f"{module_name}: {e}"
        )

        return None


# ============================================================
# LOAD FIRST AVAILABLE
# ============================================================

def _load_first(category):

    for module_name in LOAD_ORDER.get(
        category,
        []
    ):

        module = _load_module(module_name)

        if module is not None:

            LOADED[module_name] = module

            ACTIVE[category] = module_name

            return module

    return None


# ============================================================
# LOAD ACTIVE MODULES
# ============================================================

brain_core = _load_first("brain_core")

cognitive = _load_first("cognitive")

memory = _load_first("memory")

router = _load_first("router")

personality = _load_first("personality")


# ============================================================
# THINK
# ============================================================

def think(text):

    if (

        brain_core

        and

        hasattr(brain_core, "think")

    ):

        return brain_core.think(text)


    if (

        brain_core

        and

        hasattr(
            brain_core,
            "process_input"
        )

    ):

        return brain_core.process_input(text)


    return "Brain core unavailable."


# ============================================================
# PROCESS INPUT
# ============================================================

def process_input(text):

    if (

        cognitive

        and

        hasattr(
            cognitive,
            "process_input"
        )

    ):

        try:

            return cognitive.process_input(
                text
            )

        except Exception as e:

            error(
                f"[COGNITIVE ERROR] {e}"
            )


    return think(text)


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(text):

    if (

        brain_core

        and

        hasattr(
            brain_core,
            "generate_response"
        )

    ):

        return brain_core.generate_response(
            text
        )


    if (

        brain_core

        and

        hasattr(
            brain_core,
            "get_response"
        )

    ):

        return brain_core.get_response(
            text
        )


    return think(text)


# ============================================================
# ROUTING
# ============================================================

def route(text):

    if (

        router

        and

        hasattr(router, "route")

    ):

        return router.route(text)


    if (

        router

        and

        hasattr(
            router,
            "hybrid_route"
        )

    ):

        result = router.hybrid_route(text)

        if result:

            return {

                "intent": "direct",

                "response": result,
            }


    return {

        "intent": "conversation"
    }


# ============================================================
# MEMORY
# ============================================================

def store_memory(key, value):

    if (

        memory

        and

        hasattr(memory, "store")

    ):

        return memory.store(
            key,
            value
        )

    return False


def recall_memory(key):

    if (

        memory

        and

        hasattr(memory, "recall")

    ):

        return memory.recall(key)

    return None


# ============================================================
# PERSONALITY
# ============================================================

def update_mood(text):

    if (

        personality

        and

        hasattr(
            personality,
            "update_mood"
        )

    ):

        return personality.update_mood(
            text
        )

    return None


def flavor_text(text):

    if (

        personality

        and

        hasattr(
            personality,
            "flavor_text"
        )

    ):

        return personality.flavor_text(
            text
        )

    return text


# ============================================================
# RELOAD
# ============================================================

def reload_brain():

    global brain_core
    global cognitive
    global memory
    global router
    global personality


    LOADED.clear()

    ERRORS.clear()

    importlib.invalidate_caches()


    brain_core = _load_first(
        "brain_core"
    )

    cognitive = _load_first(
        "cognitive"
    )

    memory = _load_first(
        "memory"
    )

    router = _load_first(
        "router"
    )

    personality = _load_first(
        "personality"
    )


    ACTIVE["loaded_at"] = time.time()


    return status()


# ============================================================
# STATUS
# ============================================================

def status():

    return {

        "active": ACTIVE,

        "loaded": list(
            LOADED.keys()
        ),

        "errors": ERRORS,

        "brain_core_ready":
            brain_core is not None,

        "cognitive_ready":
            cognitive is not None,

        "memory_ready":
            memory is not None,

        "router_ready":
            router is not None,

        "personality_ready":
            personality is not None,
    }


# ============================================================
# READY
# ============================================================

log(
    "[BRAIN LOADER] Stage 200 ready"
)
