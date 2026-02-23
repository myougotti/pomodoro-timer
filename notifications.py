import os
import threading
import winsound

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
ALARM_PATH = os.path.join(ASSETS_DIR, "alarm.wav")


def send_toast(title, message):
    def _notify():
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Pomodoro Timer",
                timeout=5,
            )
        except Exception:
            pass

    t = threading.Thread(target=_notify, daemon=True)
    t.start()


def play_sound():
    try:
        if os.path.exists(ALARM_PATH):
            winsound.PlaySound(ALARM_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            # Fallback: system beep sequence
            for _ in range(3):
                winsound.Beep(800, 300)
                winsound.Beep(0, 150)
    except Exception:
        pass
