# aiorchestrator/memory/__init__.py
"""Memory management module for AI Orchestrator"""

import logging
from typing import Any, Dict

from .sqlite_manager import MemoryManager, SQLiteManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize memory manager
try:
    _manager = MemoryManager()
    logger.info("Memory manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize memory manager: {str(e)}")
    raise


def save_context(data: Dict[str, Any]) -> None:
    """
    Save context data to persistent storage

    Args:
        data: Dictionary containing context data
    """
    try:
        _manager.store_context(data)
        logger.info(f"Saved context data: {len(data)} items")
    except Exception as e:
        logger.error(f"Failed to save context: {str(e)}")
        raise


def load_context() -> Dict[str, Any]:
    """
    Load context data from persistent storage

    Returns:
        Dictionary containing context data
    """
    try:
        context = _manager.load_context()
        logger.info(f"Loaded context data: {len(context)} items")
        return context
    except Exception as e:
        logger.error(f"Failed to load context: {str(e)}")
        raise


# Export public interface
__all__ = ["save_context", "load_context", "SQLiteManager"]
