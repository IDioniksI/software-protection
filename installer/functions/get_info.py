import os
import ctypes
from screeninfo import get_monitors
import psutil
import json


def get_information(path):
    """
    Отримує інформацію про систему

    :param path: диск де виконується скрипт
    :return: інформація про систему
    """
    # Отримати ім'я користувача поточного користувача
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    # Отримати ім'я комп'ютера поточного користувача
    computer_name = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME")
    # Отримати шлях до папки операційної системи
    os_folder = os.environ.get("SystemRoot") or os.environ.get("WINDIR")
    # Отримати системні файли операційної системи
    system32_folder = os.path.join(os_folder, "System32")
    # Отримати кількість кнопок миші
    num_buttons = ctypes.windll.user32.GetSystemMetrics(43)
    # Отримати ширину екрану
    width = get_monitors()[0].width
    # Отримати набір дисків
    drives = [d.device for d in psutil.disk_partitions()]
    # Отримати обсяг диска, на якому встановлена програма
    usage = psutil.disk_usage(path)
    usage = usage.total

    system_info = {
        "Username": username,
        "Computer Name": computer_name,
        "OS Folder": os_folder,
        "System32 Folder": system32_folder,
        "Mouse Buttons": num_buttons,
        "Screen Width": width,
        "Disk Drives": drives,
        "Disk Space": usage
    }

    return json.dumps(system_info, indent=4)



if __name__ == "__main__":
    print(get_information(r'F:\\'))
