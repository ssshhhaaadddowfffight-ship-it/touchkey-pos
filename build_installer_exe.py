"""
Compiles Inno Setup installer for TouchKey POS Pro with auto-process kill.
"""

import os
import subprocess
import sys
from pathlib import Path

def build_installer():
    current_dir = Path(__file__).parent.resolve()
    os.chdir(str(current_dir))

    # Auto kill previous setup if open
    subprocess.run(["taskkill", "/F", "/IM", "TouchKey_POS_Setup.exe"], capture_output=True)

    iscc_path = Path("C:/Program Files (x86)/Inno Setup 6/iscc.exe")
    if not iscc_path.exists():
        iscc_path = Path("C:/Program Files/Inno Setup 6/iscc.exe")

    if not iscc_path.exists():
        print("[ERROR] Inno Setup iscc.exe not found!")
        return False

    iss_file = current_dir / "installer.iss"
    if not iss_file.exists():
        print(f"[ERROR] installer.iss not found: {iss_file}")
        return False

    dist_dir = current_dir / "dist" / "TouchKey_POS"
    if not dist_dir.exists() or not (dist_dir / "TouchKey_POS.exe").exists():
        print("[INFO] Building binaries first...")
        from build_exe import build
        if not build():
            return False

    print("\n>>> Compiling TouchKey_POS_Setup.exe with Inno Setup...")
    cmd = [str(iscc_path), str(iss_file)]
    res = subprocess.run(cmd)

    if res.returncode == 0:
        setup_exe = current_dir / "installer_output" / "TouchKey_POS_Setup.exe"
        print("\n=======================================================")
        print("[SUCCESS] TouchKey_POS_Setup.exe CREATED SUCCESSFULLY!")
        print(f"File: {setup_exe}")
        print("=======================================================")
        return True
    else:
        print("[ERROR] Inno Setup compilation failed.")
        return False

if __name__ == "__main__":
    build_installer()
