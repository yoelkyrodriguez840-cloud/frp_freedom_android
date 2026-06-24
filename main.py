#!/usr/bin/env python3
"""
FRP Freedom Android - Punto de entrada para Flet
"""

import sys
import os

# Agregar el directorio actual al path para que Flet pueda encontrar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Punto de entrada principal para Flet"""
    try:
        # Intentar importar desde la estructura de paquete
        from frp_freedom_android.android_app import main as app_main

        app_main()
    except ImportError:
        # Si falla, intentar importar directamente
        try:
            from android_app import main as app_main

            app_main()
        except ImportError as e:
            print(f"Error: No se pudo importar la aplicación: {e}")
            print("Directorio actual:", os.getcwd())
            print("Archivos en el directorio:", os.listdir())
            sys.exit(1)


if __name__ == "__main__":
    main()
