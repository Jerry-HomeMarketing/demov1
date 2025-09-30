# generate_ad_data.py
import pandas as pd
import numpy as np
import random
from datetime import date, timedelta

# --- Configuration ---
START_DATE = date(2024, 1, 1)
DAYS_OF_DATA = 90
PLATFORMS = {
    'Google Ads': {'cpc_range': (1.5, 4.0), 'conv_rate_range': (0.02, 0.05)},
    'Meta Ads': {'cpc_range': (0.8, 2.5), 'conv_rate_range': (0.01, 0.04)},
    'LinkedIn Ads': {'cpc_range': (4.0, 7.5), 'conv_rate_range': (0.005, 0.02)}
}
CAMPAIGNS = ['Brand Awareness', 'Lead Generation', 'Website Traffic', 'Sales Conversion']
AD_CREATIVES = {
    'Image': ['Product Showcase A.jpg', 'Lifestyle B.png', 'Infographic C.jpg'],
    'Video': ['Testimonial Reel.mp4', 'Explainer Animation.mov', 'Behind the Scenes.mp4'],
    'Text': ['"Limited Time Offer" Ad', '"Free Demo" Ad', '"Case Study" Ad']
}

# --- Data Generation Logic ---
data = []
for day_num in range(DAYS_OF_DATA):
    current_date = START_DATE + timedelta(days=day_num)
    for platform, metrics in PLATFORMS.items():
        for campaign in CAMPAIGNS:
            # Choose a random creative type and a specific creative
            creative_type = random.choice(list(AD_CREATIVES.keys()))
            creative_name = random.choice(AD_CREATIVES[creative_type])

            # Generate core metrics
            impressions = random.randint(5000, 20000)
            clicks = int(impressions * random.uniform(0.01, 0.06))
            spend = clicks * random.uniform(metrics['cpc_range'][0], metrics['cpc_range'][1])
            conversions = int(clicks * random.uniform(metrics['conv_rate_range'][0], metrics['conv_rate_range'][1]))
            revenue = conversions * random.uniform(50, 300) # Revenue per conversion

            data.append([
                current_date.strftime("%Y-%m-%d"),
                platform,
                campaign,
                creative_type,
                creative_name,
                impressions,
                clicks,
                round(spend, 2),
                conversions,
                round(revenue, 2)
            ])

# --- Create DataFrame and Save to CSV ---
columns = [
    'Date', 'Platform', 'Campaign', 'CreativeType', 'CreativeName',
    'Impressions', 'Clicks', 'Spend', 'Conversions', 'Revenue'
]
df = pd.DataFrame(data, columns=columns)

# Save the file
file_path = "data/ad_performance_data.csv"
df.to_csv(file_path, index=False)

print(f"✅ Success! Data file '{file_path}' created with {len(df)} records.")