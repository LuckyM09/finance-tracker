import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def signup_page():
    # Inject the same CSS as login page
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

    st.markdown("<h2 style='text-align: center; color: white;'>Welcome!</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("<div class='glass-box'>", unsafe_allow_html=True)

            name = st.text_input("Full Name", placeholder="Enter your name")
            email = st.text_input("Email Address", placeholder="Enter your email")
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input("Password", placeholder="Create a password", type="password")
            confirm_password = st.text_input("Confirm Password", placeholder="Re-enter password", type="password")

            if st.button("Create Account"):
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif name and email and username and password:
                    try:
                        conn =  psycopg2.connect(os.getenv("DATABASE_URL"))
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                        if cur.fetchone():
                            st.warning("Username already exists")
                        else:
                            cur.execute(
                                "INSERT INTO users (full_name, email, username, password) VALUES (%s, %s, %s, %s)",
                                (name, email, username, password)
                            )
                            conn.commit()
                            st.success("Account created successfully!")
                        cur.close()
                        conn.close()
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    st.warning("Please fill all fields")

            if st.button("Log in"):
                st.session_state.page = 'login'

            st.markdown("</div>", unsafe_allow_html=True)

