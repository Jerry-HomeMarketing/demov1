# app.py (Default, Unstyled Version)

import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Operations Hub",
    page_icon="🚀",
    layout="wide",
)

# --- DATA LOADING ---
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['OrderDate'] = pd.to_datetime(data['OrderDate'])
    data['TotalRevenue'] = data['Quantity'] * data['Price']
    return data

try:
    df = load_data("innovategear_sales_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please ensure 'innovategear_sales_data.csv' is in the same folder.")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("Dashboard Filters")
    min_date = df['OrderDate'].min().date()
    max_date = df['OrderDate'].max().date()
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    all_categories = df['Category'].unique()
    selected_categories = st.multiselect("Select Categories", all_categories, default=all_categories)
    
    all_sources = df['MarketingSource'].unique()
    selected_sources = st.multiselect("Select Marketing Sources", all_sources, default=all_sources)

    st.markdown("---")
    st.info("Built by Home Marketing & Consulting")

# --- DATA FILTERING ---
start_date_dt, end_date_dt = pd.to_datetime(start_date), pd.to_datetime(end_date)
filtered_df = df[(df['OrderDate'] >= start_date_dt) & (df['OrderDate'] <= end_date_dt) & (df['Category'].isin(selected_categories)) & (df['MarketingSource'].isin(selected_sources))]

# --- MAIN DASHBOARD ---
st.title("Dashboard")
st.markdown("This interactive dashboard unifies your key business data into one place.")

# --- ROBUSTNESS CHECK ---
if not filtered_df.empty:
    # --- KPI METRICS ---
    total_revenue = filtered_df['TotalRevenue'].sum()
    total_sales = filtered_df['Quantity'].sum()
    avg_satisfaction = filtered_df['SatisfactionScore'].mean()
    unique_customers = filtered_df['CustomerName'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Revenue", value=f"${total_revenue:,.0f}")
    with col2:
        st.metric(label="Items Sold", value=f"{total_sales:,}")
    with col3:
        st.metric(label="Avg. Satisfaction", value=f"{avg_satisfaction:.2f}")
    with col4:
        st.metric(label="Unique Customers", value=f"{unique_customers}")
    
    st.divider()

    # --- CHARTS ---
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Revenue Over Time")
        revenue_over_time = filtered_df.set_index('OrderDate').resample('M')['TotalRevenue'].sum()
        fig_time = px.area(revenue_over_time, x=revenue_over_time.index, y='TotalRevenue')
        # No custom styling - let Streamlit handle the theme
        st.plotly_chart(fig_time, use_container_width=True)

    with chart_col2:
        st.subheader("Sales by Category")
        sales_by_category = filtered_df.groupby('Category')['TotalRevenue'].sum().sort_values(ascending=False)
        fig_cat = px.bar(sales_by_category)
        # No custom styling - let Streamlit handle the theme
        st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # --- MAP ---
    st.subheader("Geographical Sales Performance")
    sales_by_state = filtered_df.groupby('State')['TotalRevenue'].sum().reset_index()
    fig_map = px.choropleth(
        sales_by_state, locations='State', locationmode='USA-states', color='TotalRevenue',
        scope='usa'
    )
    # No custom styling - let Streamlit handle the theme
    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.warning("No data available for the selected filters. Please adjust your selections.")
