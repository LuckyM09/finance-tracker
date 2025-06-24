import streamlit as st
import psycopg2
import pandas as pd
import altair as alt
import os
from ml_predictor import predict_expenses 
from datetime import date
from dotenv import load_dotenv
load_dotenv()


def apply_theme(theme_mode):
    if theme_mode == "dark":
        st.markdown("""
            <style>
                body, .stApp {
                    background-color: #0f1117;
                    color: white;
                }
                .stTextInput > div > input,
                .stNumberInput > div > input,
                .stSelectbox > div > div {
                    background-color: #222;
                    color: white;
                    border-radius: 10px;
                }
                .stDataFrame, .stTable {
                    background-color: #1e1e1e;
                    color: white;
                }
                .stButton > button {
                    background-color: #ffffff20;
                    color: white;
                    border: 1px solid white;
                }
                .stButton > button:hover {
                    background-color: #ffc107;
                    color: black;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                body, .stApp {
                    background-color: #ffffff;
                    color: black;
                }
                .stTextInput > div > input,
                .stNumberInput > div > input,
                .stSelectbox > div > div {
                    background-color: #f3f3f3;
                    color: black;
                    border-radius: 10px;
                }
                .stDataFrame, .stTable {
                    background-color: #ffffff;
                    color: black;
                }
                .stButton > button {
                    background-color: #eeeeee;
                    color: black;
                    border: 1px solid #ccc;
                }
                .stButton > button:hover {
                    background-color: #ffc107;
                    color: white;
                }
            </style>
        """, unsafe_allow_html=True)

def main():
    # 🔒 Block access if not logged in
    st.markdown("""
    <style>
    .dashboard-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
    }

    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stSelectbox > div > div {
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



    # ✅ Responsive CSS for mobile optimization
    st.markdown("""
    <style>
    @media screen and (max-width: 768px) {
        .dashboard-box {
            padding: 1rem !important;
            font-size: 0.9rem;
        }

        .stButton > button {
            width: 100% !important;
            padding: 0.8rem 1rem !important;
            font-size: 1rem !important;
        }

        .stTextInput > div > input,
        .stNumberInput > div > input,
        .stSelectbox > div > div {
            font-size: 1rem !important;
            width: 100% !important;
        }

        .stDataFrame {
            font-size: 0.85rem !important;
        }

        .block-container {
            padding: 1rem !important;
        }

        h2, h3, h4 {
            font-size: 1.2rem !important;
        }

        .css-1v0mbdj, .css-12oz5g7 {  /* Remove chart overflow if any */
            overflow-x: auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


    


    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Please log in to access the dashboard.")
        st.stop()

    apply_theme(st.session_state.get("theme_mode", "dark"))

    # 🧠 Get user info
    user_id = st.session_state.user_id
    name = st.session_state.name

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"<h2 style='color: white;'>Hi {name} 👋</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout",key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully.")
            st.rerun()

    st.markdown("<h3 style='color: #ffc107;'>Track Your Daily Expenses</h3>", unsafe_allow_html=True)

    # 📥 Input fields
    with st.form("expense_form"):
        amount = st.number_input("Expense Amount", min_value=1.0, format="%.2f")
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Entertainment", "Other"])
        note = st.text_input("Note (optional)")
        exp_date = st.date_input("Date", value=date.today())
        submit = st.form_submit_button("Add Expense")

    # 💾 Save to PostgreSQL
    if submit:
        try:
            conn = psycopg2.connect(
              host=os.getenv("DB_HOST"),
              database=os.getenv("DB_NAME"),
              user=os.getenv("DB_USER"),
              password=os.getenv("DB_PASSWORD"),
              port=os.getenv("DB_PORT")
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO expenses (user_id, amount, category, note, expense_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, amount, category, note, exp_date))
            conn.commit()
            st.success("Expense added successfully!")

            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Error saving expense: {e}")

    st.markdown("---")

    # 📊 Show Table of Expenses
    try:
        conn = psycopg2.connect(
            host="db.khtqiehroobqiggodxpr.supabase.co",
            database="postgres",
            user="postgres",
            password="Lucky@1908",
            port=5432
        )
        df = pd.read_sql("SELECT amount, category, note, expense_date FROM expenses WHERE user_id = %s ORDER BY expense_date DESC", conn, params=(user_id,))
        conn.close()

        if not df.empty:
            st.markdown("<h4 style='color: #ffc107;'>Your Expense History</h4>", unsafe_allow_html=True)
            with st.container():
                st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("No expenses added yet.")

    except Exception as e:
        st.error(f"Error loading expense data: {e}")

    # 🔮 Prediction section
    if st.button("Predict Next 7 Days Expense",key="prediction_btn"):
        prediction_df, error = predict_expenses(user_id)

        if error:
            st.warning(error)
        elif prediction_df is not None:
            st.subheader("📅 Predicted Expenses (Next 7 Days)")
            with st.container():
                st.dataframe(prediction_df)

            st.subheader("📊 Category-wise Expense Prediction")
            chart = alt.Chart(prediction_df).mark_bar().encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('predicted_amount:Q', title='Predicted Amount'),
                color='category:N',
                tooltip=['date', 'category', 'predicted_amount']
            ).properties(width=700)

            with st.container():

                st.altair_chart(chart, use_container_width=True)



