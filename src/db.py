"""Database operations for the Support Ticket App.

Handles all interactions with the Lakebase Postgres database.
"""
import os
from typing import Any
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

VALID_STATUSES = ["open", "in_progress", "resolved"]


def get_connection():
    """Create a database connection to Lakebase.
    
    Psycopg3 requires query parameters (like sslmode=require) to be passed
    as keyword arguments, not in the URI query string.
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Set it in .env for local dev or configure the Databricks secret for deployment."
        )
    
    # Parse query parameters if present
    if "?" in database_url:
        base_url, query_string = database_url.split("?", 1)
        params = dict(param.split("=", 1) for param in query_string.split("&") if "=" in param)
        return connect(base_url, autocommit=False, **params)
    else:
        return connect(database_url, autocommit=False)


def fetch_all_tickets() -> list[dict[str, Any]]:
    """Fetch all tickets ordered by creation date (newest first)."""
    query = """
        SELECT ticket_id, title, status, created_by, created_at
        FROM tickets
        ORDER BY created_at DESC
    """
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        return list(cur.fetchall())


def fetch_tickets_by_status(status: str) -> list[dict[str, Any]]:
    """Fetch tickets filtered by status."""
    query = """
        SELECT ticket_id, title, status, created_by, created_at
        FROM tickets
        WHERE status = %s
        ORDER BY created_at DESC
    """
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, (status,))
        return list(cur.fetchall())


def fetch_ticket_messages(ticket_id: int) -> list[dict[str, Any]]:
    """Fetch all messages for a specific ticket."""
    query = """
        SELECT message_id, ticket_id, message_text, author, created_at
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at ASC
    """
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, (ticket_id,))
        return list(cur.fetchall())


def create_ticket(title: str, status: str, created_by: str) -> int:
    """Create a new ticket and return its ID."""
    if not title.strip():
        raise ValueError("Title cannot be empty")
    if not created_by.strip():
        raise ValueError("Created by cannot be empty")
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
    
    query = """
        INSERT INTO tickets (title, status, created_by)
        VALUES (%s, %s, %s)
        RETURNING ticket_id
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (title.strip(), status, created_by.strip()))
        ticket_id = cur.fetchone()[0]
        conn.commit()
        return ticket_id


def add_message(ticket_id: int, message_text: str, author: str) -> None:
    """Add a message to an existing ticket."""
    if not message_text.strip():
        raise ValueError("Message cannot be empty")
    if not author.strip():
        raise ValueError("Author cannot be empty")
    
    query = """
        INSERT INTO ticket_messages (ticket_id, message_text, author)
        VALUES (%s, %s, %s)
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (ticket_id, message_text.strip(), author.strip()))
        conn.commit()


def get_ticket_stats() -> dict[str, int]:
    """Get count of tickets by status."""
    query = """
        SELECT status, COUNT(*) as count
        FROM tickets
        GROUP BY status
    """
    stats = {status: 0 for status in VALID_STATUSES}
    
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        for row in cur.fetchall():
            stats[row["status"]] = row["count"]
    
    return stats
