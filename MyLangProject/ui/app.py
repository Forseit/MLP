import customtkinter as ctk
import os
import tkinter
from ui.theme import Theme
from ui.widgets import CodeEditor, Console
from ui.settings_window import SettingsWindow
from core.interpreter import Interpreter
from core.system_info import get_processor_name
from core.updater import CURRENT_VERSION
from locales.manager import t, WORK_DIR


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.cpu_name = get_processor_name()
        self.geometry("1000x700")
        ctk.set_appearance_mode("Dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # 1. Редактор
        self.editor = CodeEditor(self, "LOADING...", run_callback=self.run_program)
        self.editor.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.load_initial_file()

        # 2. Консоль
        self.console = Console(self, "LOADING...")
        self.console.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # 3. Кнопка
        self.run_btn = ctk.CTkButton(
            self,
            text="LOADING...",
            command=self.run_program,
            height=50,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            font=Theme.FONT_UI,
            corner_radius=12
        )
        self.run_btn.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        self.interpreter = Interpreter(console_callback=self.console.write)

        self.reload_ui()

        self.updater = None
        self.after(1000, self.check_updates_bg)

        # --- НАСТРОЙКА ГОРЯЧИХ КЛАВИШ (РАСКЛАДКИ) ---
        self.setup_bindings()

    def setup_bindings(self):
        """Безопасная привязка клавиш для разных раскладок"""

        def safe_bind(sequence, func):
            """Пытается забиндить клавишу, игнорирует ошибки, если раскладка недоступна"""
            try:
                self.bind(sequence, func)
            except tkinter.TclError:
                pass

        # 1. Настройки (Cmd+D / Cmd+В)
        safe_bind("<Command-d>", self.open_settings)
        safe_bind("<Command-в>", self.open_settings)

        # 2. Сохранить (Cmd+S / Cmd+Ы)
        safe_bind("<Command-s>", self.save_file_command)
        safe_bind("<Command-ы>", self.save_file_command)

        # 3. Запуск (Cmd+R / Cmd+К)
        safe_bind("<Command-r>", self.run_program_event)
        safe_bind("<Command-к>", self.run_program_event)

        # 4. Выделить всё (Cmd+A / Cmd+Ф) - Глобально
        # Важно: используем bind_class, чтобы работало везде
        try:
            self.bind_class("Text", "<Command-a>", self.select_all)
            self.bind_class("Text", "<Command-ф>", self.select_all)
        except tkinter.TclError:
            pass

    def select_all(self, event):
        """Выделяет весь текст в активном поле ввода"""
        try:
            # event.widget - это виджет tkinter под курсором
            event.widget.tag_add("sel", "1.0", "end")
            return "break"
        except:
            pass

    def load_initial_file(self):
        file_path = os.path.join(WORK_DIR, "main.mylang")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.editor.set_code(f.read())
            except:
                pass
        else:
            self.editor.set_code(
                'текст("Привет, ' + self.cpu_name + '")\nтекст(\'Версия ' + str(CURRENT_VERSION) + '")')

    def save_file_command(self, event=None):
        code = self.editor.get_code()
        file_path = os.path.join(WORK_DIR, "main.mylang")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            self.console.write(f"--- {t.get('msg_saved')} ---")
        except Exception as e:
            self.console.write(f"--- {t.get('msg_save_err')}: {e} ---", is_error=True)

    def run_program_event(self, event=None):
        self.run_program()

    def reload_ui(self):
        app_title = f"MyLang IDE ({self.cpu_name}) - v{CURRENT_VERSION}"
        self.title(app_title)

        self.editor.set_title(t.get("editor_title"))
        self.console.set_title(t.get("console_title"))
        self.run_btn.configure(text=t.get("run_button"))

        font_size = t.get_font_size()
        self.editor.set_font_size(font_size)
        self.console.set_font_size(font_size)

    def open_settings(self, event=None):
        SettingsWindow(self)

    def run_program(self):
        self.console.clear()

        if t.is_autosave():
            self.save_file_command()

        code = self.editor.get_code()
        self.interpreter.execute(code)

    def check_updates_bg(self):
        from core.updater import Updater
        self.updater = Updater()
        has_update, version = self.updater.check_for_updates()
        if has_update:
            self.show_update_button(version)

    def show_update_button(self, version):
        self.update_btn = ctk.CTkButton(
            self,
            text=f"{t.get('update_avail')} (v{version})",
            fg_color="#28a745",
            hover_color="#218838",
            command=self.perform_update
        )
        self.update_btn.place(relx=0.98, rely=0.02, anchor="ne")

    def perform_update(self):
        if self.updater.download_update():
            self.update_btn.configure(text=t.get("update_msg"), state="disabled")
        else:
            self.update_btn.configure(text="Error", fg_color="red")