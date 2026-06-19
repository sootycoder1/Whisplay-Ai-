# ============================================================
# PERSISTENT SPEECH WORKER
# STAGE 10500
# Hot speech queue + nonblocking Piper control layer
# ============================================================

import os
import time
import queue
import threading
import subprocess


ENGINE_NAME = "persistent_speech_worker"
ENGINE_STAGE = 10500


PIPER_PATH = "/home/bjn/whisplay-ai/piper/piper"
MODEL_PATH = "/home/bjn/whisplay-ai/models/en_US-lessac-medium.onnx"
AUDIO_DEVICE = "plughw:0,0"

SAMPLE_RATE = 22050
CHANNELS = 1
FORMAT = "S16_LE"


STATE = {
    "status": "idle",
    "running": False,
    "speaking": False,
    "muted": False,
    "safe_mode": False,
    "speech_count": 0,
    "failures": 0,
    "queue_size": 0,
    "last_text": "",
    "last_error": "",
    "last_started": 0.0,
    "last_finished": 0.0,
    "created": time.time(),
    "updated": time.time(),
}


FLAGS = {
    "dedupe": True,
    "queue_enabled": True,
    "blocking_playback": True,
    "clear_stale_audio": True,
    "debug": True,
}


speech_queue = queue.Queue()
worker_thread = None
worker_lock = threading.Lock()


def now():
    return time.time()


def log(msg):
    if FLAGS["debug"]:
        print(f"[SPEECH10500] {msg}")


def update_queue_size():
    STATE["queue_size"] = speech_queue.qsize()
    STATE["updated"] = now()


def clean(text):
    return " ".join(str(text or "").strip().split())


def build_command(text):
    safe_text = text.replace('"', "'")

    return (
        f'echo "{safe_text}" | '
        f'{PIPER} '
        f'--model {MODEL} '
        f'--output_raw | '
        f'aplay '
        f'-D {AUDIO_DEVICE} '
        f'-f {FORMAT} '
        f'-c {CHANNELS} '
        f'-r {SAMPLE_RATE}'
    )


def _speak_now(text):
    text = clean(text)

    if not text:
        return False

    if STATE["muted"]:
        log("muted, speech skipped")
        return False

    if STATE["safe_mode"]:
        log("safe mode active, speech skipped")
        return False

    STATE["speaking"] = True
    STATE["status"] = "speaking"
    STATE["last_text"] = text
    STATE["last_started"] = now()
    STATE["updated"] = now()

    log(f"speaking: {text}")

    try:
        cmd = build_command(text)

        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
        )

        if result.returncode != 0:
            STATE["failures"] += 1
            STATE["last_error"] = f"returncode {result.returncode}"
            return False

        STATE["speech_count"] += 1
        return True

    except Exception as e:
        STATE["failures"] += 1
        STATE["last_error"] = str(e)
        log(f"error: {e}")
        return False

    finally:
        STATE["speaking"] = False
        STATE["status"] = "idle"
        STATE["last_finished"] = now()
        STATE["updated"] = now()


def _worker_loop():
    STATE["running"] = True
    STATE["status"] = "online"
    log("worker online")

    while STATE["running"]:

        try:
            text = speech_queue.get(timeout=0.25)

        except queue.Empty:
            update_queue_size()
            continue

        try:
            update_queue_size()
            _speak_now(text)

        except Exception as e:
            STATE["failures"] += 1
            STATE["last_error"] = str(e)
            log(f"worker error: {e}")

        finally:
            speech_queue.task_done()
            update_queue_size()

    STATE["status"] = "stopped"
    STATE["updated"] = now()
    log("worker stopped")


def start():
    global worker_thread

    with worker_lock:

        if STATE["running"]:
            return True

        worker_thread = threading.Thread(
            target=_worker_loop,
            daemon=True,
        )

        worker_thread.start()

        time.sleep(0.1)

        return True


def stop():
    global worker_thread

    STATE["running"] = False
    STATE["updated"] = now()

    try:
        if worker_thread is not None and worker_thread.is_alive():
            worker_thread.join(timeout=1.0)
    except Exception as e:
        STATE["last_error"] = str(e)

    if worker_thread is not None and not worker_thread.is_alive():
        worker_thread = None
        STATE["status"] = "stopped"

    STATE["updated"] = now()
    return True


def speak(text):
    text = clean(text)

    if not text:
        return False

    if FLAGS["dedupe"] and text == STATE["last_text"]:
        return False

    if not STATE["running"]:
        start()

    speech_queue.put(text)
    update_queue_size()

    return True


def speak_blocking(text):
    if not STATE["running"]:
        start()

    return _speak_now(text)


def clear_queue():
    cleared = 0

    while not speech_queue.empty():

        try:
            speech_queue.get_nowait()
            speech_queue.task_done()
            cleared += 1

        except Exception:
            break

    update_queue_size()
    log(f"queue cleared: {cleared}")

    return cleared


def mute():
    STATE["muted"] = True
    STATE["updated"] = now()
    return True


def unmute():
    STATE["muted"] = False
    STATE["updated"] = now()
    return True


def enable_safe_mode():
    STATE["safe_mode"] = True
    STATE["updated"] = now()
    return True


def disable_safe_mode():
    STATE["safe_mode"] = False
    STATE["updated"] = now()
    return True


def is_speaking():
    return STATE["speaking"]


def is_running():
    return STATE["running"]


def process(text=None):
    if text:
        speak(text)

    return snapshot()


def snapshot():
    update_queue_size()

    return {
        "engine": ENGINE_NAME,
        "stage": ENGINE_STAGE,
        "state": dict(STATE),
        "flags": dict(FLAGS),
    }


def status():
    update_queue_size()

    return (
        "\n"
        "==============================\n"
        " PERSISTENT SPEECH WORKER 10500\n"
        "==============================\n"
        f"STATUS:       {STATE['status']}\n"
        f"RUNNING:      {STATE['running']}\n"
        f"SPEAKING:     {STATE['speaking']}\n"
        f"MUTED:        {STATE['muted']}\n"
        f"QUEUE:        {STATE['queue_size']}\n"
        f"SPOKEN:       {STATE['speech_count']}\n"
        f"FAILURES:     {STATE['failures']}\n"
        f"LAST TEXT:    {STATE['last_text'][:40]}\n"
        "==============================\n"
    )


if __name__ == "__main__":

    print("\n================================")
    print(" PERSISTENT SPEECH WORKER 10500")
    print("================================\n")

    start()

    speak("Persistent speech worker online.")
    speak("Speech queue is active.")
    speak("Runtime voice layer is ready.")

    try:
        while True:
            print(status())
            time.sleep(2)

    except KeyboardInterrupt:
        stop()
        print("\n[SPEECH WORKER STOPPED]")
