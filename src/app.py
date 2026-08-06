from __future__ import annotations

import streamlit as st
from psycopg import Error as PsycopgError

from db import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    add_ticket_message,
    create_ticket,
    fetch_ticket_counts,
    fetch_ticket_messages,
    fetch_tickets,
    update_ticket_status,
)

st.set_page_config(page_title="Support Ticket Console", page_icon=":ticket:", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
      :root {
        --bg-a: #f3efe7;
        --bg-b: #d8e6e4;
        --ink: #14213d;
        --ink-soft: #37516d;
        --accent: #ef476f;
        --accent-2: #06d6a0;
        --card: #ffffffdc;
      }
      html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--ink);
      }
      .stApp {
        background: radial-gradient(circle at 10% 20%, var(--bg-b), transparent 50%),
                    radial-gradient(circle at 90% 10%, #ffe1b7, transparent 35%),
                    linear-gradient(145deg, var(--bg-a), #f8fafc);
      }
      .metric-card {
        border: 1px solid #d9e3ea;
        border-radius: 14px;
        padding: 12px 14px;
        background: var(--card);
        box-shadow: 0 8px 24px rgba(20, 33, 61, 0.08);
      }
      .ticket-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-family: 'IBM Plex Mono', monospace;
        background: #eef2f7;
        color: var(--ink-soft);
      }
      .stButton > button {
        border-radius: 999px;
        border: 0;
        background: linear-gradient(90deg, var(--accent), #f78c6b);
        color: white;
        font-weight: 600;
      }
      div[data-testid="stForm"] {
        border: 1px solid #d7e0e7;
        border-radius: 16px;
        padding: 14px;
        background: var(--card);
      }
      @media (max-width: 900px) {
        .stApp {
          background: linear-gradient(165deg, var(--bg-a), #f8fafc);
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Support Ticket Console")
st.caption("Databricks App backed by Lakebase")

status_filter = st.selectbox(
    "Filter tickets by status",
    ["all", *VALID_STATUSES],
    index=0,
)

try:
    ticket_counts = fetch_ticket_counts()
except (RuntimeError, PsycopgError) as exc:
    st.error(f"Could not load ticket statistics: {exc}")
    st.stop()

col_a, col_b, col_c = st.columns(3)
col_a.markdown(
    f"<div class='metric-card'><b>Open</b><br>{ticket_counts['open']}</div>", unsafe_allow_html=True
)
col_b.markdown(
    f"<div class='metric-card'><b>In Progress</b><br>{ticket_counts['in_progress']}</div>",
    unsafe_allow_html=True,
)
col_c.markdown(
    f"<div class='metric-card'><b>Resolved</b><br>{ticket_counts['resolved']}</div>",
    unsafe_allow_html=True,
)

st.divider()

left, right = st.columns([1.1, 1.4])

with left:
    st.subheader("Tickets")
    try:
        tickets = fetch_tickets(status_filter)
    except (RuntimeError, PsycopgError) as exc:
        st.error(f"Failed to load tickets: {exc}")
        tickets = []

    if not tickets:
        st.info("No tickets found for this filter.")
        selected_ticket_id = None
    else:
        option_lookup = {
            f"#{ticket['ticket_id']} - {ticket['title']} [{ticket['status']}]": ticket["ticket_id"]
            for ticket in tickets
        }
        selected_ticket_label = st.radio(
            "Select a ticket",
            list(option_lookup.keys()),
            index=0,
        )
        selected_ticket_id = option_lookup[selected_ticket_label]

    with st.form("new_ticket_form", clear_on_submit=True):
        st.markdown("### Create New Ticket")
        new_title = st.text_input("Title")
        new_creator = st.text_input("Created by")
        new_status = st.selectbox("Initial status", VALID_STATUSES, index=0)
        new_priority = st.selectbox("Priority", VALID_PRIORITIES, index=1)
        create_btn = st.form_submit_button("Create ticket")

        if create_btn:
            try:
                new_id = create_ticket(new_title, new_creator, new_status, new_priority)
                st.success(f"Ticket #{new_id} created.")
                st.rerun()
            except ValueError as exc:
                st.warning(str(exc))
            except (RuntimeError, PsycopgError) as exc:
                st.error(f"Ticket creation failed: {exc}")

with right:
    st.subheader("Ticket Details")

    if selected_ticket_id is None:
        st.info("Create a ticket to get started.")
    else:
        selected_ticket = next(
            ticket for ticket in tickets if ticket["ticket_id"] == selected_ticket_id
        )
        st.markdown(
            f"""
            <div>
              <h4 style='margin-bottom:4px'>#{selected_ticket["ticket_id"]} {selected_ticket["title"]}</h4>
              <span class='ticket-chip'>status: {selected_ticket["status"]}</span>
              <span class='ticket-chip'>priority: {selected_ticket["priority"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"Created by {selected_ticket['created_by']} at {selected_ticket['created_at']}")

        st.markdown("#### Update Status")
        status_col, update_col = st.columns([2, 1])
        with status_col:
            current_status = selected_ticket["status"]
            status_index = (
                VALID_STATUSES.index(current_status) if current_status in VALID_STATUSES else 0
            )
            updated_status = st.selectbox(
                "New status",
                VALID_STATUSES,
                index=status_index,
                key="status_update_select",
            )
        with update_col:
            if st.button("Save status"):
                try:
                    update_ticket_status(selected_ticket_id, updated_status)
                    st.success("Status updated.")
                    st.rerun()
                except ValueError as exc:
                    st.warning(str(exc))
                except (RuntimeError, PsycopgError) as exc:
                    st.error(f"Status update failed: {exc}")

        st.markdown("#### Messages")
        try:
            messages = fetch_ticket_messages(selected_ticket_id)
        except (RuntimeError, PsycopgError) as exc:
            st.error(f"Failed to load messages: {exc}")
            messages = []

        if messages:
            for msg in messages:
                with st.chat_message("assistant"):
                    st.markdown(msg["message_text"])
                    st.caption(f"{msg['author']} - {msg['created_at']}")
        else:
            st.info("No messages yet for this ticket.")

        with st.form("add_message_form", clear_on_submit=True):
            st.markdown("### Add Message")
            message_author = st.text_input("Author")
            message_text = st.text_area("Message")
            add_message_btn = st.form_submit_button("Post message")

            if add_message_btn:
                try:
                    add_ticket_message(selected_ticket_id, message_text, message_author)
                    st.success("Message added.")
                    st.rerun()
                except ValueError as exc:
                    st.warning(str(exc))
                except (RuntimeError, PsycopgError) as exc:
                    st.error(f"Failed to add message: {exc}")
