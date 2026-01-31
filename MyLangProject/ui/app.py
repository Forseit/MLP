import customtkinter as ctk
from ui.theme import Theme
from ui.widgets import CodeEditor, Console
from ui.settings_window import SettingsWindow
from core.interpreter import Interpreter
from core.system_info import get_processor_name
from locales.manager import t


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Получаем имя процессора
        self.cpu_name = get_processor_name()

        # Настройки окна
        self.geometry("1000x700")
        ctk.set_appearance_mode("Dark")

        # Биндим горячую клавишу (Cmd+D для macOS)
        self.bind("<Command-d>", self.open_settings)

        # Сетка: 2 колонки (редактор и консоль), 2 строки (основная и кнопка)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # 1. Левая панель (Редактор)
        self.editor = CodeEditor(self, "LOADING...")
        self.editor.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.editor.set_code('текст("Привет, ' + self.cpu_name + '")\nтекст(\'Ошибка тут ->")')

        # 2. Правая панель (Консоль)
        self.console = Console(self, "LOADING...")
        self.console.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # 3. Кнопка запуска (Снизу)
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

        # Инициализация интерпретатора
        self.interpreter = Interpreter(console_callback=self.console.write)

        # Применяем переводы (Locale)
        self.reload_ui()

        # --- СИСТЕМА ОБНОВЛЕНИЙ ---
        # Инициализируем переменную апдейтера
        self.updater = None
        # Проверяем обновления через 1 секунду (1000 мс) после запуска,
        # чтобы интерфейс успел отрисоваться и не завис
        self.after(1000, self.check_updates_bg)

    def reload_ui(self):
        """Обновляет все тексты интерфейса при смене языка"""
        # Динамический заголовок окна
        app_title = f"MyLang IDE ({self.cpu_name})"
        self.title(app_title)

        self.editor.set_title(t.get("editor_title"))
        self.console.set_title(t.get("console_title"))
        self.run_btn.configure(text=t.get("run_button"))

    def open_settings(self, event=None):
        """Открывает модальное окно настроек"""
        SettingsWindow(self)

    def run_program(self):
        """Запуск кода через интерпретатор"""
        self.console.clear()
        code = self.editor.get_code()
        self.interpreter.execute(code)

    # --- МЕТОДЫ ОБНОВЛЕНИЯ ---

    def check_updates_bg(self):
        """Фоновая проверка обновлений"""
        # Импорт внутри метода, чтобы избежать циклических ссылок при старте
        from core.updater import Updater

        self.updater = Updater()
        # Проверяем версию (вернет True, если на сервере версия больше)
        has_update, version = self.updater.check_for_updates()

        if has_update:
            self.show_update_button(version)

    def show_update_button(self, version):
        """Показывает красивую зеленую кнопку в правом верхнем углу"""
        self.update_btn = ctk.CTkButton(
            self,
            text=f"{t.get('update_avail')} (v{version})",
            fg_color="#28a745",  # Зеленый цвет успеха
            hover_color="#218838",
            command=self.perform_update,
            width=150
        )
        # place позволяет разместить поверх сетки (абсолютное позиционирование)
        # relx/rely - координаты от 0 до 1 (0.98 = правый край, 0.02 = самый верх)
        self.update_btn.place(relx=0.98, rely=0.02, anchor="ne")

    def perform_update(self):
        """Скачивает и распаковывает архив"""
        if self.updater.download_update():
            # Если успешно скачалось
            self.update_btn.configure(
                text=t.get("update_msg"),
                fg_color="#6c757d",  # Серый цвет (отключено)
                state="disabled"
            )
            # В реальном приложении здесь можно предложить перезагрузку:
            # os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            # Если ошибка скачивания
            self.update_btn.configure(text="Error downloading", fg_color="#dc3545")