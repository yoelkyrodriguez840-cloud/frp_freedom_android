#!/usr/bin/env python3
"""
Setup script for FRP Freedom Android
"""

import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """Instalar dependencias"""
    print("Instalando dependencias...")

    deps = ["flet", "jnius", "pyyaml"]  # , "cryptography"]

    for dep in deps:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

    print("Dependencias instaladas correctamente.")


def build_apk():
    """Construir APK"""
    print("Construyendo APK...")

    # Crear directorio build
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    # Ejecutar flet build
    cmd = [
        sys.executable,
        "-m",
        "flet",
        "build",
        "apk",
        "--build-number",
        "1",
        "--version",
        "1.0.0",
    ]

    try:
        subprocess.check_call(cmd)
        print("APK construida correctamente.")
        print(f"APK ubicación: {build_dir}/app-release.apk")
    except subprocess.CalledProcessError as e:
        print(f"Error construyendo APK: {e}")
        sys.exit(1)


def main():
    """Script principal"""
    print("FRP Freedom Android - Setup")
    print("=" * 40)

    # Instalar dependencias
    install_dependencies()

    # Construir APK
    build_apk()

    print("\n¡Setup completado!")
    print("Para instalar la APK en tu dispositivo:")
    print("  adb install build/app-release.apk")


if __name__ == "__main__":
    main()
