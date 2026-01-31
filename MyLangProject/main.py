import sys
import os

# --- МАГИЯ ОБНОВЛЕНИЙ ---
# Определяем путь к обновлениям
UPDATE_DIR = os.path.expanduser("~/Documents/MyLangUpdates")

# Если там есть папки с кодом, вставляем этот путь В НАЧАЛО списка импорта
if os.path.exists(UPDATE_DIR):
    sys.path.insert(0, UPDATE_DIR)
    print(f"Loaded updates from: {UPDATE_DIR}")
# ------------------------

# Теперь импортируем свои модули.
# Python возьмет их из UPDATE_DIR, если они там есть.
from ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()