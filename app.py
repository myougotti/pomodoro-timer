import json
import os
import time

import customtkinter as ctk

from timer_engine import TimerEngine, TimerState, SessionType
from models import Database
from tray import TrayManager
import notifications
from ui.timer_display import TimerDisplay
from ui.controls import Controls
from ui.task_entry import TaskEntry
from ui.settings_panel import SettingsPanel
from ui.stats_panel import StatsPanel

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")
ICON_PATH = os.path.join(APP_DIR, "assets", "icon.ico")

DEFAULT_SETTINGS = {
    "work_duration": 1500,
    "short_break_duration": 300,
    "long_break_duration": 900,
    "always_on_top": False,
    "sound_enabled": True,
    "theme": "dark",
}

SESSION_NAMES = {
    SessionType.WORK: "Work",
    SessionType.SHORT_BREAK: "Short Break",
    SessionType.LONG_BREAK: "Long Break",
}


class PomodoroApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load settings
        self.settings = self._load_settings()
        ctk.set_appearance_mode(self.settings.get("theme", "dark"))
        ctk.set_default_color_theme("blue")

        # Window setup
        self.title("Pomodoro Timer")
        self.geometry("420x620")
        self.minsize(380, 550)
        self.resizable(True, True)
        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)

        self.attributes("-topmost", self.settings.get("always_on_top", False))

        # Core components
        self.db = Database()
        self.engine = TimerEngine(
            on_tick=self._on_tick,
            on_complete=self._on_complete,
            schedule_fn=self.after,
            cancel_fn=self.after_cancel,
        )
        # Set durations directly (don't trigger on_tick before UI exists)
        self.engine.durations[SessionType.WORK] = self.settings["work_duration"]
        self.engine.durations[SessionType.SHORT_BREAK] = self.settings["short_break_duration"]
        self.engine.durations[SessionType.LONG_BREAK] = self.settings["long_break_duration"]
        self.engine._remaining = self.settings["work_duration"]

        # Build UI
        self._build_ui()

        # System tray
        self.tray = TrayManager(
            show_window_cb=self._restore_from_tray,
            quit_cb=self._quit_app,
            start_pause_cb=self._toggle_start_pause,
            reset_cb=self.engine.reset,
            root=self,
        )
        self.tray.start()

        # Window close minimizes to tray
        self.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

        # Keyboard shortcut: Space to toggle start/pause
        self.bind("<space>", lambda e: self._toggle_start_pause())

        # Initial display
        self._on_tick(self.engine.remaining, self.engine.session_type)
        self.stats_panel.refresh()

    def _build_ui(self):
        # Task entry at top
        self.task_entry = TaskEntry(self)
        self.task_entry.pack(fill="x")

        # Timer display
        self.timer_display = TimerDisplay(self)
        self.timer_display.pack(fill="x", expand=False)

        # Controls
        self.controls = Controls(
            self,
            on_start=self.engine.start,
            on_pause=self.engine.pause,
            on_resume=self.engine.resume,
            on_reset=self.engine.reset,
            on_skip=self.engine.skip,
        )
        self.controls.pack(fill="x")

        # Tab buttons for Settings / Stats
        self.tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.settings_tab_btn = ctk.CTkButton(
            self.tab_frame, text="Settings", width=100, height=30,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", border_width=1,
            command=lambda: self._show_panel("settings"),
        )
        self.settings_tab_btn.pack(side="left", padx=5)

        self.stats_tab_btn = ctk.CTkButton(
            self.tab_frame, text="Stats", width=100, height=30,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", border_width=1,
            command=lambda: self._show_panel("stats"),
        )
        self.stats_tab_btn.pack(side="left", padx=5)

        # Panel container
        self.panel_container = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_container.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        # Settings panel
        self.settings_panel = SettingsPanel(
            self.panel_container,
            settings=dict(self.settings),
            on_settings_changed=self._on_settings_changed,
        )

        # Stats panel
        self.stats_panel = StatsPanel(self.panel_container, db=self.db)

        # Show settings by default
        self._active_panel = None
        self._show_panel("settings")

    def _show_panel(self, panel_name):
        if self._active_panel == panel_name:
            # Toggle off
            self.settings_panel.pack_forget()
            self.stats_panel.pack_forget()
            self._active_panel = None
            self.settings_tab_btn.configure(fg_color="transparent")
            self.stats_tab_btn.configure(fg_color="transparent")
            return

        self.settings_panel.pack_forget()
        self.stats_panel.pack_forget()

        if panel_name == "settings":
            self.settings_panel.pack(fill="both", expand=True, pady=5)
            self.settings_tab_btn.configure(fg_color=("gray75", "gray25"))
            self.stats_tab_btn.configure(fg_color="transparent")
        elif panel_name == "stats":
            self.stats_panel.refresh()
            self.stats_panel.pack(fill="both", expand=True, pady=5)
            self.stats_tab_btn.configure(fg_color=("gray75", "gray25"))
            self.settings_tab_btn.configure(fg_color="transparent")

        self._active_panel = panel_name

    def _on_tick(self, remaining, session_type):
        self.timer_display.update_display(
            remaining, session_type,
            self.engine.total_duration,
            self.engine.completed_pomodoros,
        )
        self.controls.set_state(self.engine.state)

        # Update tray tooltip
        minutes = remaining // 60
        seconds = remaining % 60
        name = SESSION_NAMES.get(session_type, "Work")
        self.tray.update_tooltip(f"{name} - {minutes:02d}:{seconds:02d}")

    def _on_complete(self, session_type):
        name = SESSION_NAMES.get(session_type, "Session")

        # Record work sessions
        if session_type == SessionType.WORK and self.engine.started_at:
            task = self.task_entry.get_task()
            self.db.record_session(
                session_type="work",
                duration_seconds=self.engine.total_duration,
                task_label=task,
                started_at=self.engine.started_at,
            )
            self.stats_panel.refresh()

        # Notifications
        if session_type == SessionType.WORK:
            notifications.send_toast(
                "Pomodoro Complete!",
                f"Great work! Time for a break. (#{self.engine.completed_pomodoros})"
            )
        else:
            notifications.send_toast(
                "Break Over!",
                "Time to get back to work!"
            )

        if self.settings.get("sound_enabled", True):
            notifications.play_sound()

    def _toggle_start_pause(self):
        if self.engine.state == TimerState.IDLE:
            self.engine.start()
        elif self.engine.state == TimerState.RUNNING:
            self.engine.pause()
        elif self.engine.state == TimerState.PAUSED:
            self.engine.resume()

    def _on_settings_changed(self, new_settings):
        self.settings.update(new_settings)
        self.engine.set_durations(
            new_settings["work_duration"],
            new_settings["short_break_duration"],
            new_settings["long_break_duration"],
        )
        self.attributes("-topmost", new_settings.get("always_on_top", False))
        self._save_settings()

    def _minimize_to_tray(self):
        self.withdraw()

    def _restore_from_tray(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit_app(self):
        self.tray.stop()
        self.db.close()
        self.destroy()

    def _load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    loaded = json.load(f)
                    merged = dict(DEFAULT_SETTINGS)
                    merged.update(loaded)
                    return merged
            except Exception:
                pass
        return dict(DEFAULT_SETTINGS)

    def _save_settings(self):
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
