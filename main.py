#!/usr/bin/env python3
"""
FRP Freedom Android - Punto de entrada principal
"""

import sys
import os


def main():
    """Punto de entrada principal"""
    try:
        from .android_app import main as app_main

        app_main()
    except ImportError:
        # Si falla la importación relativa, intentar absoluta
        import frp_freedom_android

        frp_freedom_android.main()


if __name__ == "__main__":
    main()
