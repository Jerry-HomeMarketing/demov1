# generate_financial_data.py
import pandas as pd
import numpy as np
import random
from datetime import date
from dateutil.relativedelta import relativedelta

# --- Configuration ---
START_DATE = date(2023, 1, 1)
MONTHS_OF_DATA = 24 # Generate 2 years of historical data

# --- Sample Data Lists ---
INCOME_CATEGORIES = {
    'Product A Sales': 25000,
    'Product B Sales': 15000,
    'Consulting Services': 10000,
    'Maintenance Contracts': 5000
}

EXPENSE_CATEGORIES = {
    'Salaries': 18000,
    'Rent': 5000,
    'Marketing': 3500,
    'Software & Subscriptions': 1500,
    'Utilities': 800,
    'Office Supplies': 300
}

# --- Data Generation Logic ---
data = []
current_date = START_DATE

for i in range(MONTHS_OF_DATA):
    month_date = current_date + relativedelta(months=i)
    
    # Generate Income
    for category, base_amount in INCOME_CATEGORIES.items():
        # Add some random variance and slight growth over time
        amount = base_amount * (1 + random.uniform(-0.1, 0.1)) * (1 + i * 0.01)
        data.append([month_date.strftime("%Y-%m-%d"), 'Income', category, round(amount, 2)])
        
    # Generate Expenses
    for category, base_amount in EXPENSE_CATEGORIES.items():
        amount = base_amount * (1 + random.uniform(-0.05, 0.05))
        
        # --- ANOMALY INJECTION ---
        # Inject an unusually high Marketing spend in a specific month
        if category == 'Marketing' and i == 18: # 18 months in
             amount *= 3.5 
        # Inject an unusually high Software spend in another month
        if category == 'Software & Subscriptions' and i == 13: # 13 months in
            amount *= 4.0
            
        data.append([month_date.strftime("%Y-%m-%d"), 'Expense', category, round(amount, 2)])

# --- Create DataFrame and Save to CSV ---
columns = ['Date', 'Type', 'Category', 'Amount']
df = pd.DataFrame(data, columns=columns)

# Save the file
file_path = "data/financial_data.csv"
df.to_csv(file_path, index=False)

print(f"✅ Success! Data file '{file_path}' created with {len(df)} records.")