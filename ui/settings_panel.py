import customtkinter as ctk


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, settings, on_settings_changed, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self._settings = settings
        self._on_changed = on_settings_changed

        self.title_label = ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.title_label.pack(pady=(10, 10))

        # Work duration
        self.work_var = ctk.IntVar(value=settings.get("work_duration", 1500) // 60)
        self._add_slider("Work duration:", self.work_var, 1, 60, "work")

        # Short break
        self.short_var = ctk.IntVar(value=settings.get("short_break_duration", 300) // 60)
        self._add_slider("Short break:", self.short_var, 1, 30, "short")

        # Long break
        self.long_var = ctk.IntVar(value=settings.get("long_break_duration", 900) // 60)
        self._add_slider("Long break:", self.long_var, 1, 60, "long")

        # Separator
        ctk.CTkFrame(self, height=1, fg_color="gray50").pack(fill="x", padx=15, pady=8)

        # Always on top
        self.on_top_var = ctk.BooleanVar(value=settings.get("always_on_top", False))
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=3)
        ctk.CTkLabel(top_frame, text="Always on top:", font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkSwitch(
            top_frame, text="", variable=self.on_top_var,
            command=self._notify_change, width=40,
        ).pack(side="right")

        # Sound
        self.sound_var = ctk.BooleanVar(value=settings.get("sound_enabled", True))
        sound_frame = ctk.CTkFrame(self, fg_color="transparent")
        sound_frame.pack(fill="x", padx=20, pady=3)
        ctk.CTkLabel(sound_frame, text="Sound alerts:", font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkSwitch(
            sound_frame, text="", variable=self.sound_var,
            command=self._notify_change, width=40,
        ).pack(side="right")

        # Theme
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(3, 12))
        ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=13)).pack(side="left")
        current_theme = settings.get("theme", "dark").capitalize()
        self.theme_toggle = ctk.CTkSegmentedButton(
            theme_frame, values=["Dark", "Light"],
            command=self._on_theme_change,
        )
        self.theme_toggle.set(current_theme)
        self.theme_toggle.pack(side="right")

    def _add_slider(self, label_text, var, from_, to, key):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=3)

        label = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13))
        label.pack(side="left")

        value_label = ctk.CTkLabel(frame, text=f"{var.get()} min", font=ctk.CTkFont(size=13), width=55)
        value_label.pack(side="right")

        slider = ctk.CTkSlider(
            frame, from_=from_, to=to, number_of_steps=to - from_,
            width=140,
            command=lambda v, vl=value_label, va=var: self._on_slider(v, vl, va),
        )
        slider.set(var.get())
        slider.pack(side="right", padx=(5, 5))

    def _on_slider(self, value, value_label, var):
        val = int(round(value))
        var.set(val)
        value_label.configure(text=f"{val} min")
        self._notify_change()

    def _on_theme_change(self, value):
        ctk.set_appearance_mode(value.lower())
        self._notify_change()

    def _notify_change(self, *_):
        self._settings["work_duration"] = self.work_var.get() * 60
        self._settings["short_break_duration"] = self.short_var.get() * 60
        self._settings["long_break_duration"] = self.long_var.get() * 60
        self._settings["always_on_top"] = self.on_top_var.get()
        self._settings["sound_enabled"] = self.sound_var.get()
        self._settings["theme"] = self.theme_toggle.get().lower()
        self._on_changed(self._settings)
