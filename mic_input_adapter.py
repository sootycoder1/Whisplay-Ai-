import json
import queue
import threading
import time
from array import array

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

# Silence Vosk logs
SetLogLevel(-1)

VOSK_MODEL_PATH = "/home/bjn/vosk-model-small-en-us-0.15"

# WM8960 capture device (confirmed)
DEVICE_INDEX = 0

# Match codec rate
SAMPLE_RATE = 44100

# WM8960 reports 2 input channels (capture stereo)
CHANNELS = 2

# Stream blocksize
BLOCKSIZE = 8000

# Speech gate: raise if TV triggers; lower if it misses you
RMS_GATE = 450


# =========================
# MODEL CACHE
# =========================
_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model

    if _model is not None:
        return _model

    with _model_lock:
        if _model is None:
            _model = Model(VOSK_MODEL_PATH)

    return _model


def warm_model():
    try:
        _get_model()
        print("[MIC] model warmed")
        return True
    except Exception as e:
        print("[MIC WARM ERROR]", e)
        return False


# =========================
# STEREO -> MONO
# =========================

def _stereo_to_mono_int16(raw: bytes) -> bytes:
    a = array("h")
    a.frombytes(raw)
    if len(a) < 2:
        return raw
    # LEFT channel only (LRLR...)
    mono = array("h", (a[i] for i in range(0, len(a) - 1, 2)))
    return mono.tobytes()

# =========================
# LISTEN ONCE
# =========================
def listen_once(timeout_s: float = 6.0) -> str:
    model = _get_model()
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    q: "queue.Queue[bytes]" = queue.Queue()

    def callback(indata, frames, time_info, status):

        # callback alive; debug print disabled

        b = bytes(indata)

        # Convert stereo capture -> mono for recognizer
        if CHANNELS == 2:
            b = _stereo_to_mono_int16(b)

        # --- Speech energy gate (drops low-energy TV/room noise frames) ---
        if len(b) >= 400:
            step = max(2, len(b) // 200)
            s = 0
            n = 0
            for i in range(0, len(b) - 1, step):
                v = int.from_bytes(b[i : i + 2], "little", signed=True)
                s += abs(v)
                n += 1
            avg_abs = s // max(1, n)
            if avg_abs < RMS_GATE:
                return

        q.put(b)

    with sd.RawInputStream(
        device=DEVICE_INDEX,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCKSIZE,
        dtype="int16",
        channels=CHANNELS,
        callback=callback,
    ):
        t_end = time.time() + timeout_s

        while time.time() < t_end:
            try:
                data = q.get(timeout=0.5)
            except queue.Empty:
                continue

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = (res.get("text") or "").strip()
                if text:
                    return text

        res = json.loads(rec.FinalResult())
        return (res.get("text") or "").strip()
