# pages/3_💰_Financial_Forecaster.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dynamic Financial Forecaster",
    page_icon="💰",
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
    """Load and preprocess the financial data."""
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    return data

try:
    df = load_data("data/financial_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_financial_data.py' first.")
    st.stop()


# --- MAIN DASHBOARD LAYOUT ---
st.title("💰 The Dynamic Financial Forecaster")
st.markdown("### AI-Driven Profitability & Cash Flow")
st.markdown("""
This tool moves beyond static financial reports. Use the sliders in the sidebar to create dynamic,
AI-driven forecasts and simulate business scenarios. See the future impact on your cash flow instantly.
""")
st.divider()

# --- SIDEBAR FOR "WHAT-IF" SCENARIOS ---
st.sidebar.header("What-If Scenario Planner")
st.sidebar.markdown("Adjust these sliders to forecast future financial performance.")

# Sliders for forecasting
sales_growth_rate = st.sidebar.slider("Future Monthly Sales Growth (%)", -10, 20, 3) / 100.0
new_monthly_expense = st.sidebar.slider("New Monthly Recurring Expense ($)", 0, 10000, 1500)


# --- FEATURE 1: INTERACTIVE "WHAT-IF" CASH FLOW PROJECTIONS ---
st.subheader("Interactive 'What-If' Cash Flow Projections")
st.markdown("This chart combines your historical cash flow with an AI-powered forecast. Change the sliders on the left to see how your decisions could impact your future cash position.")

# Prepare historical data
df_monthly = df.copy()
df_monthly['Month'] = df_monthly['Date'].dt.to_period('M').dt.to_timestamp()
monthly_summary = df_monthly.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
monthly_summary['CashFlow'] = monthly_summary['Income'] - monthly_summary['Expense']

# Create forecast
last_known_month = monthly_summary.index[-1]
last_income = monthly_summary['Income'].iloc[-1]
last_expense = monthly_summary['Expense'].iloc[-1]
forecast_dates = [last_known_month + pd.DateOffset(months=i) for i in range(1, 13)]
forecast_data = []

for i, month in enumerate(forecast_dates):
    forecasted_income = last_income * ((1 + sales_growth_rate) ** (i + 1))
    forecasted_expense = last_expense + new_monthly_expense
    forecasted_cashflow = forecasted_income - forecasted_expense
    forecast_data.append([month, forecasted_income, forecasted_expense, forecasted_cashflow])

forecast_df = pd.DataFrame(forecast_data, columns=['Month', 'Income', 'Expense', 'CashFlow']).set_index('Month')

# Combine historical and forecast data
combined_cashflow = pd.concat([monthly_summary['CashFlow'], forecast_df['CashFlow']])

# Plotting
fig_cashflow = go.Figure()
fig_cashflow.add_trace(go.Scatter(
    x=combined_cashflow.index, y=combined_cashflow.values,
    mode='lines+markers', name='Cash Flow',
    line=dict(color='#2E8B57', width=3)
))
# Add a vertical line to separate history from forecast
fig_cashflow.add_vline(x=last_known_month, line_width=2, line_dash="dash", line_color="gray")
fig_cashflow.add_annotation(x=last_known_month, y=combined_cashflow.max(), text="Forecast ->", showarrow=True, arrowhead=1)

fig_cashflow.update_layout(
    title="Historical vs. Forecasted Monthly Cash Flow",
    template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    yaxis_title="Cash Flow (USD)"
)
st.plotly_chart(fig_cashflow, use_container_width=True)


st.divider()
col1, col2 = st.columns((6, 5))

with col1:
    # --- FEATURE 2: ANOMALY DETECTION HEATMAP ---
    st.subheader("AI-Powered Anomaly Detection")
    st.markdown("A visual grid of expenses. The AI automatically flags unusual spending (3 standard deviations above the category average) to help you spot errors or fraud.")
    
    expenses_df = df[df['Type'] == 'Expense'].copy()
    expenses_df['Month'] = expenses_df['Date'].dt.strftime('%Y-%m')
    expense_pivot = expenses_df.pivot_table(index='Category', columns='Month', values='Amount', aggfunc='sum').fillna(0)
    
    # AI Simulation: Flag anomalies
    anomalies = []
    for category in expense_pivot.index:
        row = expense_pivot.loc[category]
        mean = row[row > 0].mean()
        std = row[row > 0].std()
        threshold = mean + 3 * std
        anomalous_months = row[row > threshold]
        for month, amount in anomalous_months.items():
            # --- FIX: Escape the '$' with a '\' to ensure it's treated as a literal character. ---
            anomalies.append(f"High spending of **\${amount:,.2f}** in **{category}** for month **{month}** (Threshold: **\${threshold:,.2f}**)")
    
    fig_heatmap = px.imshow(
        expense_pivot,
        labels=dict(x="Month", y="Category", color="Expense Amount"),
        title="Monthly Expenses by Category Heatmap",
        color_continuous_scale="Reds",
        template="plotly_dark",
        aspect="auto"
    )
    fig_heatmap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heatmap, use_container_width=True)

    if anomalies:
        st.warning("🚨 Anomalies Detected!")
        for anomaly in anomalies:
            st.markdown(f"- {anomaly}")

with col2:
    # --- FEATURE 3: PROFITABILITY TREEMAP ---
    st.subheader("Profitability Treemap")
    st.markdown("Visually breaks down your most profitable income streams. The size and color of each rectangle represent its contribution to total revenue.")
    
    income_df = df[df['Type'] == 'Income']
    profit_by_cat = income_df.groupby('Category')['Amount'].sum().reset_index()
    
    fig_treemap = px.treemap(
        profit_by_cat,
        path=['Category'],
        values='Amount',
        title='Revenue Contribution by Category',
        color='Amount',
        color_continuous_scale='Greens',
        template="plotly_dark"
    )
    fig_treemap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_treemap, use_container_width=True)


# --- FEATURE 4: AUTOMATED FINANCIAL SUMMARY (NLG) ---
st.divider()
st.subheader("Automated Financial Summary")
st.markdown("This is an AI-generated summary of your financial dashboard, highlighting key insights, risks, and opportunities.")

# Calculate summary metrics
total_income = monthly_summary['Income'].sum()
total_expense = monthly_summary['Expense'].sum()
net_profit = total_income - total_expense
cash_flow_trend = "improving" if monthly_summary['CashFlow'].iloc[-1] > monthly_summary['CashFlow'].iloc[-2] else "declining"
top_income_stream = profit_by_cat.sort_values('Amount', ascending=False).iloc[0]['Category']

# --- FIX: Rebuilt the summary string using clean concatenation to avoid whitespace issues. ---
# --- And escaped the dollar signs with '\'. ---
summary_parts = [
    f"Over the past 24 months, your business has generated **\${total_income:,.2f}** in total income against "
    f"**\${total_expense:,.2f}** in total expenses, resulting in a net profit of **\${net_profit:,.2f}**. "
    f"Your primary income driver has been **{top_income_stream}**. ",
    f"The recent cash flow trend is currently **{cash_flow_trend}**. "
]

if anomalies:
    summary_parts.append(
        f"The AI has detected **{len(anomalies)} potential spending anomaly/anomalies** that require your review, "
        "primarily in the categories highlighted above. "
    )
else:
    summary_parts.append(
        "The AI has not detected any significant spending anomalies in your historical data. "
    )

summary_parts.append(
    f"Based on your 'What-If' scenario of **{sales_growth_rate*100:.1f}% monthly sales growth** and "
    f"**\${new_monthly_expense:,.2f}** in new expenses, the forecast indicates your cash flow will trend "
    f"{'upwards' if forecast_df['CashFlow'].iloc[-1] > forecast_df['CashFlow'].iloc[0] else 'downwards'} over the next year."
)

summary_text = "".join(summary_parts)
st.info(summary_text)

st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")
