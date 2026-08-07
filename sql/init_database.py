#!/usr/bin/env python3
"""Database initialization script.

Runs schema.sql and sample_data.sql against the configured database.

Usage:
    python sql/init_database.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from psycopg import connect

# Add src to path to import db module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

load_dotenv()


def get_connection():
    """Create database connection."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Set it in your .env file.\n"
            "Example: DATABASE_URL=postgresql://user@host/db?sslmode=require"
        )
    
    # Parse query parameters for psycopg3
    if "?" in database_url:
        base_url, query_string = database_url.split("?", 1)
        params = dict(param.split("=", 1) for param in query_string.split("&") if "=" in param)
        return connect(base_url, autocommit=False, **params)
    else:
        return connect(database_url, autocommit=False)


def run_sql_file(filepath: Path, conn):
    """Execute SQL from a file."""
    print(f"Running {filepath.name}...")
    sql = filepath.read_text(encoding="utf-8")
    
    with conn.cursor() as cur:
        cur.execute(sql)
    
    conn.commit()
    print(f"✅ {filepath.name} completed")


def main():
    """Initialize the database with schema and sample data."""
    sql_dir = Path(__file__).parent
    schema_file = sql_dir / "schema.sql"
    sample_data_file = sql_dir / "sample_data.sql"
    
    # Verify files exist
    if not schema_file.exists():
        print(f"❌ Error: {schema_file} not found")
        return 1
    
    if not sample_data_file.exists():
        print(f"❌ Error: {sample_data_file} not found")
        return 1
    
    print("🔧 Initializing support ticket database...\n")
    
    try:
        conn = get_connection()
        print("✅ Connected to database\n")
        
        # Run schema
        run_sql_file(schema_file, conn)
        print()
        
        # Run sample data
        run_sql_file(sample_data_file, conn)
        print()
        
        conn.close()
        print("✅ Database initialization complete!")
        print("\nYou can now run the app with:")
        print("  uv run --env-file .env -- streamlit run src/app.py")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
