import pytest
from aiorchestrator.memory.sqlite_manager import MemoryManager

@pytest.fixture
def production_manager(tmp_path):
    return MemoryManager(
        db_path=str(tmp_path / "prod.db"),
        backup_dir=str(tmp_path / "backups"),
        max_versions=5,
        compress=True
    )

def test_full_workflow(production_manager):
    # Store initial data
    production_manager.store_context({"user": "admin", "config": {}})
    
    # Create backup
    backup_path = production_manager.create_backup()
    
    # Simulate disaster
    production_manager.store_context({"user": "hacker", "config": {}})
    
    # Restore from backup
    production_manager.restore_backup(backup_path)
    
    # Verify recovery
    data = production_manager.load_context()
    assert data["user"] == "admin"
