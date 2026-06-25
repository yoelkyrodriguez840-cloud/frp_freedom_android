"""
Configuración de pruebas
"""

import pytest
import sys
import os

# Configurar entorno de prueba
os.environ["FRP_FREEDOM_TEST"] = "1"


@pytest.fixture
def mock_android_platform():
    """Mock de plataforma Android para pruebas"""
    sys.modules["jnius"] = MagicMock()
    sys.modules["android"] = MagicMock()
    sys.modules["android.storage"] = MagicMock()
    return sys.modules
