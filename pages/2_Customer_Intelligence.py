# pages/2_🔮_Customer_Crystal_Ball.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast # To safely evaluate string-formatted lists

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Customer Intelligence Dashboard",
    page_icon="🔮",
    layout="wide",
)

# --- FUNCTION TO LOAD CUSTOM CSS ---
def load_css(file_name):
    """A function to load a CSS file from the root directory."""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the custom CSS from the root directory
load_css("style.css")


# --- DATA LOADING AND PREPARATION ---
@st.cache_data
def load_data(file_path):
    """Load and preprocess the customer intelligence data."""
    data = pd.read_csv(file_path)
    # Convert string representation of list to actual list
    data['SentimentHistory'] = data['SentimentHistory'].apply(ast.literal_eval)
    return data

try:
    df = load_data("data/customer_intelligence_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_customer_data.py' first.")
    st.stop()


# --- MAIN DASHBOARD LAYOUT ---
st.title("🔮 Customer Intelligence")
st.markdown("### Predictive Customer Intelligence")
st.markdown("""
This dashboard provides a proactive approach to customer relationship management.
Instead of just looking at past sales, we're using AI-simulated models to predict future customer behavior,
identify churn risks, and suggest actions to improve retention.
""")

st.divider()

# --- SIDEBAR FOR FILTERS ---
st.sidebar.header("Customer Filters")
selected_risk = st.sidebar.selectbox(
    "Filter by Churn Risk",
    options=['All'] + list(df['ChurnRisk'].unique()),
    index=0
)

# Apply filters
if selected_risk != 'All':
    filtered_df = df[df['ChurnRisk'] == selected_risk].copy()
else:
    filtered_df = df.copy()


# --- KEY FEATURES ---

# 1. Customer Health Scorecard
st.subheader("Customer Health Scorecard")
st.markdown("A real-time, color-coded grid of your customers. The health score (0-100) is an AI-generated metric based on purchase frequency, recency, and support history. Green is good, red is at-risk.")

def get_color_for_score(score):
    if score > 75:
        return f"background-color: #2E8B57; color: white" # SeaGreen
    elif score > 45:
        return f"background-color: #DAA520; color: white" # GoldenRod
    else:
        return f"background-color: #B22222; color: white" # FireBrick

styled_df = filtered_df[['CustomerName', 'HealthScore', 'ChurnRisk', 'PredictedLTV']].sort_values('HealthScore', ascending=False)
styled_df = styled_df.style.apply(lambda x: [get_color_for_score(v) for v in x], subset=['HealthScore']) \
                       .format({'PredictedLTV': '${:,.2f}'})

st.dataframe(styled_df, use_container_width=True, height=35 * (len(filtered_df) + 1))


# --- SPLIT LAYOUT FOR CHARTS ---
col1, col2 = st.columns(2)

with col1:
    # 2. Churn Risk Segmentation
    st.subheader("Churn Risk Segmentation")
    churn_counts = filtered_df['ChurnRisk'].value_counts()
    fig_pie = px.pie(
        values=churn_counts.values,
        names=churn_counts.index,
        title="Customer Base by Churn Risk",
        color=churn_counts.index,
        color_discrete_map={'High': '#B22222', 'Medium': '#DAA520', 'Low': '#2E8B57'},
        template="plotly_dark"
    )
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # 4. AI-Recommended Actions
    st.subheader("AI-Recommended Next Best Actions")
    st.markdown("Based on the selected customer's risk profile, the AI suggests actions to take.")
    
    # Customer selector for this section
    customer_for_action = st.selectbox(
        "Select a Customer to see AI Recommendations",
        options=filtered_df['CustomerName']
    )
    
    customer_data = df[df['CustomerName'] == customer_for_action].iloc[0]
    risk = customer_data['ChurnRisk']
    
    if risk == 'High':
        st.warning(f"**Action for {customer_for_action} (High Risk):**")
        st.markdown("- **Immediate Outreach:** Personal call from a senior account manager to address any issues.\n"
                    "- **Exclusive Offer:** Provide a significant loyalty discount on their next purchase.\n"
                    "- **Feedback Survey:** Send a survey to understand their dissatisfaction.")
    elif risk == 'Medium':
        st.info(f"**Action for {customer_for_action} (Medium Risk):**")
        st.markdown("- **Personalized Email:** Send a check-in email highlighting new products relevant to them.\n"
                    "- **Engage on Social Media:** Like or comment on their company's social media posts.\n"
                    "- **Offer Early Access:** Give them a sneak peek at an upcoming feature or product.")
    else:
        st.success(f"**Action for {customer_for_action} (Low Risk):**")
        st.markdown("- **Nurture Relationship:** Send a thank-you note or a small, unexpected gift.\n"
                    "- **Request a Testimonial:** Ask them to share their positive experience.\n"
                    "- **Upsell Opportunity:** Introduce them to premium services or complementary products.")

st.divider()

# --- TIME-SERIES VISUALIZATIONS ---
st.subheader("Predictive Forecasts & Trends")
tab1, tab2 = st.tabs(["Predicted Lifetime Value (LTV)", "Customer Sentiment Trendline"])

with tab1:
    # 3. Predicted Lifetime Value (LTV) Forecast
    st.markdown("This chart forecasts the total revenue we can expect from different customer cohorts over time. It helps prioritize high-value segments.")
    ltv_by_risk = filtered_df.groupby('ChurnRisk')['PredictedLTV'].sum().sort_values(ascending=False)
    fig_ltv = px.bar(
        ltv_by_risk,
        x=ltv_by_risk.index,
        y=ltv_by_risk.values,
        title="Total Predicted LTV by Risk Segment",
        labels={'x': 'Churn Risk Segment', 'y': 'Total Predicted LTV (USD)'},
        color=ltv_by_risk.index,
        color_discrete_map={'High': '#B22222', 'Medium': '#DAA520', 'Low': '#2E8B57'},
        template="plotly_dark"
    )
    fig_ltv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_ltv, use_container_width=True)


with tab2:
    # 5. Sentiment Analysis Trendline
    st.markdown("This graph visually tracks the average customer sentiment over the last 12 months by analyzing feedback from emails, surveys, and reviews.")
    
    # Prepare data for sentiment trend
    sentiment_df = pd.DataFrame(filtered_df['SentimentHistory'].to_list(), index=filtered_df['CustomerName'])
    sentiment_df.columns = [f"Month -{11-i}" for i in range(12)]
    avg_sentiment = sentiment_df.mean(axis=0).rename('AverageSentiment').reset_index()
    avg_sentiment.columns = ['Month', 'AverageSentiment']
    
    fig_sentiment = px.area(
        avg_sentiment,
        x='Month',
        y='AverageSentiment',
        title="Average Customer Sentiment Over Time",
        markers=True,
        template="plotly_dark",
        labels={'AverageSentiment': 'Sentiment Score (0.0 to 1.0)'}
    )
    fig_sentiment.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_sentiment.update_yaxes(range=[0, 1])
    st.plotly_chart(fig_sentiment, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")
