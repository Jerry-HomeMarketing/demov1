# 1_🚀_Operations_Hub.py

import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="InnovateGear Sales Dashboard", page_icon="🚀", layout="wide")

# --- CSS & DATA ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['OrderDate'] = pd.to_datetime(data['OrderDate'])
    data['TotalRevenue'] = data['Quantity'] * data['Price']
    return data

try:
    df = load_data("data/innovategear_sales_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_data.py' first.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Dashboard Filters")
min_date, max_date = df['OrderDate'].min().date(), df['OrderDate'].max().date()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
selected_categories = st.sidebar.multiselect("Select Product Categories", options=list(df['Category'].unique()), default=list(df['Category'].unique()))
selected_sources = st.sidebar.multiselect("Select Marketing Source", options=list(df['MarketingSource'].unique()), default=list(df['MarketingSource'].unique()))
st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")

# --- FILTERING ---
filtered_df = df[(df['OrderDate'] >= pd.to_datetime(start_date)) & (df['OrderDate'] <= pd.to_datetime(end_date)) & (df['Category'].isin(selected_categories)) & (df['MarketingSource'].isin(selected_sources))]

# --- MAIN LAYOUT ---
st.title("🚀 InnovateGear Operations Hub")
st.markdown("### The 'Spreadsheet Killer' Demo")

# --- KPI Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
total_revenue = filtered_df['TotalRevenue'].sum()
total_sales = filtered_df['Quantity'].sum()
avg_satisfaction = filtered_df['SatisfactionScore'].mean()
unique_customers = filtered_df['CustomerName'].nunique()
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
with col2: st.metric(label="Total Items Sold", value=f"{total_sales:,}")
with col3: st.metric(label="Avg. Satisfaction Score", value=f"{avg_satisfaction:.2f} / 5")
with col4: st.metric(label="Unique Customers", value=f"{unique_customers}")
st.markdown('</div>', unsafe_allow_html=True)

# --- Charts Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
col_left, col_right = st.columns((7, 5))
with col_left:
    st.subheader("Revenue Over Time")
    revenue_over_time = filtered_df.set_index('OrderDate').resample('M')['TotalRevenue'].sum()
    fig_time = px.area(revenue_over_time, x=revenue_over_time.index, y='TotalRevenue', markers=True, template="plotly_dark")
    fig_time.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_time, use_container_width=True)
with col_right:
    st.subheader("Sales by Product Category")
    sales_by_category = filtered_df.groupby('Category')['TotalRevenue'].sum().sort_values(ascending=True)
    fig_cat = px.bar(sales_by_category, orientation='h', color=sales_by_category.values, color_continuous_scale=px.colors.sequential.Teal, template="plotly_dark")
    fig_cat.update_layout(height=400, coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_cat, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Geo & Data Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Geographical Sales Performance")
    sales_by_state = filtered_df.groupby('State')['TotalRevenue'].sum().reset_index()
    fig_map = px.choropleth(sales_by_state, locations='State', locationmode='USA-states', color='TotalRevenue', scope='usa', color_continuous_scale="Teal", template="plotly_dark")
    fig_map.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)
with col2:
    st.subheader("Drill-Down Raw Data")
    st.dataframe(filtered_df, use_container_width=True, height=450, hide_index=True, column_config={"OrderDate": st.column_config.DateColumn(format="YYYY-MM-DD"), "Price": st.column_config.NumberColumn(format="$%.2f"),"TotalRevenue": st.column_config.NumberColumn(format="$%.2f")})
st.markdown('</div>', unsafe_allow_html=True)
