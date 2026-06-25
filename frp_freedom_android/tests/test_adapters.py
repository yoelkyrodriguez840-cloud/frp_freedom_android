"""
Tests para adaptadores
"""

import pytest
from unittest.mock import patch, MagicMock

from frp_freedom_android.adapters.filesystem_adapter import FilesystemAdapter
from frp_freedom_android.adapters.usb_adapter import USBAdapter


def test_filesystem_adapter():
    """Test adaptador de sistema de archivos"""
    adapter = FilesystemAdapter()

    assert adapter.base_dir is not None
    assert adapter.logs_dir is not None
    assert adapter.cache_dir is not None

    # Test write/read
    test_path = adapter.cache_dir / "test.txt"
    assert adapter.write_file(test_path, "test content") is True

    content = adapter.read_file(test_path)
    assert content == "test content"

    assert adapter.delete_file(test_path) is True
    assert not test_path.exists()


def test_usb_adapter():
    """Test adaptador USB"""
    adapter = USBAdapter()

    # Test detección de dispositivos Android
    assert adapter._is_android_device(0x18D1) is True  # Google
    assert adapter._is_android_device(0x04E8) is True  # Samsung
    assert adapter._is_android_device(0x1234) is False

    # Test detección de ADB
    assert adapter._is_adb_device(0x18D1, 0xD001) is True
    assert adapter._is_adb_device(0x1234, 0x5678) is False
