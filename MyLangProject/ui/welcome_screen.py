import customtkinter as ctk
import os
from ui.theme import Theme
from locales.manager import t, WORK_DIR
from core.updater import CURRENT_VERSION


class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, master, on_open_editor, username):
        super().__init__(master, fg_color=Theme.BG_COLOR)
        self.on_open_editor = on_open_editor
        self.username = username
        self.pack(fill="both", expand=True)

        # Разделение на левую (меню) и правую (контент) части
        self.left_panel = ctk.CTkFrame(self, fg_color=Theme.FG_COLOR, width=300, corner_radius=0)
        self.left_panel.pack(side="left", fill="y")

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True)

        # --- ЛЕВАЯ ПАНЕЛЬ ---
        ctk.CTkLabel(self.left_panel, text="MyLang IDE", font=("Segoe UI", 24, "bold"), text_color=Theme.ACCENT).pack(
            pady=(40, 40), padx=20, anchor="w")

        self.create_menu_btn(t.get("welcome_new_proj"), self.new_project)
        self.create_menu_btn(t.get("welcome_open_file"), self.open_file)
        self.create_menu_btn(t.get("welcome_settings"), self.open_settings)

        ctk.CTkLabel(self.left_panel, text=f"{t.get("welcome_version")} {CURRENT_VERSION}",
                     text_color=Theme.TEXT_DIM).pack(side="bottom", pady=20, padx=20, anchor="w")

        # --- ПРАВАЯ ПАНЕЛЬ ---
        ctk.CTkLabel(self.right_panel, text=f"{t.get('welcome_title')}, {username}!", font=("Segoe UI", 30),
                     text_color=Theme.TEXT_MAIN).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(self.right_panel, text="Select an action to start coding", text_color=Theme.TEXT_DIM).place(
            relx=0.5, rely=0.5, anchor="center")

    def create_menu_btn(self, text, command):
        btn = ctk.CTkButton(
            self.left_panel,
            text=text,
            command=command,
            fg_color="transparent",
            text_color=Theme.TEXT_MAIN,
            hover_color=Theme.BG_COLOR,
            anchor="w",
            height=40,
            font=("Segoe UI", 14)
        )
        btn.pack(fill="x", padx=10, pady=5)

    def new_project(self):
        # Диалог создания файла
        dialog = ctk.CTkInputDialog(text=t.get("proj_name_title"), title=t.get("welcome_new_proj"))
        name = dialog.get_input()
        if name:
            filename = f"{name}.mylang"
            full_path = os.path.join(WORK_DIR, filename)
            # Создаем пустой файл
            with open(full_path, "w") as f:
                f.write('текст("Hello World")')
            self.destroy()
            self.on_open_editor(full_path)

    def open_file(self):
        # Открываем стандартный main.mylang (для упрощения, можно сделать FileDialog)
        default_file = os.path.join(WORK_DIR, "main.mylang")
        if not os.path.exists(default_file):
            with open(default_file, "w") as f: f.write("")
        self.destroy()
        self.on_open_editor(default_file)

    def open_settings(self):
        from ui.settings_window import SettingsWindow
        SettingsWindow(self.master)