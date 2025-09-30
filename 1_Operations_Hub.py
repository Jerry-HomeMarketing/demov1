# 1_Operations_Hub

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="🚀",
    layout="wide",
)

# --- FUNCTION TO LOAD CUSTOM CSS ---
def load_css(file_name):
    """A function to load a CSS file from the local directory."""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the custom CSS
load_css("style.css")

# --- DATA LOADING AND PREPARATION ---
@st.cache_data
def load_data(file_path):
    """Load and preprocess the sales data from a local CSV file."""
    data = pd.read_csv(file_path)
    data['OrderDate'] = pd.to_datetime(data['OrderDate'])
    data['TotalRevenue'] = data['Quantity'] * data['Price']
    return data

try:
    df = load_data("data/innovategear_sales_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please ensure 'innovategear_sales_data.csv' is in the same folder as the app.")
    st.stop()


# --- SIDEBAR FOR FILTERS ---
st.sidebar.header("Dashboard Filters")
st.sidebar.markdown("""
This is your control panel. Filter the entire dashboard by date, product category, or marketing source.
Watch how all the charts and metrics update instantly!
""")

# Date Range Selector
min_date = df['OrderDate'].min().date()
max_date = df['OrderDate'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Category Multi-select
# FIX: Convert NumPy array from .unique() to a Python list
all_categories = list(df['Category'].unique())
selected_categories = st.sidebar.multiselect(
    "Select Product Categories",
    options=all_categories,
    default=all_categories
)

# Marketing Source Multi-select
# FIX: Convert NumPy array from .unique() to a Python list
all_sources = list(df['MarketingSource'].unique())
selected_sources = st.sidebar.multiselect(
    "Select Marketing Source",
    options=all_sources,
    default=all_sources
)


# Apply filters to the dataframe
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

filtered_df = df[
    (df['OrderDate'] >= start_date) &
    (df['OrderDate'] <= end_date) &
    (df['Category'].isin(selected_categories)) &
    (df['MarketingSource'].isin(selected_sources))
]

# --- MAIN DASHBOARD LAYOUT ---
st.title("🚀 Operations Hub")
st.markdown("### The 'Spreadsheet Killer' Demo")
st.markdown("""
Welcome to your new command center. No more wrestling with spreadsheets!
This interactive dashboard unifies your key business data into one place.
**Try using the filters on the left** to see how quickly you can get insights.
""")

st.divider()

# --- KPI METRICS ---
total_revenue = filtered_df['TotalRevenue'].sum()
total_sales = filtered_df['Quantity'].sum()
avg_satisfaction = filtered_df['SatisfactionScore'].mean()
unique_customers = filtered_df['CustomerName'].nunique()

# Display KPIs in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
with col2:
    st.metric(label="Total Items Sold", value=f"{total_sales:,}")
with col3:
    st.metric(label="Avg. Satisfaction Score", value=f"{avg_satisfaction:.2f} / 5")
with col4:
    st.metric(label="Unique Customers", value=f"{unique_customers}")

st.markdown("---")

# --- CHARTS ---
chart_template = "plotly_dark"

col_left, col_right = st.columns((7, 5))

with col_left:
    st.subheader("Revenue Over Time")
    revenue_over_time = filtered_df.set_index('OrderDate').resample('M')['TotalRevenue'].sum()
    fig_time = px.area(
        revenue_over_time,
        x=revenue_over_time.index,
        y='TotalRevenue',
        labels={'TotalRevenue': 'Monthly Revenue (USD)'},
        template=chart_template,
        markers=True
    )
    fig_time.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_time, use_container_width=True)

with col_right:
    st.subheader("Sales by Product Category")
    sales_by_category = filtered_df.groupby('Category')['TotalRevenue'].sum().sort_values(ascending=True)
    fig_cat = px.bar(
        sales_by_category,
        orientation='h',
        labels={'value': 'Total Revenue (USD)', 'index': 'Category'},
        template=chart_template,
        color=sales_by_category.values,
        color_continuous_scale=px.colors.sequential.Teal
    )
    fig_cat.update_layout(height=400, coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_cat, use_container_width=True)

# --- GEOGRAPHICAL AND DETAILED ANALYSIS ---
st.subheader("Geographical Sales Performance")
sales_by_state = filtered_df.groupby('State')['TotalRevenue'].sum().reset_index()

fig_map = px.choropleth(
    sales_by_state,
    locations='State',
    locationmode='USA-states',
    color='TotalRevenue',
    scope='usa',
    color_continuous_scale="Teal",
    labels={'TotalRevenue': 'Total Revenue'}
)
fig_map.update_layout(
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    height=500,
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_map, use_container_width=True)

# --- DETAILED DATA VIEW ---
st.subheader("Drill-Down: Raw Data Explorer")
st.markdown("Filter and sort the raw data to find specific transactions. This table is fully interactive.")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400,
    column_config={
        "OrderDate": st.column_config.DateColumn(format="YYYY-MM-DD"),
        "Price": st.column_config.NumberColumn(format="$%.2f"),
        "TotalRevenue": st.column_config.NumberColumn(format="$%.2f"),
    },
    hide_index=True,
)

st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting. Contact us to build a custom AI dashboard for your business!")
