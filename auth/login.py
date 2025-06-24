import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def login_page():
    
     # Inject CSS
    st.markdown("""
    <style>
    body {
        background-color: #0e0e10;
    }

    .glass-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
    }

    .stTextInput > div > input,
    .stPasswordInput > div > input {
        background-color: #ffffff10;
        color: white;
        border-radius: 10px;
    }

    .stButton > button {
        background-color: #ffffff20;
        color: white;
        border-radius: 10px;
        border: 1px solid white;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #ffc107;
        color: black;
    }

    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Welcome Back!</h2>", unsafe_allow_html=True)

    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("### Log in", unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", placeholder="Enter password", type="password")
            remember = st.checkbox("Remember Me")

            if st.button("Log in"):
                try:
                    conn = psycopg2.connect(
                      host=os.getenv("DB_HOST"),
                      database=os.getenv("DB_NAME"),
                      user=os.getenv("DB_USER"),
                      password=os.getenv("DB_PASSWORD"),
                      port=os.getenv("DB_PORT")
                    )
                    cur = conn.cursor()
                    cur.execute("SELECT id, full_name FROM users WHERE username=%s AND password=%s", (username, password))
                    user = cur.fetchone()

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = username
                        st.session_state.name = user[1]
                        st.session_state.page = 'dashboard'
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

                except Exception as e:
                    st.error(f"Error: {e}")

            st.markdown("<p style='text-align: right;'>Forgot Password?</p>", unsafe_allow_html=True)

            if st.button("Sign up"):
                st.session_state.page = 'signup'

