"""
Build script to compile TouchKey POS Pro into standalone Windows executable with custom icon.
"""

import os
import subprocess
import sys

def build():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    print(">>> Building TouchKey_POS.exe...")

    icon_path = os.path.join(current_dir, "app_icon.ico")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=TouchKey_POS",
        f"--icon={icon_path}",
        f"--add-data=app_icon.ico;.",
        f"--add-data=app_icon.png;.",
        "--clean",
        "main.py"
    ]

    print("Executing: " + " ".join(cmd))
    res = subprocess.run(cmd)

    if res.returncode == 0:
        print("\n[SUCCESS] TouchKey_POS.exe built successfully!")
        dist_folder = os.path.join(current_dir, 'dist', 'TouchKey_POS')
        exe_path = os.path.join(dist_folder, 'TouchKey_POS.exe')
        print(f"Output folder: {dist_folder}")
        print(f"Executable: {exe_path}")
        return True
    else:
        print("\n[ERROR] Build failed.")
        return False

if __name__ == "__main__":
    build()
