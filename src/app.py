from __future__ import annotations

import streamlit as st
from psycopg import Error as PsycopgError
from datetime import datetime

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

st.set_page_config(
    page_title="Support Ticket Console", 
    page_icon="🎫", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
      
      :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --border: #e2e8f0;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
      }
      
      html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
      }
      
      .stApp {
        background: linear-gradient(180deg, #fafbfc 0%, #f8fafc 100%);
      }
      
      /* Header styling */
      h1 {
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
      }
      
      h2, h3, h4 {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
      }
      
      /* Enhanced metric cards */
      .metric-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
      }
      
      .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
      }
      
      .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
      }
      
      .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
      }
      
      /* Ticket card styling */
      .ticket-card {
        background: white;
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
      }
      
      .ticket-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-md);
        transform: translateX(4px);
      }
      
      .ticket-card.selected {
        border-color: var(--primary);
        background: linear-gradient(to right, #eef2ff, white);
        box-shadow: var(--shadow-md);
      }
      
      .ticket-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
      }
      
      .ticket-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
      }
      
      .ticket-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
      }
      
      .ticket-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
      }
      
      /* Status badges */
      .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      
      .status-open {
        background: #dbeafe;
        color: #1e40af;
      }
      
      .status-in_progress {
        background: #fef3c7;
        color: #92400e;
      }
      
      .status-resolved {
        background: #d1fae5;
        color: #065f46;
      }
      
      /* Priority badges */
      .priority-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      
      .priority-low {
        background: #f1f5f9;
        color: #475569;
      }
      
      .priority-medium {
        background: #fed7aa;
        color: #9a3412;
      }
      
      .priority-high {
        background: #fecaca;
        color: #991b1b;
      }
      
      /* Message styling */
      .message-container {
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
      }
      
      .message-author {
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 4px;
      }
      
      .message-time {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: 8px;
      }
      
      .message-text {
        color: var(--text-primary);
        line-height: 1.6;
      }
      
      /* Form styling */
      div[data-testid="stForm"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        box-shadow: var(--shadow-sm);
      }
      
      /* Button styling */
      .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
      }
      
      .stButton > button:hover {
        background: var(--primary-dark) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
      }
      
      /* Input styling */
      .stTextInput > div > div > input,
      .stTextArea > div > div > textarea,
      .stSelectbox > div > div > select {
        border-radius: 8px !important;
        border-color: var(--border) !important;
      }
      
      /* Empty state */
      .empty-state {
        text-align: center;
        padding: 48px 24px;
        color: var(--text-secondary);
      }
      
      .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 16px;
        opacity: 0.5;
      }
      
      /* Section headers */
      .section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--border);
      }
      
      .section-icon {
        font-size: 1.5rem;
      }
      
      /* Responsive design */
      @media (max-width: 768px) {
        .metric-card {
          padding: 16px;
        }
        
        .ticket-card {
          padding: 12px;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper functions for rendering UI components
def get_status_badge(status: str) -> str:
    """Generate HTML for a status badge."""
    status_class = f"status-{status.replace(' ', '_')}"
    status_display = status.replace('_', ' ').title()
    return f'<span class="status-badge {status_class}">{status_display}</span>'

def get_priority_badge(priority: str) -> str:
    """Generate HTML for a priority badge."""
    priority_class = f"priority-{priority}"
    return f'<span class="priority-badge {priority_class}">{priority.upper()}</span>'

def format_timestamp(timestamp) -> str:
    """Format timestamp in a user-friendly way."""
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(str(timestamp))
        except:
            return str(timestamp)
    else:
        dt = timestamp
    
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt
    
    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            mins = diff.seconds // 60
            return f"{mins} minute{'s' if mins != 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%b %d, %Y")

# Page header
st.markdown(
    """
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem;">🎫 Support Ticket Console</h1>
        <p style="color: var(--text-secondary); font-size: 1rem;">Powered by Databricks & Lakebase Postgres</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Filters section
filter_col1, filter_col2 = st.columns([3, 1])
with filter_col1:
    status_filter = st.selectbox(
        "🔍 Filter by status",
        ["all", *VALID_STATUSES],
        index=0,
        format_func=lambda x: "All Tickets" if x == "all" else x.replace('_', ' ').title()
    )
with filter_col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Fetch ticket counts
try:
    ticket_counts = fetch_ticket_counts()
except (RuntimeError, PsycopgError) as exc:
    st.error(f"⚠️ Could not load ticket statistics: {exc}")
    st.stop()

# Metrics cards
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>📬 Open</div>
            <div class='metric-value'>{ticket_counts['open']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>⏳ In Progress</div>
            <div class='metric-value'>{ticket_counts['in_progress']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_c:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>✅ Resolved</div>
            <div class='metric-value'>{ticket_counts['resolved']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# Initialize session state for selected ticket
if 'selected_ticket_id' not in st.session_state:
    st.session_state.selected_ticket_id = None

left, right = st.columns([1.1, 1.4])

with left:
    st.markdown(
        '<div class="section-header"><span class="section-icon">🎫</span><h3 style="margin:0;">Tickets</h3></div>',
        unsafe_allow_html=True
    )
    
    # Fetch tickets
    try:
        tickets = fetch_tickets(status_filter)
    except (RuntimeError, PsycopgError) as exc:
        st.error(f"⚠️ Failed to load tickets: {exc}")
        tickets = []

    if not tickets:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <p><strong>No tickets found</strong></p>
                <p style="font-size: 0.875rem;">Create a new ticket to get started</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        selected_ticket_id = None
    else:
        # Auto-select first ticket if none selected
        if st.session_state.selected_ticket_id is None:
            st.session_state.selected_ticket_id = tickets[0]["ticket_id"]
        
        # Render ticket list with clickable cards
        for idx, ticket in enumerate(tickets):
            is_selected = st.session_state.selected_ticket_id == ticket["ticket_id"]
            selected_class = "selected" if is_selected else ""
            
            # Create clickable ticket card using button
            col1, col2 = st.columns([20, 1])
            with col1:
                ticket_html = f"""
                <div class="ticket-card {selected_class}">
                    <div class="ticket-header">
                        <span class="ticket-id">#{ticket['ticket_id']}</span>
                    </div>
                    <div class="ticket-title">{ticket['title']}</div>
                    <div class="ticket-meta">
                        {get_status_badge(ticket['status'])}
                        {get_priority_badge(ticket['priority'])}
                    </div>
                </div>
                """
                st.markdown(ticket_html, unsafe_allow_html=True)
            
            with col2:
                # Small select button
                if not is_selected:
                    if st.button("▶️", key=f"select_{ticket['ticket_id']}", help="Select this ticket"):
                        st.session_state.selected_ticket_id = ticket["ticket_id"]
                        st.rerun()
                else:
                    st.markdown("<div style='font-size: 1.5rem; color: var(--primary);'>✅</div>", unsafe_allow_html=True)
        
        selected_ticket_id = st.session_state.selected_ticket_id

    # Create ticket form
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header"><span class="section-icon">➕</span><h3 style="margin:0;">Create New Ticket</h3></div>',
        unsafe_allow_html=True
    )
    
    with st.form("new_ticket_form", clear_on_submit=True):
        new_title = st.text_input("📝 Title", placeholder="Brief description of the issue")
        new_creator = st.text_input("👤 Your name", placeholder="Enter your name")
        
        col1, col2 = st.columns(2)
        with col1:
            new_status = st.selectbox(
                "📊 Status", 
                VALID_STATUSES, 
                index=0,
                format_func=lambda x: x.replace('_', ' ').title()
            )
        with col2:
            new_priority = st.selectbox(
                "⚠️ Priority", 
                VALID_PRIORITIES, 
                index=1,
                format_func=lambda x: x.title()
            )
        
        create_btn = st.form_submit_button("➕ Create Ticket", use_container_width=True)

        if create_btn:
            try:
                new_id = create_ticket(new_title, new_creator, new_status, new_priority)
                st.success(f"✅ Ticket #{new_id} created successfully!")
                st.session_state.selected_ticket_id = new_id
                st.rerun()
            except ValueError as exc:
                st.warning(f"⚠️ {exc}")
            except (RuntimeError, PsycopgError) as exc:
                st.error(f"❌ Ticket creation failed: {exc}")

with right:
    st.markdown(
        '<div class="section-header"><span class="section-icon">📋</span><h3 style="margin:0;">Ticket Details</h3></div>',
        unsafe_allow_html=True
    )

    if selected_ticket_id is None:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">👈</div>
                <p><strong>Select a ticket</strong></p>
                <p style="font-size: 0.875rem;">Choose a ticket from the list or create a new one</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        selected_ticket = next(
            ticket for ticket in tickets if ticket["ticket_id"] == selected_ticket_id
        )
        
        # Ticket header
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: var(--shadow-sm);">
                <div style="margin-bottom: 16px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.875rem; color: var(--text-muted);">#{selected_ticket["ticket_id"]}</span>
                    <h2 style="margin: 8px 0 16px 0;">{selected_ticket["title"]}</h2>
                    <div style="display: flex; gap: 8px; margin-bottom: 16px;">
                        {get_status_badge(selected_ticket["status"])}
                        {get_priority_badge(selected_ticket["priority"])}
                    </div>
                </div>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">
                    <strong>👤 {selected_ticket['created_by']}</strong> • {format_timestamp(selected_ticket['created_at'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Status update section
        st.markdown(
            '<div class="section-header"><span class="section-icon">🔄</span><h4 style="margin:0;">Update Status</h4></div>',
            unsafe_allow_html=True
        )
        
        status_col, update_col = st.columns([3, 1])
        with status_col:
            current_status = selected_ticket["status"]
            status_index = (
                VALID_STATUSES.index(current_status) if current_status in VALID_STATUSES else 0
            )
            updated_status = st.selectbox(
                "Change status",
                VALID_STATUSES,
                index=status_index,
                key="status_update_select",
                format_func=lambda x: x.replace('_', ' ').title(),
                label_visibility="collapsed"
            )
        with update_col:
            if st.button("💾 Save", use_container_width=True, key="save_status_btn"):
                try:
                    update_ticket_status(selected_ticket_id, updated_status)
                    st.success("✅ Status updated successfully!")
                    st.rerun()
                except ValueError as exc:
                    st.warning(f"⚠️ {exc}")
                except (RuntimeError, PsycopgError) as exc:
                    st.error(f"❌ Status update failed: {exc}")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Messages section
        st.markdown(
            '<div class="section-header"><span class="section-icon">💬</span><h4 style="margin:0;">Messages</h4></div>',
            unsafe_allow_html=True
        )
        
        try:
            messages = fetch_ticket_messages(selected_ticket_id)
        except (RuntimeError, PsycopgError) as exc:
            st.error(f"⚠️ Failed to load messages: {exc}")
            messages = []

        if messages:
            for msg in messages:
                st.markdown(
                    f"""
                    <div class="message-container">
                        <div class="message-author">👤 {msg['author']}</div>
                        <div class="message-time">{format_timestamp(msg['created_at'])}</div>
                        <div class="message-text">{msg['message_text']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="text-align: center; padding: 32px; color: var(--text-secondary);">
                    <div style="font-size: 2rem; margin-bottom: 8px;">💭</div>
                    <p>No messages yet. Be the first to comment!</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Add message form
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("add_message_form", clear_on_submit=True):
            st.markdown(
                '<div style="margin-bottom: 16px;"><strong>✏️ Add a Message</strong></div>',
                unsafe_allow_html=True
            )
            message_author = st.text_input("👤 Your name", placeholder="Enter your name")
            message_text = st.text_area(
                "💬 Message", 
                placeholder="Type your message here...",
                height=100
            )
            add_message_btn = st.form_submit_button("📤 Post Message", use_container_width=True)

            if add_message_btn:
                try:
                    add_ticket_message(selected_ticket_id, message_text, message_author)
                    st.success("✅ Message posted successfully!")
                    st.rerun()
                except ValueError as exc:
                    st.warning(f"⚠️ {exc}")
                except (RuntimeError, PsycopgError) as exc:
                    st.error(f"❌ Failed to add message: {exc}")
