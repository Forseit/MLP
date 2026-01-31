import customtkinter as ctk
from ui.theme import Theme
from locales.manager import t


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t.get("settings_title"))
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Фон окна
        self.configure(fg_color=Theme.BG_COLOR)

        # Заголовок (Label) берется из JSON
        self.label = ctk.CTkLabel(self, text=t.get("settings_lang_label"), font=Theme.FONT_UI)
        self.label.pack(pady=20)

        # Выбор языка (Mapping имен для человека -> код для программы)
        self.languages = {"English": "en", "Русский": "ru"}
        # Обратный поиск текущего названия по коду
        current_name = [k for k, v in self.languages.items() if v == t.lang_code][0]

        self.lang_var = ctk.StringVar(value=current_name)
        self.combo = ctk.CTkComboBox(
            self,
            values=list(self.languages.keys()),
            variable=self.lang_var,
            state="readonly",
            width=200,
            fg_color=Theme.EDITOR_BG,
            button_color=Theme.ACCENT
        )
        self.combo.pack(pady=10)

        # Кнопки
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=30)

        self.btn_save = ctk.CTkButton(
            self.btn_frame,
            text=t.get("settings_btn_apply"),
            fg_color=Theme.ACCENT,
            command=self.save_and_close
        )
        self.btn_save.pack(side="left", padx=10)

        self.btn_cancel = ctk.CTkButton(
            self.btn_frame,
            text=t.get("settings_btn_close"),
            fg_color="transparent",
            border_width=1,
            border_color=Theme.TEXT_DIM,
            command=self.destroy
        )
        self.btn_cancel.pack(side="left", padx=10)

        self.info_label = ctk.CTkLabel(self, text=t.get("settings_info"), text_color=Theme.TEXT_DIM, font=("Arial", 10))
        self.info_label.pack(side="bottom", pady=10)

    def save_and_close(self):
        # Получаем код языка (ru/en) по выбранному имени
        selected_name = self.lang_var.get()
        lang_code = self.languages[selected_name]

        t.save_config(lang_code)
        self.master.reload_ui()  # Обновляем главное окно
        self.destroy()