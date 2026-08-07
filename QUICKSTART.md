# 🚀 Quick Start Guide

## Get the App Running in 5 Minutes

### Step 1: Install Dependencies

```bash
cd support-ticket-app
uv sync
```

### Step 2: Set Up Your Database Connection

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Lakebase connection string:

```env
DATABASE_URL=postgresql://your_user@your_host.database.us-east-2.cloud.databricks.com/your_database?sslmode=require
```

**Get your connection string from:**
* Lakebase UI → Your Database → Connection Details
* Format: `postgresql://user@host/database?sslmode=require`

### Step 3: Initialize the Database

Run the initialization script to create tables and add sample data:

```bash
uv run python sql/init_database.py
```

This will:
* Create the `tickets` and `ticket_messages` tables
* Insert 4 sample tickets
* Add 2+ messages per ticket

### Step 4: Run the App

```bash
uv run --env-file .env -- streamlit run src/app.py
```

The app opens at `http://localhost:8501` 🎉

---

## What You'll See

✅ **Dashboard**: Ticket statistics (Total, Open, In Progress, Resolved)  
✅ **Ticket List**: All tickets with status indicators  
✅ **Filters**: Filter by status (all, open, in_progress, resolved)  
✅ **Ticket Details**: View full ticket with message thread  
✅ **Create Ticket**: Add new support tickets  
✅ **Add Messages**: Reply to tickets  

---

## Sample Tickets Included

1. **Login issues on mobile app** (Open)
2. **Dashboard not loading data** (In Progress)
3. **Export feature throwing errors** (Resolved)
4. **Slow query performance** (Open)

Each ticket has realistic conversation threads between users and support team.

---

## Next Steps

### Deploy to Databricks Apps

1. **Set up the secret:**
   ```bash
   uv run python src/setup_secrets.py
   ```
   Enter your DATABASE_URL when prompted.

2. **Deploy:**
   ```bash
   databricks apps create support-ticket-app --description "Support ticket system"
   databricks apps deploy support-ticket-app --source-path .
   ```

### Or Deploy via UI

1. Go to **Apps** in Databricks workspace
2. Click **Create App**
3. Connect to your repository
4. Select `app.yaml`
5. Click **Deploy**

---

## Troubleshooting

**"DATABASE_URL is not set"**
* Check your `.env` file exists in the project root
* Verify the variable is named exactly `DATABASE_URL`

**"Could not connect to database"**
* Test your connection string with `psql`
* Ensure `?sslmode=require` is included
* Check your Lakebase database is running

**"Relation does not exist"**
* Run the initialization script: `uv run python sql/init_database.py`
* This creates the required tables

---

## File Structure Overview

```
support-ticket-app/
├── .env                    # Your database connection (git-ignored)
├── .env.example            # Template for .env
├── app.yaml                # Databricks App config
├── pyproject.toml          # Python dependencies
├── README.md               # Full documentation
├── QUICKSTART.md           # This file
├── sql/
│   ├── schema.sql          # Database schema
│   ├── sample_data.sql     # Sample tickets
│   └── init_database.py    # Setup script
└── src/
    ├── app.py              # Main Streamlit app
    ├── db.py               # Database operations
    └── setup_secrets.py    # Databricks secret setup
```

---

## 📚 Need More Help?

See [README.md](README.md) for:
* Complete feature list
* Detailed database schema
* Deployment options
* Advanced configuration
