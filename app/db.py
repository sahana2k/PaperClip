"""SQLite persistence for users, workspaces, messages, and memory items."""

from __future__ import annotations

from datetime import datetime
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

from app.core import settings, get_logger

logger = get_logger(__name__)


def _get_db_path() -> str:
    url = settings.database_url or "sqlite:///./paperclip.db"
    if url.startswith("sqlite:///" ):
        path = url.replace("sqlite:///", "")
    elif url.startswith("sqlite://"):
        path = url.replace("sqlite://", "")
    else:
        # Fallback to local file if a non-sqlite URL is provided
        path = "./paperclip.db"

    if not os.path.isabs(path):
        path = os.path.abspath(path)
    return path


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if not _column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def init_db() -> None:
    """Create tables if they do not exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_type TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(workspace_id, key),
                FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ideation_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS experiment_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
            """
        )
        # Migrations
        _ensure_column(conn, "messages", "tool_type", "tool_type TEXT")
        # Migrations for existing databases
        _ensure_column(conn, "workspaces", "user_id", "user_id INTEGER")
        conn.commit()
    logger.info("SQLite database initialized")


def _safe_json_loads(payload: str) -> Dict[str, Any]:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {"raw": payload}


def create_user(email: str, password_hash: str, name: Optional[str] = None) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, name, password_hash, created_at),
        )
        user_id = cursor.lastrowid
        conn.commit()
    return get_user_by_id(user_id)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, email, name, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, email, name, password_hash, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def create_workspace(user_id: int, name: str, description: Optional[str]) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO workspaces (user_id, name, description, created_at) VALUES (?, ?, ?, ?)",
            (user_id, name, description, created_at),
        )
        workspace_id = cursor.lastrowid
        conn.commit()
    return get_workspace(workspace_id, user_id)


def list_workspaces(user_id: int) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, user_id, name, description, created_at FROM workspaces WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_workspace(workspace_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, user_id, name, description, created_at FROM workspaces WHERE id = ? AND user_id = ?",
            (workspace_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def delete_workspace(workspace_id: int, user_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM workspaces WHERE id = ? AND user_id = ?",
            (workspace_id, user_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def add_message(workspace_id: int, role: str, content: str, tool_type: Optional[str] = None) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (workspace_id, role, content, tool_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (workspace_id, role, content, tool_type, created_at),
        )
        message_id = cursor.lastrowid
        conn.commit()
    return {
        "id": message_id,
        "workspace_id": workspace_id,
        "role": role,
        "content": content,
        "tool_type": tool_type,
        "created_at": created_at,
    }


def list_messages(workspace_id: int, limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, workspace_id, role, content, tool_type, created_at
            FROM messages
            WHERE workspace_id = ?
            ORDER BY created_at ASC
            LIMIT ? OFFSET ?
            """,
            (workspace_id, limit, offset),
        ).fetchall()
    return [dict(row) for row in rows]


def add_memory_item(workspace_id: int, key: str, value: str) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO memory_items (workspace_id, key, value, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(workspace_id, key) DO UPDATE SET value = excluded.value
            """,
            (workspace_id, key, value, created_at),
        )
        conn.commit()
    return {
        "workspace_id": workspace_id,
        "key": key,
        "value": value,
        "created_at": created_at,
    }


def list_memory_items(workspace_id: int) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, workspace_id, key, value, created_at
            FROM memory_items
            WHERE workspace_id = ?
            ORDER BY created_at DESC
            """,
            (workspace_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_memory_item(workspace_id: int, key: str) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM memory_items WHERE workspace_id = ? AND key = ?",
            (workspace_id, key),
        )
        conn.commit()
    return cursor.rowcount > 0


def create_ideation_item(workspace_id: int, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    payload_json = json.dumps(payload)
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO ideation_items (workspace_id, topic, payload, created_at) VALUES (?, ?, ?, ?)",
            (workspace_id, topic, payload_json, created_at),
        )
        item_id = cursor.lastrowid
        conn.commit()
    return {
        "id": item_id,
        "workspace_id": workspace_id,
        "topic": topic,
        "payload": payload,
        "created_at": created_at,
    }


def list_ideation_items(workspace_id: int) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, workspace_id, topic, payload, created_at
            FROM ideation_items
            WHERE workspace_id = ?
            ORDER BY created_at DESC
            """,
            (workspace_id,),
        ).fetchall()
    items = []
    for row in rows:
        payload = _safe_json_loads(row["payload"])
        items.append({
            "id": row["id"],
            "workspace_id": row["workspace_id"],
            "topic": row["topic"],
            "payload": payload,
            "created_at": row["created_at"],
        })
    return items


def delete_ideation_item(workspace_id: int, item_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM ideation_items WHERE workspace_id = ? AND id = ?",
            (workspace_id, item_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def create_experiment_plan(workspace_id: int, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    payload_json = json.dumps(payload)
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO experiment_plans (workspace_id, topic, payload, created_at) VALUES (?, ?, ?, ?)",
            (workspace_id, topic, payload_json, created_at),
        )
        plan_id = cursor.lastrowid
        conn.commit()
    return {
        "id": plan_id,
        "workspace_id": workspace_id,
        "topic": topic,
        "payload": payload,
        "created_at": created_at,
    }


def list_experiment_plans(workspace_id: int) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, workspace_id, topic, payload, created_at
            FROM experiment_plans
            WHERE workspace_id = ?
            ORDER BY created_at DESC
            """,
            (workspace_id,),
        ).fetchall()
    plans = []
    for row in rows:
        payload = _safe_json_loads(row["payload"])
        plans.append({
            "id": row["id"],
            "workspace_id": row["workspace_id"],
            "topic": row["topic"],
            "payload": payload,
            "created_at": row["created_at"],
        })
    return plans


def delete_experiment_plan(workspace_id: int, plan_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM experiment_plans WHERE workspace_id = ? AND id = ?",
            (workspace_id, plan_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def create_resource(workspace_id: int, type: str, title: str, content: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat()
    metadata_json = json.dumps(metadata) if metadata else None
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO resources (workspace_id, type, title, content, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (workspace_id, type, title, content, metadata_json, created_at),
        )
        resource_id = cursor.lastrowid
        conn.commit()
    return {
        "id": resource_id,
        "workspace_id": workspace_id,
        "type": type,
        "title": title,
        "content": content,
        "metadata": metadata,
        "created_at": created_at,
    }


def get_resources(workspace_id: int) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, workspace_id, type, title, content, metadata, created_at
            FROM resources
            WHERE workspace_id = ?
            ORDER BY created_at DESC
            """,
            (workspace_id,),
        ).fetchall()
    
    resources = []
    for row in rows:
        metadata = _safe_json_loads(row["metadata"]) if row["metadata"] else None
        resources.append({
            "id": row["id"],
            "workspace_id": row["workspace_id"],
            "type": row["type"],
            "title": row["title"],
            "content": row["content"],
            "metadata": metadata,
            "created_at": row["created_at"],
        })
    return resources


def delete_resource(workspace_id: int, resource_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM resources WHERE workspace_id = ? AND id = ?",
            (workspace_id, resource_id),
        )
        conn.commit()
    return cursor.rowcount > 0
