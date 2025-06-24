import streamlit as st
import psycopg2
import os
import streamlit_authenticator as stauth
import datetime
from dotenv import load_dotenv
load_dotenv()

cookies = EncryptedCookieManager(
    prefix="finance_",  # optional namespace
    password=os.getenv("COOKIE_SECRET", "my_secret")  # use env var in production
)
cookies.load()


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


    
    if cookies.get("user_id") and cookies.get("username"):
        st.session_state.logged_in = True
        st.session_state.user_id = int(cookies["user_id"])
        st.session_state.username = cookies["username"]
        st.session_state.name = cookies["full_name"]
        st.session_state.page = 'dashboard'
        st.experimental_rerun()
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
                    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
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
                        
                        if remember:
                            cookies["user_id"] = str(user[0])
                            cookies["username"] = username
                            cookies["full_name"] = user[1]
                            cookies.save()

                        st.rerun()
                    else:
                        st.error("Invalid credentials")

                except Exception as e:
                    st.error(f"Error: {e}")

            st.markdown("<p style='text-align: right;'>Forgot Password?</p>", unsafe_allow_html=True)

            if st.button("Sign up"):
                st.session_state.page = 'signup'



