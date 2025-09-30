# generate_customer_data.py
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# --- Configuration ---
NUM_RECORDS = 200
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime.now()

# --- Sample Data Lists ---
CUSTOMERS = [
    'Alpha Corp', 'Beta Industries', 'Gamma Solutions', 'Delta Tech', 'Epsilon Global',
    'Zeta Services', 'Omega Holdings', 'Theta Digital', 'Iota Innovations', 'Kappa Logistics',
    'Meridian Inc.', 'Nexus Enterprises', 'Orion Group', 'Pinnacle Corp', 'Quantum Ltd.'
]

# --- Data Generation Logic ---
data = []
for i, customer_name in enumerate(random.sample(CUSTOMERS, len(CUSTOMERS))):
    # Base metrics
    purchase_frequency = random.randint(1, 20) # purchases in the last year
    last_purchase_days_ago = random.randint(1, 365)
    last_purchase_date = END_DATE - timedelta(days=last_purchase_days_ago)
    avg_order_value = round(random.uniform(50, 1000), 2)
    
    # Engagement and support metrics
    support_tickets = random.randint(0, 5)
    engagement_score = random.randint(20, 99) # e.g., email opens, web visits
    
    # --- AI Simulation ---
    # 1. Health Score Calculation (simulated)
    # Higher score is better. Penalize for old purchases and high support tickets.
    recency_score = max(0, 100 - last_purchase_days_ago / 3.65)
    frequency_score = min(100, purchase_frequency * 10)
    support_score = max(0, 100 - support_tickets * 20)
    health_score = int(0.5 * recency_score + 0.3 * frequency_score + 0.2 * support_score)
    
    # 2. Churn Risk Segmentation (simulated)
    if health_score < 45:
        churn_risk = 'High'
    elif 45 <= health_score < 75:
        churn_risk = 'Medium'
    else:
        churn_risk = 'Low'

    # 3. Predicted LTV (simulated)
    predicted_ltv = avg_order_value * purchase_frequency * random.uniform(1.5, 3.0)

    # 4. Sentiment Score (simulated for trendline)
    # Generate a time series of sentiment scores for the last 12 months
    sentiment_history = [max(0.1, min(1.0, np.random.normal(loc=health_score/100, scale=0.15))) for _ in range(12)]
    
    data.append([
        f"CUST-{101 + i}",
        customer_name,
        last_purchase_date.strftime("%Y-%m-%d"),
        purchase_frequency,
        avg_order_value,
        support_tickets,
        engagement_score,
        health_score,
        churn_risk,
        round(predicted_ltv, 2),
        sentiment_history
    ])

# --- Create DataFrame and Save to CSV ---
columns = [
    'CustomerID', 'CustomerName', 'LastPurchaseDate', 'PurchaseFrequency',
    'AvgOrderValue', 'SupportTickets', 'EngagementScore', 'HealthScore',
    'ChurnRisk', 'PredictedLTV', 'SentimentHistory'
]
df = pd.DataFrame(data, columns=columns)

# Save the file
file_path = "data/customer_intelligence_data.csv"
df.to_csv(file_path, index=False)

print(f"✅ Success! Data file '{file_path}' created with {len(df)} records.")
