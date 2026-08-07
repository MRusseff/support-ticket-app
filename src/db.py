from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

VALID_STATUSES = ["open", "in_progress", "resolved"]
VALID_PRIORITIES = ["low", "medium", "high"]


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Configure it in environment variables.")
    return database_url


def get_connection():
    """Create a database connection, handling connection string formats properly."""
    database_url = get_database_url()
    
    # psycopg3 requires proper handling of query parameters
    # Convert ?sslmode=require format to proper conninfo format
    if "?" in database_url:
        # Split base URL and query params
        base_url, query_string = database_url.split("?", 1)
        
        # Parse query parameters and add them as conninfo parameters
        params = {}
        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
        
        # Build conninfo string with proper formatting
        conninfo = base_url
        if params:
            # Add parameters in the format psycopg3 expects
            param_str = " ".join(f"{k}={v}" for k, v in params.items())
            conninfo = f"{base_url} {param_str}"
        
        return connect(conninfo, autocommit=False)
    else:
        return connect(database_url, autocommit=False)


def execute_sql_script(script_path: Path) -> None:
    sql = script_path.read_text(encoding="utf-8")
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()


def fetch_tickets(status_filter: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT
            ticket_id,
            title,
            status,
            priority,
            created_by,
            created_at
        FROM tickets
    """
    params: tuple[Any, ...] = ()
    if status_filter and status_filter != "all":
        query += " WHERE status = %s"
        params = (status_filter,)
    query += " ORDER BY created_at DESC"

    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        return list(cur.fetchall())


def fetch_ticket_messages(ticket_id: int) -> list[dict[str, Any]]:
    query = """
        SELECT
            message_id,
            ticket_id,
            message_text,
            author,
            created_at
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at ASC
    """
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, (ticket_id,))
        return list(cur.fetchall())


def create_ticket(title: str, created_by: str, status: str, priority: str) -> int:
    if not title.strip():
        raise ValueError("Title is required.")
    if not created_by.strip():
        raise ValueError("Created by is required.")
    if status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")

    query = """
        INSERT INTO tickets (title, status, priority, created_by)
        VALUES (%s, %s, %s, %s)
        RETURNING ticket_id
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (title.strip(), status, priority, created_by.strip()))
        ticket_id = cur.fetchone()[0]
        conn.commit()
        return ticket_id


def add_ticket_message(ticket_id: int, message_text: str, author: str) -> None:
    if not message_text.strip():
        raise ValueError("Message text is required.")
    if not author.strip():
        raise ValueError("Author is required.")

    query = """
        INSERT INTO ticket_messages (ticket_id, message_text, author)
        VALUES (%s, %s, %s)
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (ticket_id, message_text.strip(), author.strip()))
        conn.commit()


def update_ticket_status(ticket_id: int, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")

    query = """
        UPDATE tickets
        SET status = %s
        WHERE ticket_id = %s
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (new_status, ticket_id))
        conn.commit()


def fetch_ticket_counts() -> dict[str, int]:
    query = """
        SELECT status, COUNT(*) AS count
        FROM tickets
        GROUP BY status
    """
    counts = {"open": 0, "in_progress": 0, "resolved": 0}
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        for row in cur.fetchall():
            counts[row["status"]] = row["count"]
    return counts
