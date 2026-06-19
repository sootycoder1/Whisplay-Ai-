# =========================
# WHISPLAY SPEAK SYSTEM — STAGE 250
# Queue + Thread + Piper + WM8960 + Mood/Energy Ready
# =========================

import os
import re
import time
import queue
import threading
import subprocess

# =========================
# CONFIG
# =========================

PIPER_BIN = "/home/bjn/whisplay-ai/piper/piper"
PIPER_MODEL = "/home/bjn/whisplay-ai/models/en_US-lessac-medium.onnx"

DEVICE = "plughw:0,0"
FORMAT = "S16_LE"

# LOCKED GOOD VALUES — prevents chipmunk
BASE_RATE = 22050
CHANNELS = 1

DEBUG_AUDIO = False
MAX_CHUNK_LEN = 140
MAX_QUEUE_SIZE = 8

# =========================
# STATE
# =========================

_speech_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
_speaking = False
_current_proc = None
_worker_started = False


# =========================
# CLEAN / TEXT HELPERS
# =========================

def clean_text(text):
    if text is None:
        return ""

    text = str(text)
    text = text.replace('"', "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_text(text, max_len=MAX_CHUNK_LEN):
    text = clean_text(text)
    if not text:
        return []

    words = text.split()
    chunks = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word

        if len(test) <= max_len:
            current = test
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


# =========================
# PERSONALITY / ENERGY HOOKS
# =========================

def get_voice_profile(payload=None):
    """
    Safe hook for Stage301 brain result:
    accepts dicts like:
    {
        "response": "...",
        "mood": "focused",
        "energy": 1.2,
        "mode": "casual"
    }
    """

    mood = "neutral"
    energy = 1.0
    mode = "casual"

    if isinstance(payload, dict):
        mood = payload.get("mood", mood)
        energy = payload.get("energy", energy)
        mode = payload.get("mode", mode)

    try:
        energy = float(energy)
    except Exception:
        energy = 1.0

    rate = BASE_RATE

    if mood in ["low", "calm"]:
        rate = 21000
    elif mood in ["focused", "technical"]:
        rate = 22050
    elif mood in ["engaged", "curious"]:
        rate = 22500
    elif mode == "edge":
        rate = 23000

    if energy > 1.35:
        rate += 500

    if energy < 0.75:
        rate -= 500

    rate = max(20000, min(23500, int(rate)))

    return {
        "rate": str(rate),
        "channels": str(CHANNELS),
        "device": DEVICE,
        "format": FORMAT,
        "mood": mood,
        "energy": energy,
        "mode": mode,
    }


# =========================
# AUDIO PIPELINE
# =========================

def _run_audio(text, profile):
    global _current_proc

    text = clean_text(text)
    if not text:
        return

    rate = profile["rate"]

    if DEBUG_AUDIO:
        print(f"[SPEAK] rate={rate} text={text}")

    try:
        piper = subprocess.Popen(
            [PIPER_BIN, "--model", PIPER_MODEL, "--output_raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        aplay = subprocess.Popen(
            [
                "aplay",
                "-D", DEVICE,
                "-f", FORMAT,
                "-c", str(CHANNELS),
                "-r", str(rate),
            ],
            stdin=piper.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        _current_proc = aplay

        piper.stdin.write((text + "\n").encode("utf-8"))
        piper.stdin.close()

        piper.wait()
        aplay.wait()

    except Exception as e:
        print("[SPEAK ERROR]", e)

    finally:
        _current_proc = None


# =========================
# WORKER
# =========================

def _speech_worker():
    global _speaking

    while True:
        item = _speech_queue.get()

        if item is None:
            _speech_queue.task_done()
            break

        try:
            _speaking = True

            if isinstance(item, dict):
                text = item.get("text") or item.get("response") or ""
                profile = get_voice_profile(item)
            else:
                text = str(item)
                profile = get_voice_profile()

            for chunk in chunk_text(text):
                _run_audio(chunk, profile)

        except Exception as e:
            print("[SPEAK WORKER ERROR]", e)

        finally:
            _speaking = False
            _speech_queue.task_done()


def _ensure_worker():
    global _worker_started

    if _worker_started:
        return

    thread = threading.Thread(target=_speech_worker, daemon=True)
    thread.start()
    _worker_started = True


# =========================
# PUBLIC API
# =========================

def speak(text):
    _ensure_worker()

    if isinstance(text, dict):
        payload = text
    else:
        payload = {"text": clean_text(text)}

    if not clean_text(payload.get("text") or payload.get("response", "")):
        return

    try:
        _speech_queue.put(payload, block=False)
    except queue.Full:
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except Exception:
            pass
        _speech_queue.put(payload, block=False)


def speak_now(text):
    stop()
    speak(text)


def stop():
    global _current_proc, _speaking

    while not _speech_queue.empty():
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except Exception:
            break

    if _current_proc:
        try:
            _current_proc.terminate()
        except Exception:
            pass

    _current_proc = None
    _speaking = False


def is_speaking():
    return _speaking


def queue_size():
    return _speech_queue.qsize()


def status():
    return {
        "speaking": _speaking,
        "queue": _speech_queue.qsize(),
        "rate": BASE_RATE,
        "channels": CHANNELS,
        "device": DEVICE,
        "model": PIPER_MODEL,
    }


# =========================
# START WORKER
# =========================

_ensure_worker()
