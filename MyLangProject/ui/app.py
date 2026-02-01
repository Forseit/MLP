import customtkinter as ctk
import os
import sys
import tkinter
from ui.theme import Theme
from ui.splash_screen import SplashScreen
from ui.login_screen import LoginScreen
from ui.welcome_screen import WelcomeScreen
from ui.widgets import CodeEditor, Console
from ui.settings_window import SettingsWindow
from core.interpreter import Interpreter
from core.system_info import get_processor_name
from core.updater import CURRENT_VERSION
from locales.manager import t, WORK_DIR


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1100x750")
        self.title(t.get("app_name"))
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=Theme.BG_COLOR)

        self.current_user = None
        self.current_file = None

        # Запускаем цепочку экранов
        self.show_splash()

    def show_splash(self):
        self.clean_frame()
        SplashScreen(self, on_complete=self.show_login)

    def show_login(self):
        self.clean_frame()
        LoginScreen(self, on_login_success=self.on_login_success)

    def on_login_success(self, username):
        self.current_user = username
        self.show_welcome()

    def show_welcome(self):
        self.clean_frame()
        WelcomeScreen(self, on_open_editor=self.launch_editor, username=self.current_user)

    def launch_editor(self, file_path):
        self.current_file = file_path
        self.clean_frame()
        EditorView(self, file_path)

    def clean_frame(self):
        for widget in self.winfo_children():
            widget.destroy()


# --- ОСНОВНОЙ ВИД РЕДАКТОРА (То, что раньше было App) ---
class EditorView(ctk.CTkFrame):
    def __init__(self, master, file_path):
        super().__init__(master, fg_color=Theme.BG_COLOR)
        self.pack(fill="both", expand=True)
        self.file_path = file_path
        self.master = master  # Ссылка на App для смены заголовка

        self.cpu_name = get_processor_name()

        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Редактор
        self.editor = CodeEditor(self, t.get("editor_title"), run_callback=self.run_program)
        self.editor.grid(row=0, column=0, padx=(20, 5), pady=20, sticky="nsew")

        self.load_file()

        # Консоль
        self.console = Console(self, t.get("console_title"))
        self.console.grid(row=0, column=1, padx=(5, 20), pady=20, sticky="nsew")

        # Кнопка запуска
        self.run_btn = ctk.CTkButton(
            self, text=t.get("run_button"), command=self.run_program,
            height=40, fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            font=("Segoe UI", 13, "bold"), corner_radius=6
        )
        self.run_btn.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.interpreter = Interpreter(console_callback=self.console.write)

        # Бинды
        self.setup_bindings()

        # Апдейтер
        self.updater = None
        self.after(1000, self.check_updates_bg)

    def setup_bindings(self):
        def safe_bind(seq, func):
            try:
                self.master.bind(seq, func)
            except:
                pass

        # Биндим на главное окно (master)
        safe_bind("<Command-s>", self.save_file)
        safe_bind("<Command-ы>", self.save_file)
        safe_bind("<Command-r>", lambda e: self.run_program())
        safe_bind("<Command-к>", lambda e: self.run_program())

    def load_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.editor.set_code(f.read())
        else:
            self.editor.set_code("")

    def save_file(self, event=None):
        code = self.editor.get_code()
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(code)
            self.console.write(f"--- {t.get('msg_saved')} ---")
        except Exception as e:
            self.console.write(f"--- {t.get('msg_save_err')}: {e} ---", is_error=True)

    def run_program(self):
        self.console.clear()
        if t.is_autosave(): self.save_file()
        self.interpreter.execute(self.editor.get_code())

    def check_updates_bg(self):
        from core.updater import Updater
        self.updater = Updater()
        has, ver = self.updater.check_for_updates()
        if has:
            if t.is_auto_restart():
                self.perform_update(restart=True)
            else:
                self.show_update_btn(ver)

    def show_update_btn(self, version):
        btn = ctk.CTkButton(self, text=f"Update v{version}", fg_color=Theme.CONSOLE_TEXT_SUCCESS,
                            command=lambda: self.perform_update(restart=True))
        btn.place(relx=0.98, rely=0.02, anchor="ne")

    def perform_update(self, restart=False):
        if self.updater.download_update():
            if restart:
                python = sys.executable
                os.execl(python, python, *sys.argv)