import customtkinter as ctk
import os
import sys
import tkinter
from ui.theme import Theme
from ui.widgets import CodeEditor, Console
from ui.settings_window import SettingsWindow
from core.interpreter import Interpreter
from core.system_info import get_processor_name
from core.updater import CURRENT_VERSION
from locales.manager import t, WORK_DIR


def restart_application():
    python = sys.executable
    os.execl(python, python, *sys.argv)


class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, version, update_callback):
        super().__init__(parent)
        self.update_callback = update_callback
        self.title(t.get("dlg_update_title"))
        self.geometry("400x250")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=Theme.BG_COLOR)

        self.lbl_header = ctk.CTkLabel(self, text=t.get("dlg_update_header"), font=("Segoe UI", 18, "bold"),
                                       text_color=Theme.TEXT_MAIN)
        self.lbl_header.pack(pady=(20, 10))

        msg = t.get("dlg_update_text", version=version)
        self.lbl_text = ctk.CTkLabel(self, text=msg, font=("Segoe UI", 13), text_color=Theme.TEXT_DIM, justify="center")
        self.lbl_text.pack(pady=5)

        self.chk_auto = ctk.CTkCheckBox(self, text=t.get("dlg_update_auto"), font=("Segoe UI", 12),
                                        text_color=Theme.TEXT_MAIN, fg_color=Theme.ACCENT)
        self.chk_auto.pack(pady=15)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=10)

        self.btn_cancel = ctk.CTkButton(self.btn_frame, text=t.get("dlg_btn_cancel"), fg_color="transparent",
                                        border_width=1, border_color=Theme.TEXT_DIM, command=self.destroy, width=100)
        self.btn_cancel.pack(side="left", padx=(0, 10), expand=True)

        self.btn_update = ctk.CTkButton(self.btn_frame, text=t.get("dlg_btn_update"), fg_color=Theme.ACCENT,
                                        hover_color=Theme.ACCENT_HOVER, command=self.on_update, width=100)
        self.btn_update.pack(side="right", padx=(10, 0), expand=True)

    def on_update(self):
        if self.chk_auto.get() == 1:
            t.save_settings({"auto_restart": True})
        self.destroy()
        self.update_callback()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cpu_name = get_processor_name()
        self.geometry("1100x750")  # Чуть шире по умолчанию
        self.title("MyLang IDE")
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=Theme.BG_COLOR)  # Применяем цвет фона из темы

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Отступы для "воздуха" в дизайне
        PAD_X = 20
        PAD_Y = 20

        # 1. Редактор
        self.editor = CodeEditor(self, "EDITOR", run_callback=self.run_program)
        self.editor.grid(row=0, column=0, padx=(PAD_X, 10), pady=PAD_Y, sticky="nsew")
        self.load_initial_file()

        # 2. Консоль
        self.console = Console(self, "TERMINAL")
        self.console.grid(row=0, column=1, padx=(10, PAD_X), pady=PAD_Y, sticky="nsew")

        # 3. Кнопка запуска (БОЛЬШАЯ и красивая)
        self.run_btn = ctk.CTkButton(
            self,
            text="RUN",
            command=self.run_program,
            height=45,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            font=Theme.FONT_UI,
            corner_radius=8
        )
        self.run_btn.grid(row=1, column=0, columnspan=2, padx=PAD_X, pady=(0, PAD_Y), sticky="ew")

        self.interpreter = Interpreter(console_callback=self.console.write)
        self.reload_ui()

        self.updater = None
        self.after(1000, self.check_updates_bg)
        self.setup_bindings()

    def setup_bindings(self):
        def safe_bind(sequence, func):
            try:
                self.bind(sequence, func)
            except tkinter.TclError:
                pass

        safe_bind("<Command-s>", self.save_file_command)
        safe_bind("<Command-ы>", self.save_file_command)
        safe_bind("<Command-d>", self.open_settings)
        safe_bind("<Command-в>", self.open_settings)
        safe_bind("<Command-r>", self.run_program_event)
        safe_bind("<Command-к>", self.run_program_event)

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
            self.console.write(f"--- {t.get('msg_saved')} ---", is_error=False)
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
        if t.is_autosave(): self.save_file_command()
        code = self.editor.get_code()
        self.interpreter.execute(code)

    def check_updates_bg(self):
        from core.updater import Updater
        self.updater = Updater()
        has_update, version = self.updater.check_for_updates()
        if has_update:
            if t.is_auto_restart():
                self.perform_update(restart=True)
            else:
                self.new_version = version
                self.show_update_button(version)

    def show_update_button(self, version):
        self.update_btn = ctk.CTkButton(
            self,
            text=f"{t.get('update_avail')} (v{version})",
            fg_color=Theme.CONSOLE_TEXT_SUCCESS,
            hover_color="#63a35c",
            text_color="black",
            command=self.open_update_dialog
        )
        self.update_btn.place(relx=0.98, rely=0.02, anchor="ne")

    def open_update_dialog(self):
        UpdateDialog(self, self.new_version, lambda: self.perform_update(restart=True))

    def perform_update(self, restart=False):
        if self.updater.download_update():
            if restart:
                restart_application()
            else:
                self.update_btn.configure(text=t.get("update_msg"), state="disabled")
        else:
            if self.update_btn: self.update_btn.configure(text="Error", fg_color="red")