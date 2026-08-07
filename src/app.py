"""Support Ticket App - Main Streamlit Application.

A simple internal support system built with Streamlit and Lakebase.
"""
import streamlit as st
from datetime import datetime
from psycopg import Error as PsycopgError

import db

# Page configuration
st.set_page_config(
    page_title="Support Ticket System",
    page_icon="🎫",
    layout="wide"
)

# Initialize session state
if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None


def format_datetime(dt):
    """Format datetime for display."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M")


def show_error(message: str):
    """Display error message."""
    st.error(f"❌ {message}")


def show_success(message: str):
    """Display success message."""
    st.success(f"✅ {message}")


def main():
    """Main application entry point."""
    st.title("🎫 Support Ticket System")
    st.markdown("---")
    
    # Show statistics
    try:
        stats = db.get_ticket_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", sum(stats.values()))
        with col2:
            st.metric("Open", stats["open"])
        with col3:
            st.metric("In Progress", stats["in_progress"])
        with col4:
            st.metric("Resolved", stats["resolved"])
        st.markdown("---")
    except Exception as e:
        show_error(f"Could not load statistics: {e}")
    
    # Create two columns for layout
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("📋 Tickets")
        
        # Filter by status
        status_filter = st.selectbox(
            "Filter by status",
            ["all", "open", "in_progress", "resolved"]
        )
        
        # Add new ticket button
        if st.button("➕ Create New Ticket", use_container_width=True):
            st.session_state.show_create_form = True
        
        st.markdown("---")
        
        # Show create ticket form
        if st.session_state.get("show_create_form", False):
            with st.form("create_ticket_form"):
                st.write("**Create New Ticket**")
                new_title = st.text_input("Title")
                new_status = st.selectbox("Status", db.VALID_STATUSES)
                new_created_by = st.text_input("Your Email")
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("Create", use_container_width=True)
                with col_cancel:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if submitted:
                    try:
                        ticket_id = db.create_ticket(new_title, new_status, new_created_by)
                        show_success(f"Ticket #{ticket_id} created successfully!")
                        st.session_state.show_create_form = False
                        st.session_state.selected_ticket_id = ticket_id
                        st.rerun()
                    except Exception as e:
                        show_error(str(e))
                
                if cancelled:
                    st.session_state.show_create_form = False
                    st.rerun()
            
            st.markdown("---")
        
        # List tickets
        try:
            if status_filter == "all":
                tickets = db.fetch_all_tickets()
            else:
                tickets = db.fetch_tickets_by_status(status_filter)
            
            if not tickets:
                st.info("No tickets found")
            else:
                for ticket in tickets:
                    status_emoji = {
                        "open": "🔵",
                        "in_progress": "🟡",
                        "resolved": "🟢"
                    }[ticket["status"]]
                    
                    ticket_selected = st.session_state.selected_ticket_id == ticket["ticket_id"]
                    
                    if st.button(
                        f"{status_emoji} #{ticket['ticket_id']}: {ticket['title'][:40]}...",
                        key=f"ticket_{ticket['ticket_id']}",
                        use_container_width=True,
                        type="primary" if ticket_selected else "secondary"
                    ):
                        st.session_state.selected_ticket_id = ticket["ticket_id"]
                        st.rerun()
        
        except Exception as e:
            show_error(f"Could not load tickets: {e}")
    
    with col_right:
        if st.session_state.selected_ticket_id:
            show_ticket_detail(st.session_state.selected_ticket_id)
        else:
            st.info("👈 Select a ticket from the list to view details")


def show_ticket_detail(ticket_id: int):
    """Display detailed view of a selected ticket."""
    try:
        # Fetch ticket details
        if status_filter := st.session_state.get("status_filter", "all") == "all":
            tickets = db.fetch_all_tickets()
        else:
            tickets = db.fetch_tickets_by_status(status_filter)
        
        ticket = next((t for t in tickets if t["ticket_id"] == ticket_id), None)
        
        if not ticket:
            show_error("Ticket not found")
            return
        
        # Display ticket header
        st.subheader(f"Ticket #{ticket['ticket_id']}")
        st.write(f"**Title:** {ticket['title']}")
        st.write(f"**Status:** {ticket['status']}")
        st.write(f"**Created by:** {ticket['created_by']}")
        st.write(f"**Created at:** {format_datetime(ticket['created_at'])}")
        
        st.markdown("---")
        
        # Display messages
        st.write("**💬 Messages**")
        
        messages = db.fetch_ticket_messages(ticket_id)
        
        if not messages:
            st.info("No messages yet")
        else:
            for msg in messages:
                with st.container():
                    st.write(f"**{msg['author']}** · {format_datetime(msg['created_at'])}")
                    st.write(msg['message_text'])
                    st.markdown("---")
        
        # Add message form
        with st.form(f"add_message_form_{ticket_id}"):
            st.write("**Add a message**")
            message_text = st.text_area("Message", height=100)
            author_name = st.text_input("Your Email")
            
            if st.form_submit_button("Send Message"):
                try:
                    db.add_message(ticket_id, message_text, author_name)
                    show_success("Message added!")
                    st.rerun()
                except Exception as e:
                    show_error(str(e))
    
    except Exception as e:
        show_error(f"Error loading ticket details: {e}")


if __name__ == "__main__":
    main()
