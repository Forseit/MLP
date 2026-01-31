import json
import os
import locale

# Исправление: Сохраняем конфиг в Документы пользователя,
# так как папка приложения на macOS может быть доступна только для чтения.
WORK_DIR = os.path.expanduser("~/Documents/MyLangProject")
CONFIG_FILE = os.path.join(WORK_DIR, "config.json")


class LocaleManager:
    def __init__(self):
        # Если папки в Документах нет — создаем её
        if not os.path.exists(WORK_DIR):
            try:
                os.makedirs(WORK_DIR)
            except Exception as e:
                print(f"Error creating config dir: {e}")

        # Путь к JSON файлам переводов (остается внутри программы)
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # Путь к файлу настроек (теперь в Документах)
        self.config_path = CONFIG_FILE

        self.lang_code = self.load_config()
        self.translations = {}
        self.load_translations()

    def load_config(self):
        """Загружает язык из файла в Документах, или берет системный"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    return data.get("language", "en")
            except:
                pass

        # Автоопределение
        try:
            sys_lang = locale.getdefaultlocale()[0]
            return 'ru' if sys_lang and sys_lang.startswith('ru') else 'en'
        except:
            return 'en'

    def save_config(self, lang_code):
        """Сохраняет выбранный язык в Документы"""
        self.lang_code = lang_code
        try:
            with open(self.config_path, "w") as f:
                json.dump({"language": lang_code}, f)
        except Exception as e:
            print(f"Error saving config: {e}")

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