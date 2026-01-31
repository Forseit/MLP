# ui/theme.py
class Theme:
    # --- ОСНОВНЫЕ ЦВЕТА ---
    BG_COLOR = "#191919"  # Очень темный серый, почти черный (Deep Dark)
    FG_COLOR = "#252526"  # Цвет панелей
    ACCENT = "#0A84FF"  # macOS Blue
    ACCENT_HOVER = "#007AFF"

    # --- ТЕКСТ ---
    TEXT_MAIN = "#FFFFFF"
    TEXT_DIM = "#808080"  # Для подписей

    # --- РЕДАКТОР ---
    EDITOR_BG = "#1E1E1E"  # Классический цвет VS Code
    EDITOR_FG = "#D4D4D4"  # Светло-серый код

    # --- КОНСОЛЬ (ВЫВОД) ---
    CONSOLE_BG = "#121212"  # Глубокий черный

    # Тот самый "кайфовый серый" для успешного вывода
    # Это цвет "Cool Gray", он читаемый, но не режет глаза как белый
    CONSOLE_TEXT_NORMAL = "#A8A8B6"

    CONSOLE_TEXT_ERROR = "#FF453A"  # Мягкий красный (macOS style)

    # --- ШРИФТЫ ---
    FONT_CODE = ("Menlo", 14)
    FONT_UI = ("SF Pro Text", 13, "bold")