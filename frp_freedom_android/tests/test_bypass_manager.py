"""
Tests para BypassManagerAndroid
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from frp_freedom_android.core_android.bypass_manager_android import BypassManagerAndroid
from frp_freedom_android.models.device_model import DeviceInfo, BypassMethod


@pytest.mark.asyncio
async def test_get_recommended_methods():
    """Test obtención de métodos recomendados"""
    device = DeviceInfo(
        serial="test_serial", model="Pixel 6", manufacturer="Google", android_version="14.0"
    )

    bypass_manager = BypassManagerAndroid(None)
    methods = bypass_manager.get_recommended_methods(device)

    assert len(methods) > 0
    assert all(isinstance(m, BypassMethod) for m in methods)


@pytest.mark.asyncio
async def test_get_methods():
    """Test obtención de todos los métodos"""
    bypass_manager = BypassManagerAndroid(None)
    methods = bypass_manager.get_methods()

    assert len(methods) > 0
    assert all(isinstance(m, BypassMethod) for m in methods)


@pytest.mark.asyncio
async def test_get_method_by_name():
    """Test obtener método por nombre"""
    bypass_manager = BypassManagerAndroid(None)

    method = bypass_manager.get_method_by_name("adb_setup_wizard")
    assert method is not None
    assert method.name == "adb_setup_wizard"
    assert method.category == "adb"

    method = bypass_manager.get_method_by_name("no_existe")
    assert method is None


@pytest.mark.asyncio
async def test_execute_bypass():
    """Test ejecución de bypass"""
    device = DeviceInfo(
        serial="test_serial", model="Pixel 6", manufacturer="Google", android_version="14.0"
    )

    bypass_manager = BypassManagerAndroid(None)

    # Mock de los exploits
    with patch.object(bypass_manager.adb_exploits, "execute_method") as mock_execute:
        mock_execute.return_value = {"result": "success", "message": "Bypass completado"}

        result = await bypass_manager.execute_bypass(device, "adb_setup_wizard")

        assert result["result"] == "success"


@pytest.mark.asyncio
async def test_execute_methods():
    """Test ejecución de múltiples métodos"""
    device = DeviceInfo(
        serial="test_serial", model="Pixel 6", manufacturer="Google", android_version="14.0"
    )

    bypass_manager = BypassManagerAndroid(None)

    methods = [
        BypassMethod(
            name="adb_setup_wizard",
            description="Test method",
            category="adb",
            risk_level="low",
            success_rate=0.8,
            estimated_time=5,
        )
    ]

    with patch.object(bypass_manager, "execute_bypass") as mock_execute:
        mock_execute.return_value = {"result": "success", "message": "Bypass completado"}

        results = await bypass_manager.execute_methods(device, methods)

        assert len(results) == 1
        assert results[0]["result"] == "success"


@pytest.mark.asyncio
async def test_cancel_execution():
    """Test cancelación de ejecución"""
    bypass_manager = BypassManagerAndroid(None)

    assert bypass_manager.is_cancelled is False

    bypass_manager.cancel_execution()
    assert bypass_manager.is_cancelled is True
