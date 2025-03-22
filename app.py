from dotenv import load_dotenv
load_dotenv()  # Load environment variables before using them

import streamlit as st
from components.auth_ui import show_auth_ui
from components.inventory_form import show_inventory_form
from components.inventory_view import show_inventory_view

def main():
    st.set_page_config(
        page_title="Inventory Management System",
        page_icon="📦",
        layout="wide"
    )

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_token' not in st.session_state:
        st.session_state.user_token = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

    # Show authentication UI if not authenticated
    if not st.session_state.authenticated:
        show_auth_ui()
        return

    # Show user info in sidebar
    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_token = None
        st.session_state.user_email = None
        st.rerun()

    # Main application
    st.title("📦 Inventory Management System")
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Add/Edit Inventory", "View Inventory"])
    
    if page == "Add/Edit Inventory":
        show_inventory_form()
    else:
        show_inventory_view()

if __name__ == "__main__":
    main() 