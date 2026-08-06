# Support Ticket App (Databricks + Lakebase)

This project is a small internal support system built as a Databricks App. It stores all operational data in Lakebase.

## Features implemented

- View all support tickets
- Filter tickets by status (`open`, `in_progress`, `resolved`)
- Select a ticket and view its messages
- Create a new ticket
- Add a message to an existing ticket
- Update a ticket status
- Ticket statistics by status
- Input validation and user-friendly error messages
- Priority field (`low`, `medium`, `high`)

## Data model

### `tickets`

- `ticket_id` (PK)
- `title`
- `status`
- `priority`
- `created_by`
- `created_at`

### `ticket_messages`

- `message_id` (PK)
- `ticket_id` (FK -> `tickets.ticket_id`)
- `message_text`
- `author`
- `created_at`

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Access to a Lakebase database with a Postgres-compatible connection string
- Databricks workspace with Databricks Apps enabled

## 1) Configure environment

Copy `.env.example` to `.env` and set your Lakebase connection string:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>?sslmode=require
```

## 2) Install dependencies (uv)

```bash
uv sync
```

## 3) Create schema and seed sample data

```bash
uv run --env-file .env -- python -m scripts.init_db
uv run --env-file .env -- python -m scripts.seed_db
```

Sample data includes:

- 3 support tickets
- 2 messages per ticket
- statuses across at least two values (`open`, `in_progress`, `resolved`)

## 4) Run locally

```bash
uv run --env-file .env -- streamlit run support_ticket_app/app.py
```

## 5) Deploy with Databricks Apps

1. Commit/push this project to your repo.
2. In Databricks, create a new App from this repository.
3. Ensure `app.yaml` is detected.
4. Create a secret named `support-ticket-database-url` containing your `DATABASE_URL` value.
5. Deploy the app.

Example Databricks CLI flow (adjust paths/names to your workspace):

```bash
databricks apps create support-ticket-app --description "Support ticket app"
databricks apps deploy support-ticket-app --source .
```

## 6) Test checklist after deployment

- Existing tickets load from Lakebase on app start.
- Creating a new ticket succeeds.
- Adding a message to an existing ticket succeeds.
- Updating ticket status succeeds.
- Refreshing the app preserves all changes.

## Project layout

```text
.
├── app.yaml
├── pyproject.toml
├── README.md
├── sql
│   ├── 001_create_schema.sql
│   └── 002_seed_data.sql
├── scripts
│   ├── init_db.py
│   └── seed_db.py
└── support_ticket_app
    ├── app.py
    ├── db.py
    └── __init__.py
```

## Notes

- The app uses parameterized SQL queries for inserts/updates.
- `ticket_messages.ticket_id` is enforced via a foreign key.
- `ON DELETE CASCADE` is enabled for message cleanup if tickets are deleted in future enhancements.
