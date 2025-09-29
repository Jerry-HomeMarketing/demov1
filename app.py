# app.py (Final "Check Box" Inspired Theme)

import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Operations Hub",
    page_icon="🚀",
    layout="wide",
)

# --- CSS INJECTION ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

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
    st.error("Data file not found. Please ensure 'innovategear_sales_data.csv' is in the same folder as the app.")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.title("🚀 Operations Hub")
    min_date = df['OrderDate'].min().date()
    max_date = df['OrderDate'].max().date()
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    all_categories = df['Category'].unique()
    selected_categories = st.multiselect("Select Product Categories", all_categories, default=all_categories)
    
    all_sources = df['MarketingSource'].unique()
    selected_sources = st.multiselect("Select Marketing Source", all_sources, default=all_sources)

# --- DATA FILTERING ---
start_date_dt = pd.to_datetime(start_date)
end_date_dt = pd.to_datetime(end_date)
filtered_df = df[
    (df['OrderDate'] >= start_date_dt) & 
    (df['OrderDate'] <= end_date_dt) & 
    (df['Category'].isin(selected_categories)) & 
    (df['MarketingSource'].isin(selected_sources))
]

# --- MAIN DASHBOARD LAYOUT ---
st.title("Dashboard")

# --- ROBUSTNESS CHECK: Only display dashboard if there is data ---
if not filtered_df.empty:
    # --- KPI METRICS ---
    total_revenue = filtered_df['TotalRevenue'].sum()
    total_sales = filtered_df['Quantity'].sum()
    avg_satisfaction = filtered_df['SatisfactionScore'].mean()
    unique_customers = filtered_df['CustomerName'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="card kpi-card"><h3>Total Revenue</h3><p>${total_revenue:,.0f}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card kpi-card"><h3>Items Sold</h3><p>{total_sales:,}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card kpi-card"><h3>Avg. Satisfaction</h3><p>{avg_satisfaction:.2f}</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="card kpi-card"><h3>Unique Customers</h3><p>{unique_customers}</p></div>', unsafe_allow_html=True)

    # --- CHARTS ---
    chart_col1, chart_col2 = st.columns(2)
    accent_color = "#23d160" # Vibrant green

    with chart_col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Revenue Over Time")
        revenue_over_time = filtered_df.set_index('OrderDate').resample('M')['TotalRevenue'].sum()
        fig_time = px.area(revenue_over_time, x=revenue_over_time.index, y='TotalRevenue')
        fig_time.update_traces(line_color=accent_color, fillcolor='rgba(35, 209, 96, 0.2)')
        fig_time.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffe9',
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'), yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=350, margin=dict(l=20, r=20, t=40, b=20), xaxis_title=None, yaxis_title=None
        )
        st.plotly_chart(fig_time, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Sales by Category")
        sales_by_category = filtered_df.groupby('Category')['TotalRevenue'].sum().sort_values(ascending=True)
        fig_cat = px.bar(sales_by_category, orientation='h')
        fig_cat.update_traces(marker_color=accent_color)
        fig_cat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffe9',
            xaxis=dict(showgrid=False), yaxis=dict(showticklabels=False), height=350,
            margin=dict(l=20, r=20, t=40, b=20), xaxis_title=None, yaxis_title=None
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- MAP (BUG FIXED) ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Geographical Sales Performance")
    sales_by_state = filtered_df.groupby('State')['TotalRevenue'].sum().reset_index()
    fig_map = px.choropleth(
        sales_by_state, locations='State', locationmode='USA-states',
        color='TotalRevenue', scope='usa',
        color_continuous_scale=px.colors.sequential.Greens # Use a green scale for the map
    )
    fig_map.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', geo_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffe9', height=400, margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- Display message if no data is available ---
    st.warning("No data available for the selected filters. Please adjust your selections.")
