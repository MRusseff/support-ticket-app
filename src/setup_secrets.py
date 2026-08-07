"""
One-time setup script: creates the Databricks secret scope and stores the Lakebase connection URL.

Run this locally with the Databricks CLI configured, or from a notebook.
Never commit the resulting secret value anywhere.

Usage:
    python setup_secrets.py

This script creates:
- Secret scope: support-tickets
- Secret key: support-ticket-database-url
- ACL: users group with READ permission
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
from databricks.sdk.core import DatabricksError
import getpass

SCOPE_NAME = "support-tickets"
SECRET_KEY = "support-ticket-database-url"

w = WorkspaceClient()

# Create the secret scope (or skip if it already exists)
try:
    w.secrets.create_scope(scope=SCOPE_NAME)
    print(f"✓ Created secret scope '{SCOPE_NAME}'")
except DatabricksError as e:
    if "already exists" in str(e).lower():
        print(f"ℹ Secret scope '{SCOPE_NAME}' already exists, skipping creation")
    else:
        raise

# Store the Lakebase connection URL
print(f"\nEnter your Lakebase Postgres connection string.")
print("Format: postgresql://<user>:<password>@<host>:<port>/<database>?sslmode=require")
database_url = getpass.getpass("\nDatabase URL: ")

if not database_url.strip():
    raise ValueError("Database URL cannot be empty")

w.secrets.put_secret(
    scope=SCOPE_NAME,
    key=SECRET_KEY,
    string_value=database_url
)
print(f"✓ Stored secret '{SECRET_KEY}' in scope '{SCOPE_NAME}'")

# Grant READ permission to all users
w.secrets.put_acl(
    scope=SCOPE_NAME,
    principal="users",
    permission=workspace.AclPermission.READ,
)
print(f"✓ Granted READ permission to 'users' group")

print("\n✅ Setup complete!")
print(f"\nIMPORTANT: Update your app.yaml to reference this secret:")
print(f"  secret: {SCOPE_NAME}/{SECRET_KEY}")
