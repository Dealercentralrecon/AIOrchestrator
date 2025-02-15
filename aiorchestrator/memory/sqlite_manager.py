# aiorchestrator/memory/sqlite_manager.py
"""SQLite-based memory manager for versioning, compression, and backup."""

import sqlite3
import json
import zlib
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
from pathlib import Path
import jsonschema
import os
import time
import tempfile
from ..db import DatabaseManager

logger = logging.getLogger(__name__)


class SQLiteManager(DatabaseManager):
    CONTEXT_SCHEMA = {
        "type": "object",
        "properties": {
            "version": {"type": "string"},
            "timestamp": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["version", "timestamp", "data"],
    }

    def __init__(
        self,
        db_path: str = ":memory:",
        max_versions: int = 10,
        compress: bool = True,
        backup_dir: Optional[str] = None,
    ):
        """Initialize enhanced SQLite memory manager.

        Args:
            db_path: Path to SQLite database
            max_versions: Maximum number of versions to keep
            compress: Whether to compress stored data
            backup_dir: Directory for automatic backups
        """
        self.db_path = db_path
        self.max_versions = max_versions
        self.compress = compress
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.conn = None

        try:
            self.connect()
            if self.backup_dir:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized SQLiteManager with database at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    async def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self) -> None:
        """Initialize database schema with versioning support."""
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    id TEXT,
                    version INTEGER,
                    data TEXT NOT NULL,
                    compressed BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id, version)
                )
                """
            )
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY,
                    agent_id TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    agent_id TEXT PRIMARY KEY,
                    success_rate REAL,
                    avg_response_time REAL,
                    last_healing TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_versions (
                    id INTEGER PRIMARY KEY,
                    agent_id TEXT,
                    hash TEXT,
                    code TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_agent_hash 
                ON code_versions (agent_id, hash)
            ''')
            self.conn.commit()
            logger.info("Database schema initialized with versioning support")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize schema: {str(e)}")
            raise

    def _compress_data(self, data: str) -> bytes:
        """Compress string data using zlib."""
        return zlib.compress(data.encode())

    def _decompress_data(self, data: bytes) -> str:
        """Decompress zlib compressed data."""
        return zlib.decompress(data).decode()

    def _validate_context(self, data: Dict[str, Any]) -> None:
        """Validate context data against schema."""
        try:
            jsonschema.validate(instance=data, schema=self.CONTEXT_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Context validation failed: {str(e)}")
            raise

    async def store_context(self, data: Dict[str, Any]) -> None:
        """Store versioned context data with optional compression.

        Args:
            data: Dictionary containing context data
        """
        try:
            context = {
                "version": datetime.now(timezone.utc).isoformat(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
            }

            self._validate_context(context)

            self.cursor.execute(
                "SELECT MAX(version) FROM memory WHERE id = ?", ("context",)
            )
            current_version = self.cursor.fetchone()[0] or 0
            next_version = current_version + 1

            serialized = json.dumps(context)
            if self.compress:
                serialized = self._compress_data(serialized)

            with self.conn:
                self.cursor.execute(
                    "INSERT INTO memory (id, version, data, compressed) "
                    "VALUES (?, ?, ?, ?)",
                    ("context", next_version, serialized, self.compress),
                )

            if next_version > self.max_versions:
                self.cursor.execute(
                    "DELETE FROM memory WHERE id = ? AND version <= ?",
                    ("context", next_version - self.max_versions),
                )

            if self.backup_dir:
                self.create_backup()

            logger.info(f"Stored context version {next_version}")

        except Exception as e:
            logger.error(f"Failed to store context: {str(e)}")
            raise

    async def load_context(self, version: Optional[int] = None) -> Dict[str, Any]:
        """Load context data with optional version specification.

        Args:
            version: Specific version to load, None for latest

        Returns:
            Dictionary containing context data
        """
        try:
            if version:
                query = (
                    "SELECT data, compressed FROM memory WHERE id = ? AND version = ?"
                )
                params = ("context", version)
            else:
                query = (
                    "SELECT data, compressed FROM memory "
                    "WHERE id = ? ORDER BY version DESC LIMIT 1"
                )
                params = ("context",)

            self.cursor.execute(query, params)
            row = self.cursor.fetchone()

            if row:
                data, is_compressed = row
                if is_compressed:
                    data = self._decompress_data(data)
                context = json.loads(data)
                msg = f"Loaded context version {version if version else 'latest'}"
                logger.info(msg)
                return context["data"]

            logger.info("No context found, returning empty dict")
            return {}

        except Exception as e:
            logger.error(f"Failed to load context: {str(e)}")
            raise

    async def list_versions(self) -> List[Dict[str, Any]]:
        """List all available context versions."""
        try:
            self.cursor.execute(
                "SELECT version, timestamp FROM memory WHERE id = ? "
                "ORDER BY version DESC",
                ("context",),
            )
            versions = [{"version": row[0], "timestamp": row[1]} for row in self.cursor]
            return versions
        except sqlite3.Error as e:
            logger.error(f"Failed to list versions: {str(e)}")
            raise

    async def create_backup(self) -> Optional[str]:
        """Create atomic backup."""
        if self.db_path == ":memory:":
            return None

        try:
            self.conn.commit()  # Ensure transaction is committed
            backup_name = f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)
            self.cursor.execute(f"VACUUM INTO '{backup_path}'")
            logger.info(f"Created backup at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise

    async def restore_backup(self, backup_path: str) -> None:
        """Restore database using SQLite backup API without file operations."""
        try:
            # Connect to backup database
            with sqlite3.connect(backup_path) as backup_conn:
                # Connect to main database
                main_conn = sqlite3.connect(self.db_path)
                
                # Backup from backup DB to main DB
                backup_conn.backup(main_conn, pages=1, progress=None)
                
                # Close and replace original connection
                main_conn.close()
                
                # Reinitialize connection
                if self.conn:
                    self.conn.close()
                self.conn = sqlite3.connect(self.db_path)
                self.cursor = self.conn.cursor()
                self.init_db()
                
                # Verify integrity
                self.cursor.execute("PRAGMA integrity_check")
                self.cursor.execute("PRAGMA quick_check")
                
                logger.info(f"Successfully restored from {backup_path}")
                
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise

    async def store_interaction(self, interaction_data):
        """Store agent interaction data"""
        self.cursor.execute('''
            INSERT INTO interactions 
            (agent_id, input_data, output_data, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (interaction_data['agent_id'], 
              json.dumps(interaction_data['input']), 
              json.dumps(interaction_data['output'])))
        self.conn.commit()

    async def store_code_version(self, agent_id: str, code_hash: str, code: str):
        self.cursor.execute("""
            INSERT INTO code_versions 
            (agent_id, hash, code, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (agent_id, code_hash, code))
        self.conn.commit()

    async def get_code_version(self, agent_id: str, code_hash: str) -> Optional[str]:
        self.cursor.execute('''
            SELECT code FROM code_versions
            WHERE agent_id = ? AND hash = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (agent_id, code_hash))
        result = self.cursor.fetchone()
        return result[0] if result else None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    async def __del__(self) -> None:
        """Ensure database connection is closed."""
        try:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")