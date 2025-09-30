# pages/2_🔮_Customer_Crystal_Ball.py

import streamlit as st
import pandas as pd
import plotly.express as px
import ast

# --- PAGE CONFIG ---
st.set_page_config(page_title="Customer Intelligence Dashboard", page_icon="🔮", layout="wide")

# --- CSS & DATA ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['SentimentHistory'] = data['SentimentHistory'].apply(ast.literal_eval)
    return data
try:
    df = load_data("data/customer_intelligence_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_customer_data.py' first.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Customer Filters")
selected_risk = st.sidebar.selectbox("Filter by Churn Risk", options=['All'] + list(df['ChurnRisk'].unique()))
st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")

# --- FILTERING ---
filtered_df = df if selected_risk == 'All' else df[df['ChurnRisk'] == selected_risk].copy()

# --- MAIN LAYOUT ---
st.title("🔮 The Customer Crystal Ball")
st.markdown("### Predictive Customer Intelligence")

# --- Scorecard Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Customer Health Scorecard")
def get_color_for_score(score):
    if score > 75: return "background-color: #2E8B57; color: white"
    elif score > 45: return "background-color: #DAA520; color: white"
    else: return "background-color: #B22222; color: white"
styled_df = filtered_df[['CustomerName', 'HealthScore', 'ChurnRisk', 'PredictedLTV']].sort_values('HealthScore', ascending=False)
styled_df_display = styled_df.style.apply(lambda x: [get_color_for_score(v) for v in x], subset=['HealthScore']).format({'PredictedLTV': '${:,.2f}'})
st.dataframe(styled_df_display, use_container_width=True, height=35 * (len(filtered_df) + 1))
st.markdown('</div>', unsafe_allow_html=True)

# --- Segmentation & Actions Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Churn Risk Segmentation")
    churn_counts = filtered_df['ChurnRisk'].value_counts()
    fig_pie = px.pie(values=churn_counts.values, names=churn_counts.index, color=churn_counts.index, color_discrete_map={'High': '#B22222', 'Medium': '#DAA520', 'Low': '#2E8B57'}, template="plotly_dark")
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    st.subheader("AI-Recommended Actions")
    customer_for_action = st.selectbox("Select a Customer", options=filtered_df['CustomerName'])
    if customer_for_action:
        risk = df[df['CustomerName'] == customer_for_action].iloc[0]['ChurnRisk']
        if risk == 'High': st.warning(f"**Action for {customer_for_action} (High Risk):**\n- Immediate Personal Outreach\n- Offer Loyalty Discount")
        elif risk == 'Medium': st.info(f"**Action for {customer_for_action} (Medium Risk):**\n- Personalized Email Check-in\n- Offer Early Access to New Products")
        else: st.success(f"**Action for {customer_for_action} (Low Risk):**\n- Nurture Relationship (Thank you note)\n- Request a Testimonial")
st.markdown('</div>', unsafe_allow_html=True)

# --- Forecasts & Trends Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Predictive Forecasts & Trends")
tab1, tab2 = st.tabs(["Predicted LTV Forecast", "Sentiment Trendline"])
with tab1:
    ltv_by_risk = filtered_df.groupby('ChurnRisk')['PredictedLTV'].sum().sort_values(ascending=False)
    fig_ltv = px.bar(ltv_by_risk, x=ltv_by_risk.index, y=ltv_by_risk.values, color=ltv_by_risk.index, color_discrete_map={'High': '#B22222', 'Medium': '#DAA520', 'Low': '#2E8B57'}, template="plotly_dark")
    fig_ltv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_ltv, use_container_width=True)
with tab2:
    sentiment_df = pd.DataFrame(filtered_df['SentimentHistory'].to_list(), index=filtered_df['CustomerName'])
    sentiment_df.columns = [f"Month -{11-i}" for i in range(12)]
    avg_sentiment = sentiment_df.mean(axis=0).rename('AverageSentiment').reset_index()
    avg_sentiment.columns = ['Month', 'AverageSentiment']
    fig_sentiment = px.area(avg_sentiment, x='Month', y='AverageSentiment', markers=True, template="plotly_dark")
    fig_sentiment.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)').update_yaxes(range=[0, 1])
    st.plotly_chart(fig_sentiment, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
