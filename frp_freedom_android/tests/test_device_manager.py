"""
Tests para DeviceManagerAndroid
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from frp_freedom_android.core_android.device_manager_android import DeviceManagerAndroid
from frp_freedom_android.models.device_model import DeviceInfo


@pytest.mark.asyncio
async def test_scan_devices():
    """Test escaneo de dispositivos"""
    device_manager = DeviceManagerAndroid()

    # Mock de adapters
    with patch.object(device_manager.adb_adapter, "get_all_devices") as mock_get:
        mock_get.return_value = [
            {
                "serial": "test_serial_1",
                "model": "Pixel 6",
                "manufacturer": "Google",
                "android_version": "14.0",
                "connection_type": "adb",
            }
        ]

        devices = await device_manager.scan_devices()

        assert len(devices) == 1
        assert devices[0].serial == "test_serial_1"
        assert devices[0].model == "Pixel 6"
        assert devices[0].manufacturer == "Google"


@pytest.mark.asyncio
async def test_get_devices():
    """Test obtener dispositivos"""
    device_manager = DeviceManagerAndroid()

    # Simular dispositivos
    device_manager.devices = [
        DeviceInfo(
            serial="test_serial_1", model="Pixel 6", manufacturer="Google", android_version="14.0"
        )
    ]

    devices = device_manager.get_devices()
    assert len(devices) == 1


@pytest.mark.asyncio
async def test_get_device_by_serial():
    """Test obtener dispositivo por serial"""
    device_manager = DeviceManagerAndroid()

    device_manager.devices = [
        DeviceInfo(serial="serial_1", model="Pixel 6"),
        DeviceInfo(serial="serial_2", model="Galaxy S24"),
    ]

    device = device_manager.get_device_by_serial("serial_1")
    assert device is not None
    assert device.serial == "serial_1"
    assert device.model == "Pixel 6"

    device = device_manager.get_device_by_serial("no_existe")
    assert device is None


@pytest.mark.asyncio
async def test_is_device_available():
    """Test verificar disponibilidad de dispositivo"""
    device_manager = DeviceManagerAndroid()

    with patch.object(device_manager.adb_adapter, "ping_device") as mock_ping:
        mock_ping.return_value = True
        available = await device_manager.is_device_available("test_serial")
        assert available is True

        mock_ping.return_value = False
        available = await device_manager.is_device_available("test_serial")
        assert available is False
