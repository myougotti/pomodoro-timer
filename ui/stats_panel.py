import customtkinter as ctk


class StatsPanel(ctk.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.db = db

        self.title_label = ctk.CTkLabel(
            self, text="Statistics",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.title_label.pack(pady=(10, 5))

        # Today section
        self.today_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.today_frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(self.today_frame, text="Today", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.today_pomodoros = ctk.CTkLabel(self.today_frame, text="Pomodoros: 0", font=ctk.CTkFont(size=13))
        self.today_pomodoros.pack(anchor="w")
        self.today_focus = ctk.CTkLabel(self.today_frame, text="Focus time: 0 min", font=ctk.CTkFont(size=13))
        self.today_focus.pack(anchor="w")

        # Separator
        ctk.CTkFrame(self, height=1, fg_color="gray50").pack(fill="x", padx=15, pady=5)

        # This week section
        self.week_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.week_frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(self.week_frame, text="This Week", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.week_details = ctk.CTkLabel(
            self.week_frame, text="No data yet",
            font=ctk.CTkFont(size=12), justify="left", anchor="w",
        )
        self.week_details.pack(anchor="w", fill="x")

        # Separator
        ctk.CTkFrame(self, height=1, fg_color="gray50").pack(fill="x", padx=15, pady=5)

        # All time section
        self.alltime_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.alltime_frame.pack(fill="x", padx=15, pady=(2, 10))
        ctk.CTkLabel(self.alltime_frame, text="All Time", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.alltime_pomodoros = ctk.CTkLabel(self.alltime_frame, text="Pomodoros: 0", font=ctk.CTkFont(size=13))
        self.alltime_pomodoros.pack(anchor="w")
        self.alltime_focus = ctk.CTkLabel(self.alltime_frame, text="Focus time: 0 hr", font=ctk.CTkFont(size=13))
        self.alltime_focus.pack(anchor="w")

    def refresh(self):
        today = self.db.get_today_stats()
        self.today_pomodoros.configure(text=f"Pomodoros: {today['pomodoros']}")
        self.today_focus.configure(text=f"Focus time: {today['focus_seconds'] // 60} min")

        week = self.db.get_week_stats()
        if week:
            lines = []
            for day in week:
                mins = day["focus_seconds"] // 60
                lines.append(f"  {day['day']}:  {day['pomodoros']} sessions, {mins} min")
            self.week_details.configure(text="\n".join(lines))
        else:
            self.week_details.configure(text="No data yet")

        alltime = self.db.get_all_time_stats()
        self.alltime_pomodoros.configure(text=f"Pomodoros: {alltime['pomodoros']}")
        hours = alltime["focus_seconds"] / 3600
        self.alltime_focus.configure(text=f"Focus time: {hours:.1f} hr")
