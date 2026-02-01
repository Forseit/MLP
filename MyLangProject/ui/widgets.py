import customtkinter as ctk
import tkinter as tk
from tkinter import Menu
import os
from ui.theme import Theme
from locales.manager import t

try:
    from PIL import Image, ImageTk

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def load_menu_icon(name):
    if not HAS_PILLOW: return None
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, name)
    if os.path.exists(file_path):
        try:
            pil_img = Image.open(file_path)
            pil_img = pil_img.resize((16, 16), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_img)
        except Exception:
            return None
    return None


class CodeEditor(ctk.CTkFrame):
    def __init__(self, master, title, run_callback=None):
        super().__init__(master, fg_color="transparent")
        self.run_callback = run_callback

        # Заголовок
        self.label = ctk.CTkLabel(
            self,
            text=title,
            font=Theme.FONT_UI,
            text_color=Theme.TEXT_DIM,
            anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 5))

        # Поле ввода (Стиль VS Code)
        self.text_area = ctk.CTkTextbox(
            self,
            font=Theme.FONT_CODE,
            fg_color=Theme.EDITOR_BG,
            text_color=Theme.EDITOR_FG,
            corner_radius=6,  # Чуть меньше скругление
            border_width=1,  # Тонкая рамка
            border_color=Theme.EDITOR_BORDER,
            undo=True,
            wrap="none"  # Отключаем перенос строк для кода
        )
        self.text_area.pack(expand=True, fill="both")

        # --- Хоткеи и меню ---
        tb = self.text_area._textbox

        def force_bind(seq, event_name):
            try:
                tb.bind(seq, lambda e: tb.event_generate(event_name))
            except:
                pass

        force_bind("<Command-c>", "<<Copy>>")
        force_bind("<Command-с>", "<<Copy>>")
        force_bind("<Command-v>", "<<Paste>>")
        force_bind("<Command-м>", "<<Paste>>")
        force_bind("<Command-x>", "<<Cut>>")
        force_bind("<Command-ч>", "<<Cut>>")

        def select_all(e):
            tb.tag_add("sel", "1.0", "end")
            return "break"

        try:
            tb.bind("<Command-a>", select_all)
        except:
            pass
        try:
            tb.bind("<Command-ф>", select_all)
        except:
            pass

        self.icon_copy = load_menu_icon("copy.icns")
        self.icon_paste = load_menu_icon("paste.icns")
        self.icon_cut = load_menu_icon("cut.icns")
        self.icon_run = load_menu_icon("run.icns")

        self.text_area.bind("<Button-3>", self.show_context_menu)
        self.text_area.bind("<Button-2>", self.show_context_menu)
        self.text_area.bind("<Control-Button-1>", self.show_context_menu)

    def show_context_menu(self, event):
        # Используем цвета темы для меню (если поддерживается ОС, иначе стандарт)
        menu = Menu(self, tearoff=0, bg=Theme.EDITOR_BG, fg="black")  # На Mac bg не влияет, но пусть будет

        has_selection = False
        try:
            if self.text_area._textbox.tag_ranges("sel"): has_selection = True
        except:
            pass

        menu.add_command(label=t.get("ctx_run"), image=self.icon_run, compound="left", command=self._run_action,
                         accelerator="Cmd+R")
        menu.add_separator()

        if has_selection:
            menu.add_command(label=t.get("ctx_cut"), image=self.icon_cut, compound="left",
                             command=lambda: self.text_area._textbox.event_generate("<<Cut>>"), accelerator="Cmd+X")
            menu.add_command(label=t.get("ctx_copy"), image=self.icon_copy, compound="left",
                             command=lambda: self.text_area._textbox.event_generate("<<Copy>>"), accelerator="Cmd+C")

        menu.add_command(label=t.get("ctx_paste"), image=self.icon_paste, compound="left",
                         command=lambda: self.text_area._textbox.event_generate("<<Paste>>"), accelerator="Cmd+V")

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _run_action(self):
        if self.run_callback: self.run_callback()

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

        self.label = ctk.CTkLabel(
            self,
            text=title,
            font=Theme.FONT_UI,
            text_color=Theme.TEXT_DIM,
            anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 5))

        self.text_area = ctk.CTkTextbox(
            self,
            font=Theme.FONT_CODE,
            fg_color=Theme.CONSOLE_BG,
            text_color=Theme.CONSOLE_TEXT_NORMAL,
            corner_radius=6,
            border_width=0,  # Консоль без рамки, "вглубине"
            wrap="word"
        )
        self.text_area.pack(expand=True, fill="both")

        self.text_area.bind("<Key>", self.prevent_user_input)

        tb = self.text_area._textbox
        try:
            tb.bind("<Command-с>", lambda e: self.copy_selection())
        except:
            pass

        self.icon_copy = load_menu_icon("copy.icns")
        self.text_area.bind("<Button-3>", self.show_context_menu)
        self.text_area.bind("<Button-2>", self.show_context_menu)
        self.text_area.bind("<Control-Button-1>", self.show_context_menu)

    def show_context_menu(self, event):
        has_selection = False
        try:
            if self.text_area._textbox.tag_ranges("sel"): has_selection = True
        except:
            pass
        if not has_selection: return

        menu = Menu(self, tearoff=0, bg="white", fg="black")
        menu.add_command(label=t.get("ctx_copy"), image=self.icon_copy, compound="left", command=self.copy_selection,
                         accelerator="Cmd+C")
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def copy_selection(self):
        try:
            sel = self.text_area.get("sel.first", "sel.last")
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.master.update()
        except:
            pass

    def prevent_user_input(self, event):
        if event.keysym in ["Left", "Right", "Up", "Down", "Prior", "Next", "Home", "End"]: return None
        is_cmd = (event.state & 8) or (event.state & 4)
        if is_cmd: return None
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