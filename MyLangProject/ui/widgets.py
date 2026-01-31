# ui/widgets.py
import customtkinter as ctk
from ui.theme import Theme


class CodeEditor(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="transparent")
        self.label = ctk.CTkLabel(master=self, text=title, font=Theme.FONT_UI, text_color=Theme.TEXT_DIM)
        self.label.pack(anchor="w", padx=5, pady=(0, 5))

        self.text_area = ctk.CTkTextbox(
            self,
            font=Theme.FONT_CODE,
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


class Console(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="transparent")
        self.label = ctk.CTkLabel(master=self, text=title, font=Theme.FONT_UI, text_color=Theme.TEXT_DIM)
        self.label.pack(anchor="w", padx=5, pady=(0, 5))

        self.text_area = ctk.CTkTextbox(
            self,
            font=Theme.FONT_CODE,
            fg_color=Theme.CONSOLE_BG,
            # По умолчанию ставим серый цвет
            text_color=Theme.CONSOLE_TEXT_NORMAL,
            corner_radius=10,
            border_width=0
        )
        self.text_area.pack(expand=True, fill="both")
        self.text_area.configure(state="disabled")

    def write(self, message, is_error=False):
        self.text_area.configure(state="normal")

        tag = "error" if is_error else "normal"
        # Настраиваем теги цветов
        self.text_area.tag_config("error", foreground=Theme.CONSOLE_TEXT_ERROR)
        self.text_area.tag_config("normal", foreground=Theme.CONSOLE_TEXT_NORMAL)

        self.text_area.insert("end", str(message) + "\n", tag)
        self.text_area.configure(state="disabled")
        self.text_area.see("end")

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("0.0", "end")
        self.text_area.configure(state="disabled")

    def set_title(self, title):
        self.label.configure(text=title)