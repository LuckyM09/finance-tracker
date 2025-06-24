import streamlit as st
import psycopg2
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("SELECT id, full_name FROM users WHERE username=%s AND password=%s", (username, password))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = username
                st.session_state.name = user[1]
                st.session_state.page = "dashboard"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

        except Exception as e:
            st.error(f"Login failed: {e}")

    if st.button("Sign Up"):
        st.session_state.page = "signup"
        st.rerun()








