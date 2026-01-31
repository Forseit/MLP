# core/system_info.py
import subprocess
import platform

def get_processor_name():
    try:
        # Команда macOS для получения названия чипа
        command = ["sysctl", "-n", "machdep.cpu.brand_string"]
        proc_name = subprocess.check_output(command).decode("utf-8").strip()
        return proc_name
    except:
        # Фолбэк, если что-то пошло не так
        return platform.processor()