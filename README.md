# Support Ticket App

**Day 1 Homework: Build a Lakebase-Powered AI Support App**

A simple internal support ticket system built with Streamlit and Lakebase (Postgres).

## 📋 Features

* View all support tickets
* Filter tickets by status (open, in progress, resolved)
* Create new tickets
* Add messages to tickets
* Real-time ticket statistics dashboard

## 🗄️ Database Schema

### `tickets` table
```sql
ticket_id    SERIAL PRIMARY KEY
title        VARCHAR(255) NOT NULL
status       VARCHAR(50) CHECK (status IN ('open', 'in_progress', 'resolved'))
created_by   VARCHAR(100) NOT NULL
created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### `ticket_messages` table
```sql
message_id   SERIAL PRIMARY KEY
ticket_id    INTEGER REFERENCES tickets(ticket_id) ON DELETE CASCADE
message_text TEXT NOT NULL
author       VARCHAR(100) NOT NULL
created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## 🚀 Setup Instructions

### Prerequisites

* Python 3.11+
* [uv](https://docs.astral.sh/uv/) package manager
* Lakebase Postgres database
* Databricks workspace (for deployment)

### 1. Install Dependencies

```bash
cd support-ticket-app
uv sync
```

### 2. Set Up Database

Run the schema and sample data scripts on your Lakebase database:

```bash
# Using psql
psql "$DATABASE_URL" < sql/schema.sql
psql "$DATABASE_URL" < sql/sample_data.sql
```

Or manually run the SQL files using a database client.

### 3. Configure Environment

Create a `.env` file with your database connection:

```bash
cp .env.example .env
```

Edit `.env` and add your Lakebase connection string:

```env
DATABASE_URL=postgresql://user@host:port/database?sslmode=require
```

**Important:** For psycopg3 compatibility, use the format shown above. Query parameters like `?sslmode=require` are automatically parsed.

### 4. Run Locally

```bash
uv run --env-file .env -- streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔐 Deploy to Databricks Apps

### 1. Set Up Databricks Secret

Store your database connection string in Databricks:

```bash
# Using the setup script
uv run python src/setup_secrets.py

# Or manually
databricks secrets create-scope support-tickets
databricks secrets put-secret support-tickets support-ticket-database-url
databricks secrets put-acl support-tickets users READ
```

### 2. Deploy the App

```bash
databricks apps create support-ticket-app --description "Support ticket system"
databricks apps deploy support-ticket-app --source-path .
```

Or deploy through the Databricks UI:

1. Go to **Apps** in your Databricks workspace
2. Click **Create App**
3. Connect to this repository
4. Select `app.yaml`
5. Deploy

## 📁 Project Structure

```
support-ticket-app/
├── app.yaml                 # Databricks App configuration
├── pyproject.toml           # Python dependencies
├── .env.example             # Environment template
├── README.md
├── sql/
│   ├── schema.sql           # Database schema
│   └── sample_data.sql      # Sample tickets and messages
└── src/
    ├── app.py               # Streamlit application
    ├── db.py                # Database operations
    └── setup_secrets.py     # Secret configuration script
```

## ✅ Sample Data

The `sql/sample_data.sql` file includes:

* **4 sample tickets** with varying statuses
* **2+ messages per ticket** showing conversation threads
* Realistic support scenarios (login issues, dashboard errors, etc.)

## 🔧 Troubleshooting

### Connection Errors

If you see `extra key/value separator` errors:

* The app automatically handles psycopg3's requirement to pass query parameters as kwargs
* Ensure your `DATABASE_URL` is NOT base64 encoded
* Format: `postgresql://user@host/db?sslmode=require`

### Secret Issues

If the deployed app can't connect:

* Verify the secret exists: `databricks secrets list-secrets support-tickets`
* Check the secret value is correct (not base64 encoded)
* Ensure `app.yaml` references: `support-tickets/support-ticket-database-url`

## 📝 Notes

* All timestamps are in UTC
* Foreign key constraints ensure referential integrity
* `ON DELETE CASCADE` automatically removes messages when tickets are deleted
* The app uses Streamlit's session state for UI interactions
