import customtkinter as ctk


class TaskEntry(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="What are you working on?",
            width=340,
            height=38,
            font=ctk.CTkFont(size=14),
            corner_radius=8,
        )
        self.entry.pack(pady=(15, 5), padx=20)

    def get_task(self):
        text = self.entry.get().strip()
        return text if text else None
