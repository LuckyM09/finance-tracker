import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import psycopg2
import os
from datetime import timedelta, date
from dotenv import load_dotenv
load_dotenv()


def predict_expenses(user_id):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute("SELECT amount, category, expense_date FROM expenses WHERE user_id = %s", (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if len(rows) < 7:
            return None, "Not enough data to make predictions."

        df = pd.DataFrame(rows, columns=['amount', 'category', 'expense_date'])
        df['expense_date'] = pd.to_datetime(df['expense_date'], errors='coerce')
        df = df.dropna(subset=['expense_date'])
        df['day'] = df['expense_date'].dt.dayofweek
        df['month'] = df['expense_date'].dt.month

        # One-hot encode category
        df = pd.get_dummies(df, columns=['category'])

        feature_cols = [col for col in df.columns if col not in ['amount', 'expense_date']]
        X = df[feature_cols]
        y = df['amount']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Unique categories from training
        category_cols = [col for col in X.columns if col.startswith('category_')]
        categories = [col.replace('category_', '') for col in category_cols]

        future_predictions = []

        future_dates = [date.today() + timedelta(days=i) for i in range(1, 8)]

        for future_date in future_dates:
            for cat in categories:
                row = {
                    'day': future_date.weekday(),
                    'month': future_date.month
                }
                for c in category_cols:
                    row[c] = 1 if c == f'category_{cat}' else 0
                future_df = pd.DataFrame([row])
                pred = model.predict(future_df)[0]
                future_predictions.append({
                    'date': future_date,
                    'category': cat,
                    'predicted_amount': round(pred, 2)
                })

        prediction_df = pd.DataFrame(future_predictions)
        return prediction_df, None

    except Exception as e:
        return None, f"Prediction failed: {e}"

