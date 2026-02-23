import threading
import pystray
from PIL import Image, ImageDraw


def _create_tray_icon_image(color="#e74c3c"):
    """Create a simple tomato-colored circle icon programmatically."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill=color)
    # Small green stem
    draw.rectangle([28, 0, 36, 12], fill="#27ae60")
    return img


class TrayManager:
    def __init__(self, show_window_cb, quit_cb, start_pause_cb, reset_cb, root):
        self._show_cb = show_window_cb
        self._quit_cb = quit_cb
        self._start_pause_cb = start_pause_cb
        self._reset_cb = reset_cb
        self._root = root
        self._icon = None
        self._thread = None

    def start(self):
        image = _create_tray_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self._on_show, default=True),
            pystray.MenuItem("Start/Pause", self._on_start_pause),
            pystray.MenuItem("Reset", self._on_reset),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )
        self._icon = pystray.Icon("pomodoro", image, "Pomodoro Timer", menu)
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def update_tooltip(self, text):
        if self._icon:
            self._icon.title = text

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _on_show(self, icon, item):
        self._root.after(0, self._show_cb)

    def _on_start_pause(self, icon, item):
        self._root.after(0, self._start_pause_cb)

    def _on_reset(self, icon, item):
        self._root.after(0, self._reset_cb)

    def _on_quit(self, icon, item):
        self._root.after(0, self._quit_cb)
