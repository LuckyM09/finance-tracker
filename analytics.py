import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


def apply_theme(theme_mode):
    

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


def monthly_analytics():
    apply_theme(st.session_state.get("theme_mode", "dark"))


    st.markdown("<h2 style='color: #ffc107;'>📈 Monthly Analytics</h2>", unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    month = st.selectbox("Select Month", options=pd.date_range('2024-01-01', datetime.today(), freq='MS').strftime("%B %Y"))

    # Convert selected month to date range
    selected_date = datetime.strptime(month, "%B %Y")
    start_date = selected_date.replace(day=1)
    end_date = (start_date + pd.DateOffset(months=1)).replace(day=1)

    # Fetch data
    try:
        conn =  psycopg2.connect(os.getenv("DATABASE_URL"))
        query = """
            SELECT amount, category, expense_date FROM expenses 
            WHERE user_id = %s AND expense_date >= %s AND expense_date < %s
        """
        df = pd.read_sql(query, conn, params=(user_id, start_date, end_date))
        conn.close()

        if df.empty:
            st.info("No expenses found for the selected month.")
            return

        df['expense_date'] = pd.to_datetime(df['expense_date'])

        # 1. Income vs Expense chart (assuming income is a fixed value, or later input field)
        monthly_income = st.number_input("Enter your monthly income (₹)", min_value=0.0, value=20000.0, step=1000.0)

        total_expense = df['amount'].sum()
        savings = monthly_income - total_expense
        burn_rate = (total_expense / monthly_income) * 100 if monthly_income else 0

        st.markdown(f"💰 **Total Expense:** ₹{total_expense:.2f} | 💾 **Savings:** ₹{savings:.2f} | 🔥 **Burn Rate:** {burn_rate:.1f}%")

        # Budget status
        if total_expense > monthly_income:
            st.error("⚠️ You overspent this month.")
        else:
            st.success("✅ You stayed within budget.")

        # 2. Line chart: Daily expense trend
        daily_trend = df.groupby('expense_date')['amount'].sum().reset_index()
        line_fig = px.line(daily_trend, x='expense_date', y='amount', title='Daily Expense Trend')
        with st.container():
            st.plotly_chart(line_fig, use_container_width=True)

        # 3. Pie chart: Category-wise breakdown
        category_break = df.groupby('category')['amount'].sum().reset_index()
        pie_fig = px.pie(category_break, names='category', values='amount', title='Category-wise Expense Breakdown')
        with st.container():
            st.plotly_chart(pie_fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading analytics: {e}")



            # 🚀 Button to toggle comparison


    if st.button("🔁 Show Month-over-Month Comparison", key="compare_btn"):

                # Previous month date range
        prev_start = (start_date - pd.DateOffset(months=1)).replace(day=1)
        prev_end = start_date

        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            query = """
                SELECT amount, category, expense_date FROM expenses 
                WHERE user_id = %s AND expense_date >= %s AND expense_date < %s
            """
            df_prev = pd.read_sql(query, conn, params=(user_id, prev_start, prev_end))
            conn.close()

                    # Current month category totals
            current_month_cat = df.groupby('category')['amount'].sum().reset_index()
            current_month_cat.rename(columns={'amount': 'current_month'}, inplace=True)

                        # Previous month category totals
            prev_month_cat = df_prev.groupby('category')['amount'].sum().reset_index()
            prev_month_cat.rename(columns={'amount': 'previous_month'}, inplace=True)

                        # Merge
            comparison_df = pd.merge(current_month_cat, prev_month_cat, on='category', how='outer').fillna(0)

                    # Melt for Plotly
            melted = comparison_df.melt(id_vars='category', value_vars=['current_month', 'previous_month'],
                                                    var_name='Month', value_name='Amount')

                    
            fig = px.bar(
                melted,
                x="category",
                y="Amount",
                color="Month",
                barmode="group",
                title="This Month vs. Last Month by Category"
            )
            with st.container():
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
          st.error(f"Error loading comparison chart: {e}")
    
