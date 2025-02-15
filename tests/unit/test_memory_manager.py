"""Tests for the SQLite-based memory manager."""

import os
import pytest
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime, timezone
from aiorchestrator.memory.sqlite_manager import MemoryManager


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    try:
        os.unlink(f.name)
    except OSError:
        pass


@pytest.fixture
def temp_backup_dir():
    """Create a temporary backup directory with manual cleanup."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Manual cleanup to avoid file locking issues
    for _ in range(3):
        try:
            shutil.rmtree(temp_dir)
            break
        except PermissionError:
            time.sleep(0.1)


@pytest.fixture
def memory_manager(temp_backup_dir):
    """Create MemoryManager with test configuration."""
    db_path = os.path.join(temp_backup_dir, "test_db.db")
    return MemoryManager(
        db_path=db_path,
        backup_dir=temp_backup_dir,
        max_versions=3,
        compress=True
    )


def test_init_with_invalid_path():
    """Test initialization with invalid database path."""
    with pytest.raises(Exception):
        MemoryManager(db_path="/invalid/path/db.sqlite")


def test_compression(memory_manager):
    """Test data compression and decompression."""
    test_data = "test string"
    compressed = memory_manager._compress_data(test_data)
    decompressed = memory_manager._decompress_data(compressed)
    assert decompressed == test_data


def test_context_validation(memory_manager):
    """Test context data validation."""
    invalid_data = {
        "version": "1.0",
        "data": {}  # Missing timestamp
    }
    with pytest.raises(Exception):
        memory_manager._validate_context(invalid_data)


def test_version_cleanup(memory_manager):
    """Test old version cleanup."""
    # Store more versions than max_versions
    for i in range(5):
        memory_manager.store_context({"test": f"data_{i}"})

    versions = memory_manager.list_versions()
    assert len(versions) <= 3  # max_versions is 3


def test_backup_and_restore(memory_manager, temp_backup_dir):
    """Test backup creation and restoration."""
    # Store some data
    test_data = {"test": "backup_data"}
    memory_manager.store_context(test_data)

    # Create backup
    backup_path = memory_manager.create_backup()
    assert backup_path is not None
    assert os.path.exists(backup_path)

    # Modify data
    memory_manager.store_context({"test": "modified_data"})

    # Restore backup
    memory_manager.restore_backup(backup_path)

    # Verify data
    loaded_data = memory_manager.load_context()
    assert loaded_data == test_data


def test_in_memory_database():
    """Test in-memory database functionality."""
    manager = MemoryManager(db_path=":memory:")
    test_data = {"test": "memory_data"}
    manager.store_context(test_data)
    loaded_data = manager.load_context()
    assert loaded_data == test_data


def test_load_nonexistent_version(memory_manager):
    """Test loading a non-existent version."""
    loaded_data = memory_manager.load_context(version=999)
    assert loaded_data == {}


def test_list_versions_empty(memory_manager):
    """Test listing versions with empty database."""
    versions = memory_manager.list_versions()
    assert versions == []


def test_create_backup_in_memory():
    """Test backup creation with in-memory database."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = MemoryManager(
            db_path=":memory:",
            backup_dir=temp_dir
        )
        result = manager.create_backup()
        assert result is None


def test_store_and_load_with_compression(memory_manager):
    """Test storing and loading data with compression enabled."""
    test_data = {
        "complex_data": {
            "nested": {
                "array": [1, 2, 3],
                "string": "test" * 1000  # Large string to test compression
            }
        }
    }
    memory_manager.store_context(test_data)
    loaded_data = memory_manager.load_context()
    assert loaded_data == test_data
