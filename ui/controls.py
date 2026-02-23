import customtkinter as ctk
from timer_engine import TimerState


class Controls(ctk.CTkFrame):
    def __init__(self, master, on_start, on_pause, on_resume, on_reset, on_skip, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._on_start = on_start
        self._on_pause = on_pause
        self._on_resume = on_resume
        self._on_reset = on_reset
        self._on_skip = on_skip

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(
            self.button_frame, text="Start", width=100, height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#e74c3c", hover_color="#c0392b",
            command=self._on_start,
        )

        self.pause_btn = ctk.CTkButton(
            self.button_frame, text="Pause", width=100, height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#f39c12", hover_color="#d68910",
            command=self._on_pause,
        )

        self.resume_btn = ctk.CTkButton(
            self.button_frame, text="Resume", width=100, height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2ecc71", hover_color="#27ae60",
            command=self._on_resume,
        )

        self.reset_btn = ctk.CTkButton(
            self.button_frame, text="Reset", width=80, height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray", hover_color="#555555",
            command=self._on_reset,
        )

        self.skip_btn = ctk.CTkButton(
            self.button_frame, text="Skip", width=80, height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray", hover_color="#555555",
            command=self._on_skip,
        )

        self.set_state(TimerState.IDLE)

    def set_state(self, state):
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()

        if state == TimerState.IDLE:
            self.start_btn.pack(side="left", padx=5)
            self.skip_btn.pack(side="left", padx=5)
        elif state == TimerState.RUNNING:
            self.pause_btn.pack(side="left", padx=5)
            self.reset_btn.pack(side="left", padx=5)
            self.skip_btn.pack(side="left", padx=5)
        elif state == TimerState.PAUSED:
            self.resume_btn.pack(side="left", padx=5)
            self.reset_btn.pack(side="left", padx=5)
            self.skip_btn.pack(side="left", padx=5)
