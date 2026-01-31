import customtkinter as ctk
import tkinter as tk
from tkinter import Menu
import os
from ui.theme import Theme
from locales.manager import t

# --- БЕЗОПАСНЫЙ ИМПОРТ PILLOW ---
try:
    from PIL import Image, ImageTk

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Warning: PIL (Pillow) library not found. Icons disabled.")


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

        # --- ДОБАВЛЯЕМ ПОДДЕРЖКУ РУССКИХ ХОТКЕЕВ ---
        # Мы должны добраться до внутреннего виджета tkinter
        tb = self.text_area._textbox

        def safe_bind(seq, func):
            try:
                tb.bind(seq, func)
            except:
                pass

        # Копировать (С)
        safe_bind("<Command-с>", lambda e: tb.event_generate("<<Copy>>"))
        # Вставить (М)
        safe_bind("<Command-м>", lambda e: tb.event_generate("<<Paste>>"))
        # Вырезать (Ч)
        safe_bind("<Command-ч>", lambda e: tb.event_generate("<<Cut>>"))
        # Отменить (Я - это Z)
        safe_bind("<Command-я>", lambda e: tb.event_generate("<<Undo>>"))

        # Иконки
        self.icon_copy = load_menu_icon("copy.icns")
        self.icon_paste = load_menu_icon("paste.icns")
        self.icon_cut = load_menu_icon("cut.icns")
        self.icon_run = load_menu_icon("run.icns")

        # Привязка ПКМ
        self.text_area.bind("<Button-3>", self.show_context_menu)
        self.text_area.bind("<Button-2>", self.show_context_menu)
        self.text_area.bind("<Control-Button-1>", self.show_context_menu)

    def show_context_menu(self, event):
        menu = Menu(self, tearoff=0, bg=Theme.EDITOR_BG, fg="black")

        # ПРОВЕРКА ВЫДЕЛЕНИЯ
        has_selection = False
        try:
            if self.text_area._textbox.tag_ranges("sel"):
                has_selection = True
        except:
            pass

        # 1. RUN
        menu.add_command(
            label=t.get("ctx_run"),
            image=self.icon_run,
            compound="left",
            command=self._run_action,
            accelerator="Cmd+R"
        )
        menu.add_separator()

        # 2. CUT (Только если есть выделение)
        if has_selection:
            menu.add_command(
                label=t.get("ctx_cut"),
                image=self.icon_cut,
                compound="left",
                command=lambda: self.text_area._textbox.event_generate("<<Cut>>"),
                accelerator="Cmd+X"
            )

        # 3. COPY (Только если есть выделение)
        if has_selection:
            menu.add_command(
                label=t.get("ctx_copy"),
                image=self.icon_copy,
                compound="left",
                command=lambda: self.text_area._textbox.event_generate("<<Copy>>"),
                accelerator="Cmd+C"
            )

        # 4. PASTE (Всегда)
        menu.add_command(
            label=t.get("ctx_paste"),
            image=self.icon_paste,
            compound="left",
            command=lambda: self.text_area._textbox.event_generate("<<Paste>>"),
            accelerator="Cmd+V"
        )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _run_action(self):
        if self.run_callback:
            self.run_callback()

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

        self.text_area.bind("<Key>", self.prevent_user_input)
        self.icon_copy = load_menu_icon("copy.icns")

        self.text_area.bind("<Button-3>", self.show_context_menu)
        self.text_area.bind("<Button-2>", self.show_context_menu)
        self.text_area.bind("<Control-Button-1>", self.show_context_menu)

        # Русское копирование в консоли
        tb = self.text_area._textbox
        try:
            tb.bind("<Command-с>", lambda e: self.copy_selection())
        except:
            pass

    def show_context_menu(self, event):
        has_selection = False
        try:
            if self.text_area._textbox.tag_ranges("sel"):
                has_selection = True
        except:
            pass

        if not has_selection:
            return

        menu = Menu(self, tearoff=0, bg="white", fg="black")
        menu.add_command(
            label=t.get("ctx_copy"),
            image=self.icon_copy,
            compound="left",
            command=self.copy_selection,
            accelerator="Cmd+C"
        )

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
        # Разрешаем навигацию
        if event.keysym in ["Left", "Right", "Up", "Down", "Prior", "Next", "Home", "End"]:
            return None

        # УПРОЩЕННАЯ ЛОГИКА:
        # Если нажат Command (state 4 или 8) -> Разрешаем действие (Копирование и т.д.)
        # Если Command не нажат -> Блокируем ввод (чтобы нельзя было стирать)
        is_cmd = (event.state & 8) or (event.state & 4)
        if is_cmd:
            return None

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