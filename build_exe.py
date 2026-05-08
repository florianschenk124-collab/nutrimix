#!/usr/bin/env python3
"""
NutrientMixer → Windows .exe Builder
=====================================

Voraussetzungen (einmalig):
    pip install pyinstaller customtkinter

Ausführen:
    python build_exe.py

Ergebnis:
    dist/NutrientMixer.exe  (Single-File, ~40–60 MB)
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def find_ctk_path():
    """Findet das customtkinter Installationsverzeichnis."""
    try:
        import customtkinter
        return Path(customtkinter.__file__).parent
    except ImportError:
        print("❌ customtkinter nicht installiert!")
        print("   pip install customtkinter")
        sys.exit(1)

def main():
    print("═══════════════════════════════════════════")
    print("  NutrientMixer → .exe Builder")
    print("═══════════════════════════════════════════")

    # Prüfe PyInstaller
    try:
        import PyInstaller
        print(f"  ✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  ❌ PyInstaller nicht installiert!")
        print("     pip install pyinstaller")
        sys.exit(1)

    ctk_path = find_ctk_path()
    print(f"  ✅ customtkinter: {ctk_path}")

    # Icon prüfen
    icon_path = Path(__file__).parent / "icon.ico"
    if not icon_path.exists():
        print("  ⚠️ icon.ico nicht gefunden – baue ohne Icon")
        icon_arg = []
    else:
        print(f"  ✅ Icon: {icon_path}")
        icon_arg = ["--icon", str(icon_path)]

    # Aufräumen
    for d in ["build", "dist"]:
        p = Path(__file__).parent / d
        if p.exists():
            shutil.rmtree(p)
            print(f"  🗑 {d}/ entfernt")

    spec_file = Path(__file__).parent / "NutrientMixer.spec"
    if spec_file.exists():
        spec_file.unlink()

    # PyInstaller Kommando
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "NutrientMixer",
        "--onefile",
        "--windowed",          # Kein Konsolenfenster
        "--noconfirm",
        # customtkinter Assets einbinden
        "--add-data", f"{ctk_path}{os.pathsep}customtkinter",
        # Eigene Datenverzeichnisse
        "--add-data", f"chemistry{os.pathsep}chemistry",
        "--add-data", f"database{os.pathsep}database",
        "--add-data", f"ui{os.pathsep}ui",
        # Hidden imports die PyInstaller nicht findet
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
        "--collect-all", "customtkinter",
        *icon_arg,
        "main.py",
    ]

    print(f"\n  🔨 Starte Build...")
    print(f"     {' '.join(cmd[-6:])}")
    print()

    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))

    if result.returncode == 0:
        exe_path = Path(__file__).parent / "dist" / "NutrientMixer.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n  ✅ BUILD ERFOLGREICH!")
            print(f"  📁 {exe_path}")
            print(f"  📏 {size_mb:.1f} MB")
            print(f"\n  Die .exe kann frei kopiert und gestartet werden.")
            print(f"  Benutzerdaten werden neben der .exe gespeichert.")
        else:
            print(f"\n  ⚠️ Build scheinbar OK, aber .exe nicht gefunden")
    else:
        print(f"\n  ❌ Build fehlgeschlagen (Exit-Code: {result.returncode})")
        print(f"     Prüfe die Ausgabe oben für Fehlerdetails.")

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
