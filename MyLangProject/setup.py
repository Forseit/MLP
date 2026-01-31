import os


def create_init_files():
    # Папки, где должны быть пустые __init__.py
    folders = ["core", "ui", "locales"]

    print("--- Проверка структуры ---")
    for folder in folders:
        if os.path.exists(folder):
            init_path = os.path.join(folder, "__init__.py")
            if not os.path.exists(init_path):
                print(f"[FIX] Создаю файл: {init_path}")
                with open(init_path, "w") as f:
                    pass  # Пустой файл
            else:
                print(f"[OK]  Файл есть: {init_path}")
        else:
            print(f"[ERR] Папка не найдена: {folder}")

    print("\n--- Проверка библиотек ---")
    try:
        import customtkinter
        import requests
        print("[OK]  Все библиотеки установлены!")
    except ImportError as e:
        print(f"[ERR] Ошибка библиотек: {e}")
        print("Попробуй выполнить в терминале: ./venv/bin/pip install customtkinter requests")


if __name__ == "__main__":
    create_init_files()