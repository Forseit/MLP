import requests
import json
import os
import shutil
import zipfile  # <--- Добавили библиотеку для работы с архивами

# Путь, куда падают обновления
UPDATE_DIR = os.path.expanduser("~/Documents/MyLangUpdates")
CURRENT_VERSION = 5.02


class Updater:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.update_path = UPDATE_DIR

        # Создаем папку, если нет
        if not os.path.exists(self.update_path):
            os.makedirs(self.update_path)

    def check_for_updates(self):
        try:
            print(f"Checking update from {self.server_url}/version.json...")
            response = requests.get(f"{self.server_url}/version.json", timeout=2)
            if response.status_code == 200:
                data = response.json()
                server_version = data.get("version", 0)

                if server_version > CURRENT_VERSION:
                    return True, server_version
            return False, CURRENT_VERSION
        except Exception as e:
            print(f"Update check failed: {e}")
            return False, CURRENT_VERSION

    def download_update(self):
        """Скачивает update.zip и распаковывает его"""
        try:
            print("Downloading update.zip...")

            # 1. Ссылка на архив
            zip_url = f"{self.server_url}/update.zip"
            local_zip_path = os.path.join(self.update_path, "update.zip")

            # 2. Скачивание файла
            with requests.get(zip_url, stream=True) as r:
                r.raise_for_status()
                with open(local_zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            print("Download finished. Extracting...")

            # 3. Распаковка
            with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.update_path)

            # 4. Удаление самого архива (мусора)
            os.remove(local_zip_path)

            print(f"Updated successfully to {self.update_path}")
            return True

        except Exception as e:
            print(f"Critical Update Error: {e}")
            return False