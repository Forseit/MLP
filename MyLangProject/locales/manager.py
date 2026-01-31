# locales/manager.py
import json
import os
import locale

CONFIG_FILE = "config.json"


class LocaleManager:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.root_path = os.path.dirname(self.base_path)  # Папка проекта
        self.config_path = os.path.join(self.root_path, CONFIG_FILE)

        self.lang_code = self.load_config()
        self.translations = {}
        self.load_translations()

    def load_config(self):
        """Загружает язык из файла, или берет системный"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    return data.get("language", "en")
            except:
                pass

        # Автоопределение
        sys_lang = locale.getdefaultlocale()[0]
        return 'ru' if sys_lang and sys_lang.startswith('ru') else 'en'

    def save_config(self, lang_code):
        """Сохраняет выбранный язык"""
        self.lang_code = lang_code
        with open(self.config_path, "w") as f:
            json.dump({"language": lang_code}, f)
        self.load_translations()

    def load_translations(self):
        file_path = os.path.join(self.base_path, f"{self.lang_code}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            self.translations = {}

    def get(self, key):
        return self.translations.get(key, key)


t = LocaleManager()