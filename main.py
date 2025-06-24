import streamlit as st
from auth.login import login_page
from auth.signup import signup_page
from dashboard import main as dashboard_main
from analytics import monthly_analytics

st.set_page_config(page_title="Finance Tracker", layout="wide")

# Theme toggle
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# Default to login page
if "page" not in st.session_state:
    st.session_state.page = "login"

# Auth handling
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()

# 🔒 After login, show sidebar navigation
if st.session_state.get("logged_in", False):
    # Sidebar navigation that remembers selection
    selected = st.sidebar.radio("Navigate", ["Dashboard", "Monthly Analytics"], key="nav_radio")

    # Theme toggle button
    toggle = st.sidebar.toggle("🌗 Dark Mode", value=st.session_state.theme_mode == "dark")
    st.session_state.theme_mode = "dark" if toggle else "light"

    # Render selected page
    if selected == "Dashboard":
        dashboard_main()
    elif selected == "Monthly Analytics":
        monthly_analytics()



