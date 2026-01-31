import customtkinter as ctk
from ui.theme import Theme


class CodeEditor(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="transparent")
        self.label = ctk.CTkLabel(master=self, text=title, font=Theme.FONT_UI, text_color=Theme.TEXT_DIM)
        self.label.pack(anchor="w", padx=5, pady=(0, 5))

        self.text_area = ctk.CTkTextbox(
            self,
            font=Theme.FONT_CODE,  # Размер будет обновлен позже
            fg_color=Theme.EDITOR_BG,
            text_color=Theme.EDITOR_FG,
            corner_radius=10,
            border_width=1,
            border_color="#333333",
            undo=True
        )
        self.text_area.pack(expand=True, fill="both")

    def get_code(self):
        return self.text_area.get("0.0", "end")

    def set_code(self, code):
        self.text_area.delete("0.0", "end")
        self.text_area.insert("0.0", code)

    def set_title(self, title):
        self.label.configure(text=title)

    def set_font_size(self, size):
        # Обновляем шрифт редактора
        self.text_area.configure(font=("Menlo", size))


class Console(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="transparent")
        self.label = ctk.CTkLabel(master=self, text=title, font=Theme.FONT_UI, text_color=Theme.TEXT_DIM)
        self.label.pack(anchor="w", padx=5, pady=(0, 5))

        self.text_area = ctk.CTkTextbox(
            self,
            font=Theme.FONT_CODE,
            fg_color=Theme.CONSOLE_BG,
            text_color=Theme.CONSOLE_TEXT_NORMAL,
            corner_radius=10,
            border_width=0
        )
        self.text_area.pack(expand=True, fill="both")

        # --- ХАК ДЛЯ КОПИРОВАНИЯ ---
        # Мы НЕ делаем state="disabled", потому что это блокирует выделение в CustomTkinter.
        # Вместо этого мы оставляем state="normal", но перехватываем нажатия клавиш,
        # чтобы пользователь не мог печатать сам.
        self.text_area.bind("<Key>", self.prevent_user_input)

    def prevent_user_input(self, event):
        # Разрешаем копирование (Command+C) и выделение (Command+A)
        # На Windows это Control, но на Mac Command отображается как State 8 или похожие.
        # Проще всего разрешить ничего не делая, если это горячая клавиша.

        keysym = event.keysym.lower()

        # Разрешаем стрелки для навигации
        if keysym in ["left", "right", "up", "down", "home", "end"]:
            return

        # Разрешаем копирование (c) и выделение (a) при зажатом Command/Control
        # (event.state & 4) == 4 - это Ctrl на Linux/Win, на Mac Command может быть другим битом.
        # Но ctk обычно пробрасывает системные шорткаты ДО этого ивента.
        # Если мы вернем "break", то символ не напечатается.

        # Если это просто буквы/цифры/энтер/бэкспейс - блокируем
        if len(keysym) == 1 or keysym in ["return", "backspace", "delete", "tab"]:
            return "break"

    def write(self, message, is_error=False):
        # Для программной вставки нам не нужно менять state, так как мы блокируем только <Key>
        tag = "error" if is_error else "normal"
        self.text_area.tag_config("error", foreground=Theme.CONSOLE_TEXT_ERROR)
        self.text_area.tag_config("normal", foreground=Theme.CONSOLE_TEXT_NORMAL)

        self.text_area.insert("end", str(message) + "\n", tag)
        self.text_area.see("end")

    def clear(self):
        self.text_area.delete("0.0", "end")

    def set_title(self, title):
        self.label.configure(text=title)

    def set_font_size(self, size):
        self.text_area.configure(font=("Menlo", size))