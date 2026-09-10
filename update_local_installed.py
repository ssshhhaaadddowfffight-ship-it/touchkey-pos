"""
Update script to compile TouchKey POS and sync files directly into the installed folder:
C:\\Users\\raxatskiye\\AppData\\Local\\Programs\\TouchKey_POS
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def update_local():
    current_dir = Path(__file__).parent.resolve()
    os.chdir(str(current_dir))

    installed_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\TouchKey_POS"))
    
    print(f"1. Завершение запущенных процессов TouchKey_POS.exe...")
    subprocess.run(["taskkill", "/F", "/IM", "TouchKey_POS.exe"], capture_output=True)

    print(f"2. Сборка свежих бинарников...")
    from build_exe import build
    if not build():
        print("[ERROR] Сборка завершилась с ошибкой.")
        return False

    dist_dir = current_dir / "dist" / "TouchKey_POS"
    if not dist_dir.exists():
        print(f"[ERROR] Папка {dist_dir} не найдена.")
        return False

    print(f"3. Синхронизация файлов в: {installed_dir}...")
    installed_dir.mkdir(parents=True, exist_ok=True)

    for item in dist_dir.iterdir():
        dest = installed_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Copy icons
    shutil.copy2(current_dir / "app_icon.ico", installed_dir / "app_icon.ico")
    shutil.copy2(current_dir / "app_icon.png", installed_dir / "app_icon.png")

    print("\n=======================================================")
    print("[УСПЕХ] ПРОГРАММА УСПЕШНО ОБНОВЛЕНА В УСТАНОВЛЕННОЙ ПАПКЕ!")
    print(f"Путь: {installed_dir / 'TouchKey_POS.exe'}")
    print("=======================================================")

    # Launch the updated exe
    print("4. Запуск обновленной программы...")
    subprocess.Popen([str(installed_dir / "TouchKey_POS.exe")])
    return True

if __name__ == "__main__":
    update_local()
