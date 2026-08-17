import threading
import time
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

_last_beep_time = 0
_beep_cooldown_sec = 2.5

def _play_alert_sound(freq=1000, duration_ms=400):
    if HAS_WINSOUND:
        try:
            winsound.Beep(freq, duration_ms)
        except Exception:
            pass

def trigger_posture_alert(freq=1000, duration_ms=400):
    global _last_beep_time
    now = time.time()
    if now - _last_beep_time >= _beep_cooldown_sec:
        _last_beep_time = now
        threading.Thread(target=_play_alert_sound, args=(freq, duration_ms), daemon=True).start()
