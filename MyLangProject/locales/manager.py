import json
import os
import locale

WORK_DIR = os.path.expanduser("~/Documents/MyLangProject")
CONFIG_FILE = os.path.join(WORK_DIR, "config.json")

# Настройки по умолчанию
DEFAULT_CONFIG = {
    "language": "en",
    "font_size": 14,
    "autosave": False
}


class LocaleManager:
    def __init__(self):
        if not os.path.exists(WORK_DIR):
            try:
                os.makedirs(WORK_DIR)
            except Exception as e:
                print(f"Error creating config dir: {e}")

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = CONFIG_FILE

        # Загружаем конфиг полностью
        self.config = self.load_config()

        self.translations = {}
        self.load_translations()

    def load_config(self):
        """Загружает конфиг или создает дефолтный"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    # Объединяем с дефолтным, чтобы старые конфиги не ломали новые ключи
                    return {**DEFAULT_CONFIG, **data}
            except:
                pass

        # Автоопределение языка для первого запуска
        try:
            sys_lang = locale.getdefaultlocale()[0]
            detected_lang = 'ru' if sys_lang and sys_lang.startswith('ru') else 'en'
        except:
            detected_lang = 'en'

        initial_config = DEFAULT_CONFIG.copy()
        initial_config["language"] = detected_lang
        return initial_config

    def save_settings(self, new_settings):
        """Сохраняет словарь настроек"""
        self.config.update(new_settings)
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

        self.load_translations()  # Перезагружаем язык, если он сменился

    def load_translations(self):
        lang = self.config.get("language", "en")
        file_path = os.path.join(self.base_path, f"{lang}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            self.translations = {}

    def get(self, key):
        return self.translations.get(key, key)

    # Хелперы для доступа к настройкам
    def get_font_size(self):
        return self.config.get("font_size", 14)

    def get_lang(self):
        return self.config.get("language", "en")

    def is_autosave(self):
        return self.config.get("autosave", False)


t = LocaleManager()