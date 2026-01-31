import customtkinter as ctk
from ui.theme import Theme
from locales.manager import t


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t.get("settings_title"))
        self.geometry("400x450")  # Увеличили высоту
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=Theme.BG_COLOR)

        # --- 1. ЯЗЫК ---
        self.lbl_lang = ctk.CTkLabel(self, text=t.get("settings_lang_label"), font=Theme.FONT_UI)
        self.lbl_lang.pack(pady=(20, 5))

        self.languages = {"English": "en", "Русский": "ru"}
        current_lang_code = t.get_lang()
        # Ищем имя по коду
        current_name = next((k for k, v in self.languages.items() if v == current_lang_code), "English")

        self.lang_var = ctk.StringVar(value=current_name)
        self.combo_lang = ctk.CTkComboBox(
            self,
            values=list(self.languages.keys()),
            variable=self.lang_var,
            state="readonly",
            width=200,
            fg_color=Theme.EDITOR_BG
        )
        self.combo_lang.pack(pady=5)

        # --- 2. РАЗМЕР ШРИФТА ---
        self.lbl_font = ctk.CTkLabel(self, text=f"{t.get('settings_font_label')}: {t.get_font_size()}",
                                     font=Theme.FONT_UI)
        self.lbl_font.pack(pady=(20, 5))

        self.slider_font = ctk.CTkSlider(
            self,
            from_=10,
            to=30,
            number_of_steps=20,
            width=200,
            command=self.update_font_label
        )
        self.slider_font.set(t.get_font_size())
        self.slider_font.pack(pady=5)

        # --- 3. АВТОСОХРАНЕНИЕ ---
        self.switch_autosave = ctk.CTkSwitch(
            self,
            text=t.get("settings_autosave"),
            onvalue=True,
            offvalue=False,
            font=Theme.FONT_UI
        )
        if t.is_autosave():
            self.switch_autosave.select()
        else:
            self.switch_autosave.deselect()
        self.switch_autosave.pack(pady=30)

        # --- КНОПКИ ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="bottom", pady=20)

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

    def update_font_label(self, value):
        self.lbl_font.configure(text=f"{t.get('settings_font_label')}: {int(value)}")

    def save_and_close(self):
        lang_code = self.languages[self.lang_var.get()]
        font_size = int(self.slider_font.get())
        autosave = bool(self.switch_autosave.get())

        # Сохраняем всё вместе
        new_settings = {
            "language": lang_code,
            "font_size": font_size,
            "autosave": autosave
        }

        t.save_settings(new_settings)
        self.master.reload_ui()  # Обновляем главное окно
        self.destroy()