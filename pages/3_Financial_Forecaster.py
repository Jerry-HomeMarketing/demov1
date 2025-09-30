# pages/3_💰_Financial_Forecaster.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dynamic Financial Forecaster", page_icon="💰", layout="wide")

# --- CSS & DATA ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    return data
try:
    df = load_data("data/financial_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_financial_data.py' first.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("What-If Scenario Planner")
sales_growth_rate = st.sidebar.slider("Future Monthly Sales Growth (%)", -10, 20, 3) / 100.0
new_monthly_expense = st.sidebar.slider("New Monthly Recurring Expense ($)", 0, 10000, 1500)
st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")

# --- MAIN LAYOUT ---
st.title("💰 The Dynamic Financial Forecaster")
st.markdown("### AI-Driven Profitability & Cash Flow")

# --- Cash Flow Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Interactive 'What-If' Cash Flow Projections")
df_monthly = df.copy()
df_monthly['Month'] = df_monthly['Date'].dt.to_period('M').dt.to_timestamp()
monthly_summary = df_monthly.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
monthly_summary['CashFlow'] = monthly_summary['Income'] - monthly_summary['Expense']
last_known_month = monthly_summary.index[-1]
forecast_dates = [last_known_month + pd.DateOffset(months=i) for i in range(1, 13)]
forecast_data = []
for i, month in enumerate(forecast_dates):
    forecasted_income = monthly_summary['Income'].iloc[-1] * ((1 + sales_growth_rate) ** (i + 1))
    forecasted_expense = monthly_summary['Expense'].iloc[-1] + new_monthly_expense
    forecast_data.append([month, forecasted_income - forecasted_expense])
forecast_df = pd.DataFrame(forecast_data, columns=['Month', 'CashFlow']).set_index('Month')
combined_cashflow = pd.concat([monthly_summary['CashFlow'], forecast_df['CashFlow']])
fig_cashflow = go.Figure()
fig_cashflow.add_trace(go.Scatter(x=combined_cashflow.index, y=combined_cashflow.values, mode='lines+markers', line=dict(color='#2E8B57', width=3)))
fig_cashflow.add_vline(x=last_known_month, line_width=2, line_dash="dash", line_color="gray")
fig_cashflow.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_cashflow, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Anomaly & Profitability Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2 = st.columns((6, 5))
with col1:
    st.subheader("AI-Powered Anomaly Detection")
    expenses_df = df[df['Type'] == 'Expense'].copy()
    expenses_df['Month'] = expenses_df['Date'].dt.strftime('%Y-%m')
    expense_pivot = expenses_df.pivot_table(index='Category', columns='Month', values='Amount', aggfunc='sum').fillna(0)
    fig_heatmap = px.imshow(expense_pivot, color_continuous_scale="Reds", template="plotly_dark", aspect="auto")
    fig_heatmap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heatmap, use_container_width=True)
with col2:
    st.subheader("Profitability Treemap")
    income_df = df[df['Type'] == 'Income']
    profit_by_cat = income_df.groupby('Category')['Amount'].sum().reset_index()
    fig_treemap = px.treemap(profit_by_cat, path=['Category'], values='Amount', color='Amount', color_continuous_scale='Greens', template="plotly_dark")
    fig_treemap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_treemap, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Summary Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Automated Financial Summary")
total_income = monthly_summary['Income'].sum()
total_expense = monthly_summary['Expense'].sum()
net_profit = total_income - total_expense
cash_flow_trend = "improving" if monthly_summary['CashFlow'].iloc[-1] > monthly_summary['CashFlow'].iloc[-2] else "declining"
top_income_stream = income_df.groupby('Category')['Amount'].sum().idxmax()
summary_text = (
    f"Over the past 24 months, your business has generated **\${total_income:,.2f}** in total income against "
    f"**\${total_expense:,.2f}** in total expenses, resulting in a net profit of **\${net_profit:,.2f}**. "
    f"Your primary income driver has been **{top_income_stream}**. The recent cash flow trend is **{cash_flow_trend}**. "
    f"Based on your 'What-If' scenario, the forecast indicates your cash flow will trend "
    f"{'upwards' if forecast_df['CashFlow'].iloc[-1] > forecast_df['CashFlow'].iloc[0] else 'downwards'} over the next year."
)
st.info(summary_text)
st.markdown('</div>', unsafe_allow_html=True)
