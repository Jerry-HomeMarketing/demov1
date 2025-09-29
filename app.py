# generate_data.py
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# --- Configuration ---
NUM_RECORDS = 500
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

# --- Sample Data Lists ---
PRODUCTS = {
    'Smart Home': ['AI Voice Assistant', 'Smart Thermostat', 'Robotic Vacuum'],
    'Wearables': ['Fitness Tracker', 'Smartwatch', 'AR Glasses'],
    'Accessories': ['Wireless Charger', 'Portable Power Bank', 'Noise-Cancelling Earbuds']
}
CUSTOMERS = [
    'Alpha Corp', 'Beta Industries', 'Gamma Solutions', 'Delta Tech', 'Epsilon Global',
    'Zeta Services', 'Omega Holdings', 'Theta Digital', 'Iota Innovations', 'Kappa Logistics'
]
LOCATIONS = {
    'New York': 'NY', 'California': 'CA', 'Texas': 'TX', 'Florida': 'FL',
    'Illinois': 'IL', 'Pennsylvania': 'PA', 'Ohio': 'OH', 'Georgia': 'GA'
}
MARKETING_SOURCES = ['Google Ads', 'Organic Search', 'Social Media', 'Referral', 'Email Campaign']

# --- Data Generation Logic ---
data = []
for _ in range(NUM_RECORDS):
    # Choose a random category and then a product from that category
    category = random.choice(list(PRODUCTS.keys()))
    product = random.choice(PRODUCTS[category])
    
    # Generate random order date
    time_between_dates = END_DATE - START_DATE
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    order_date = START_DATE + timedelta(days=random_number_of_days)
    
    # Generate other random data
    quantity = np.random.randint(1, 10)
    price = round(np.random.uniform(29.99, 499.99), 2)
    customer_name = random.choice(CUSTOMERS)
    state = random.choice(list(LOCATIONS.keys()))
    state_abbr = LOCATIONS[state]
    marketing_source = random.choice(MARKETING_SOURCES)
    satisfaction_score = np.random.randint(3, 6) # Skew towards higher satisfaction
    
    data.append([
        f"ORD-{1001 + _}",
        order_date.strftime("%Y-%m-%d"),
        customer_name,
        state_abbr,
        product,
        category,
        quantity,
        price,
        marketing_source,
        satisfaction_score
    ])

# --- Create DataFrame and Save to CSV ---
columns = [
    'OrderID', 'OrderDate', 'CustomerName', 'State', 'Product', 'Category',
    'Quantity', 'Price', 'MarketingSource', 'SatisfactionScore'
]
df = pd.DataFrame(data, columns=columns)

# Save the file
file_path = "innovategear_sales_data.csv"
df.to_csv(file_path, index=False)

print(f"✅ Success! Data file '{file_path}' created with {len(df)} records.")
