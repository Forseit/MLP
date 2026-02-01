import customtkinter as ctk
from ui.theme import Theme
from locales.manager import t

class SplashScreen(ctk.CTkFrame):
    def __init__(self, master, on_complete):
        super().__init__(master, fg_color=Theme.BG_COLOR)
        self.on_complete = on_complete
        self.pack(fill="both", expand=True)

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Логотип (Текст)
        self.logo = ctk.CTkLabel(
            self.center_frame,
            text="MyLang IDE",
            font=("Segoe UI", 40, "bold"),
            text_color=Theme.ACCENT
        )
        self.logo.pack(pady=20)

        # Статус
        self.status = ctk.CTkLabel(
            self.center_frame,
            text=t.get("loading"),
            font=Theme.FONT_UI,
            text_color=Theme.TEXT_DIM
        )
        self.status.pack(pady=10)

        # Прогресс бар
        self.progress = ctk.CTkProgressBar(
            self.center_frame,
            width=300,
            height=10,
            progress_color=Theme.ACCENT
        )
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.loading_step = 0
        self.after(50, self.animate_loading)

    def animate_loading(self):
        if self.loading_step < 100:
            self.loading_step += 2
            self.progress.set(self.loading_step / 100)
            self.after(20, self.animate_loading)
        else:
            self.destroy()
            self.on_complete()