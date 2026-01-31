import customtkinter as ctk
import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk
import os
from ui.theme import Theme
from locales.manager import t


# Хелпер для загрузки иконок в меню (так как tk.Menu требует ImageTk, а не CTkImage)
def load_menu_icon(name):
    # Путь к папке ui
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, name)

    if os.path.exists(file_path):
        try:
            # Открываем через PIL
            pil_img = Image.open(file_path)
            # Ресайзим под меню (обычно 16x16 или 20x20)
            pil_img = pil_img.resize((16, 16), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_img)
        except Exception:
            return None
    return None


class CodeEditor(ctk.CTkFrame):
    def __init__(self, master, title, run_callback=None):
        super().__init__(master, fg_color="transparent")
        self.run_callback = run_callback  # Функция запуска кода

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

        # --- КОНТЕКСТНОЕ МЕНЮ ---
        self.menu = Menu(self, tearoff=0, bg=Theme.EDITOR_BG, fg="black", activebackground=Theme.ACCENT)

        # Загружаем иконки (сохраняем ссылки, чтобы сборщик мусора не удалил)
        self.icon_copy = load_menu_icon("copy.icns")
        self.icon_paste = load_menu_icon("paste.icns")
        self.icon_cut = load_menu_icon("cut.icns")
        self.icon_run = load_menu_icon("run.icns")

        # Добавляем пункты
        self.menu.add_command(label=t.get("ctx_run"), image=self.icon_run, compound="left", command=self._run_action,
                              accelerator="Cmd+R")
        self.menu.add_separator()
        self.menu.add_command(label=t.get("ctx_cut"), image=self.icon_cut, compound="left",
                              command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Cmd+X")
        self.menu.add_command(label=t.get("ctx_copy"), image=self.icon_copy, compound="left",
                              command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Cmd+C")
        self.menu.add_command(label=t.get("ctx_paste"), image=self.icon_paste, compound="left",
                              command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Cmd+V")

        # Привязка правой кнопки мыши (на Mac это часто Button-2 или Button-3)
        self.text_area.bind("<Button-3>", self.show_menu)
        self.text_area.bind("<Button-2>", self.show_menu)

    def _run_action(self):
        if self.run_callback:
            self.run_callback()

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def get_code(self):
        return self.text_area.get("0.0", "end")

    def set_code(self, code):
        self.text_area.delete("0.0", "end")
        self.text_area.insert("0.0", code)

    def set_title(self, title):
        self.label.configure(text=title)

    def set_font_size(self, size):
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

        # --- ЛОГИКА READ-ONLY С КОПИРОВАНИЕМ ---
        # Мы оставляем state="normal", чтобы работало выделение.
        # Но мы блокируем ввод текста.
        self.text_area.bind("<Key>", self.prevent_user_input)

        # --- КОНТЕКСТНОЕ МЕНЮ (Только копировать) ---
        self.menu = Menu(self, tearoff=0, bg="white", fg="black")
        self.icon_copy = load_menu_icon("copy.icns")
        self.menu.add_command(label=t.get("ctx_copy"), image=self.icon_copy, compound="left",
                              command=self.copy_selection, accelerator="Cmd+C")

        self.text_area.bind("<Button-3>", self.show_menu)
        self.text_area.bind("<Button-2>", self.show_menu)

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def copy_selection(self):
        try:
            # Получаем выделенный текст
            sel = self.text_area.get("sel.first", "sel.last")
            # Кладем в буфер обмена
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        except:
            pass  # Если ничего не выделено

    def prevent_user_input(self, event):
        # Разрешаем копирование (Command+C) и выделение (Command+A)
        # На Mac Command - это часто бит 8 (или 4 в зависимости от Tk)
        # Проще проверить keysym, если это не буква, или состояние модификатора

        # Разрешаем стрелки навигации
        if event.keysym in ["Left", "Right", "Up", "Down", "Prior", "Next", "Home", "End"]:
            return None

        # Разрешаем Command+C / Command+A
        # Проверяем, нажат ли Command (обычно state & 8 на Mac, но иногда & 4)
        is_cmd = (event.state & 8) or (event.state & 4)
        if is_cmd and event.keysym.lower() in ['c', 'a']:
            return None

        # Блокируем всё остальное (ввод текста, backspace, enter)
        return "break"

    def write(self, message, is_error=False):
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