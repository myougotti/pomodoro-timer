import customtkinter as ctk
from timer_engine import SessionType


SESSION_LABELS = {
    SessionType.WORK: "WORK SESSION",
    SessionType.SHORT_BREAK: "SHORT BREAK",
    SessionType.LONG_BREAK: "LONG BREAK",
}

SESSION_COLORS = {
    SessionType.WORK: "#e74c3c",
    SessionType.SHORT_BREAK: "#2ecc71",
    SessionType.LONG_BREAK: "#3498db",
}


class TimerDisplay(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.session_label = ctk.CTkLabel(
            self,
            text="WORK SESSION",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e74c3c",
        )
        self.session_label.pack(pady=(20, 5))

        self.time_label = ctk.CTkLabel(
            self,
            text="25:00",
            font=ctk.CTkFont(family="Consolas", size=72, weight="bold"),
        )
        self.time_label.pack(pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self, width=300, height=8, corner_radius=4
        )
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(1.0)

        self.pomodoro_label = ctk.CTkLabel(
            self,
            text="Pomodoro #0",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.pomodoro_label.pack(pady=(0, 10))

        self._total_duration = 25 * 60

    def update_display(self, remaining, session_type, total_duration, completed_count):
        minutes = remaining // 60
        seconds = remaining % 60
        self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")

        label = SESSION_LABELS.get(session_type, "WORK SESSION")
        color = SESSION_COLORS.get(session_type, "#e74c3c")
        self.session_label.configure(text=label, text_color=color)
        self.progress_bar.configure(progress_color=color)

        self._total_duration = total_duration
        if total_duration > 0:
            self.progress_bar.set(remaining / total_duration)
        else:
            self.progress_bar.set(0)

        self.pomodoro_label.configure(text=f"Pomodoro #{completed_count}")
