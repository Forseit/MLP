import customtkinter as ctk
from ui.theme import Theme
from locales.manager import t
from core.auth import AuthManager


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=Theme.BG_COLOR)
        self.on_login_success = on_login_success
        self.auth = AuthManager()
        self.is_register_mode = False

        self.center_frame = ctk.CTkFrame(self, fg_color=Theme.FG_COLOR, corner_radius=15)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок
        self.lbl_title = ctk.CTkLabel(self.center_frame, text=t.get("auth_login_title"), font=Theme.FONT_HEADER)
        self.lbl_title.pack(pady=(30, 20), padx=50)

        # Поля
        self.entry_user = ctk.CTkEntry(self.center_frame, placeholder_text=t.get("auth_username"), width=250)
        self.entry_user.pack(pady=10, padx=30)

        self.entry_pass = ctk.CTkEntry(self.center_frame, placeholder_text=t.get("auth_password"), show="*", width=250)
        self.entry_pass.pack(pady=10, padx=30)

        # Ошибка
        self.lbl_error = ctk.CTkLabel(self.center_frame, text="", text_color=Theme.CONSOLE_TEXT_ERROR,
                                      font=("Segoe UI", 12))
        self.lbl_error.pack(pady=5)

        # Кнопка действия
        self.btn_action = ctk.CTkButton(
            self.center_frame,
            text=t.get("auth_btn_login"),
            command=self.perform_action,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            width=250,
            height=35
        )
        self.btn_action.pack(pady=20, padx=30)

        # Переключатель режима
        self.lbl_switch = ctk.CTkLabel(
            self.center_frame,
            text=t.get("auth_link_reg"),
            text_color=Theme.ACCENT,
            cursor="hand2"
        )
        self.lbl_switch.pack(pady=(0, 30))
        self.lbl_switch.bind("<Button-1>", self.switch_mode)

    def switch_mode(self, event=None):
        self.is_register_mode = not self.is_register_mode
        self.lbl_error.configure(text="")

        if self.is_register_mode:
            self.lbl_title.configure(text=t.get("auth_reg_title"))
            self.btn_action.configure(text=t.get("auth_btn_reg"))
            self.lbl_switch.configure(text=t.get("auth_link_login"))
        else:
            self.lbl_title.configure(text=t.get("auth_login_title"))
            self.btn_action.configure(text=t.get("auth_btn_login"))
            self.lbl_switch.configure(text=t.get("auth_link_reg"))

    def perform_action(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        if not user or not pwd:
            self.lbl_error.configure(text=t.get("auth_err_fields"))
            return

        if self.is_register_mode:
            success, msg_key = self.auth.register(user, pwd)
            if success:
                self.switch_mode()  # Переключаем на вход
                self.lbl_error.configure(text=t.get(msg_key), text_color=Theme.CONSOLE_TEXT_SUCCESS)
            else:
                self.lbl_error.configure(text=t.get(msg_key), text_color=Theme.CONSOLE_TEXT_ERROR)
        else:
            success, msg_key = self.auth.login(user, pwd)
            if success:
                self.destroy()
                self.on_login_success(user)
            else:
                self.lbl_error.configure(text=t.get(msg_key), text_color=Theme.CONSOLE_TEXT_ERROR)