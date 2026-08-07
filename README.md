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

## 3) Run locally

```bash
uv run --env-file .env -- streamlit run src/app.py
```

## 4) Set up Databricks secrets

Before deploying the app, create a secret to store your Lakebase connection URL:

```bash
# Install dev dependencies (includes databricks-sdk)
uv sync --dev

# Run the setup script
uv run python src/setup_secrets.py
```

This creates:
* Secret scope: `support-tickets`
* Secret key: `support-ticket-database-url`
* ACL: `users` group with READ permission

Alternatively, you can create the secret manually:
```bash
databricks secrets create-scope support-tickets
databricks secrets put-secret support-tickets support-ticket-database-url --string-value "<your-database-url>"
databricks secrets put-acl support-tickets users READ
```

## 5) Deploy with Databricks Apps

1. Commit/push this project to your repo.
2. In Databricks, create a new App from this repository.
3. Ensure `app.yaml` is detected.
4. Deploy the app (the secret will be automatically injected as the `DATABASE_URL` environment variable).

Example Databricks CLI flow:

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
├── .env.example
└── src
    ├── app.py
    ├── db.py
    └── setup_secrets.py
```

## Notes

- `ticket_messages.ticket_id` is enforced via a foreign key.
- `ON DELETE CASCADE` is enabled for message cleanup if tickets are deleted in future enhancements.
