# pages/4_🎯_Ad_Performance_Command_Center.py

import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Ad Performance Command Center",
    page_icon="🎯",
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
    """Load and preprocess the ad performance data."""
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    # --- Feature Engineering for KPIs ---
    data['ROAS'] = data['Revenue'] / data['Spend']
    data['CTR'] = data['Clicks'] / data['Impressions']
    data['CPC'] = data['Spend'] / data['Clicks']
    data['ConversionRate'] = data['Conversions'] / data['Clicks']
    data.fillna(0, inplace=True) # Replace infinities or NaNs with 0
    data.replace([float('inf'), -float('inf')], 0, inplace=True)
    return data

try:
    df = load_data("data/ad_performance_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_ad_data.py' first.")
    st.stop()


# --- MAIN DASHBOARD LAYOUT ---
st.title("🎯 Ad Performance Command Center")
st.markdown("### A Unified View to Conquer Ad Complexity")
st.markdown("""
This dashboard addresses key advertiser pain points by unifying data from all platforms,
enabling customizable performance analysis, and highlighting creative insights.
**Use the sliders on the left** to define what 'performance' means to you.
""")
st.divider()

# --- SIDEBAR: CUSTOMIZABLE WEIGHTED RANKING ---
st.sidebar.header("Performance Grade Tuner")
st.sidebar.markdown("Set the importance of each KPI to calculate an overall 'Performance Grade' for each ad source.")
weight_roas = st.sidebar.slider("ROAS Weight", 0, 100, 50)
weight_ctr = st.sidebar.slider("CTR Weight", 0, 100, 15)
weight_cpc = st.sidebar.slider("CPC Weight (lower is better)", 0, 100, 20)
weight_conv_rate = st.sidebar.slider("Conversion Rate Weight", 0, 100, 15)

# Normalize weights to sum to 1
total_weight = weight_roas + weight_ctr + weight_cpc + weight_conv_rate
if total_weight == 0: total_weight = 1 # Avoid division by zero
norm_roas = weight_roas / total_weight
norm_ctr = weight_ctr / total_weight
norm_cpc = weight_cpc / total_weight
norm_conv_rate = weight_conv_rate / total_weight

# --- DATA AGGREGATION & SCORING ---
# Group by platform (ad source) to get summary stats
platform_summary = df.groupby('Platform').agg(
    TotalSpend=('Spend', 'sum'),
    TotalRevenue=('Revenue', 'sum'),
    TotalImpressions=('Impressions', 'sum'),
    TotalClicks=('Clicks', 'sum'),
    TotalConversions=('Conversions', 'sum')
).reset_index()

# Calculate aggregate KPIs
platform_summary['AvgROAS'] = platform_summary['TotalRevenue'] / platform_summary['TotalSpend']
platform_summary['AvgCTR'] = platform_summary['TotalClicks'] / platform_summary['TotalImpressions']
platform_summary['AvgCPC'] = platform_summary['TotalSpend'] / platform_summary['TotalClicks']
platform_summary['AvgConvRate'] = platform_summary['TotalConversions'] / platform_summary['TotalClicks']
platform_summary.fillna(0, inplace=True)

# Min-Max Scaling for each KPI (0 to 1)
for kpi in ['AvgROAS', 'AvgCTR', 'AvgConvRate', 'AvgCPC']:
    min_val = platform_summary[kpi].min()
    max_val = platform_summary[kpi].max()
    if (max_val - min_val) == 0:
        platform_summary[f'{kpi}_norm'] = 0.5 # Assign neutral score if all values are the same
        continue
    if kpi == 'AvgCPC': # Lower is better for CPC
        platform_summary[f'{kpi}_norm'] = 1 - ((platform_summary[kpi] - min_val) / (max_val - min_val))
    else: # Higher is better for others
        platform_summary[f'{kpi}_norm'] = (platform_summary[kpi] - min_val) / (max_val - min_val)

# Calculate the final weighted Performance Grade
platform_summary['PerformanceGrade'] = (
    platform_summary['AvgROAS_norm'] * norm_roas +
    platform_summary['AvgCTR_norm'] * norm_ctr +
    platform_summary['AvgCPC_norm'] * norm_cpc +
    platform_summary['AvgConvRate_norm'] * norm_conv_rate
) * 100 # Scale to 100

# --- FEATURE 1: WEIGHTED PERFORMANCE RANKING ---
st.subheader("Customizable Performance Ranking")
st.markdown("This table ranks your ad platforms based on the weighted KPI sliders you set. It directly addresses the pain point of defining 'what's working' according to your specific business goals (e.g., maximizing ROAS vs. minimizing cost).")

ranked_platforms = platform_summary[['Platform', 'PerformanceGrade', 'AvgROAS', 'AvgCTR', 'AvgCPC', 'AvgConvRate']].sort_values('PerformanceGrade', ascending=False)
st.dataframe(
    ranked_platforms.style
        .background_gradient(cmap='Greens', subset=['PerformanceGrade'])
        .format({
            'PerformanceGrade': '{:.1f}',
            'AvgROAS': '{:.2f}x',
            'AvgCTR': '{:.2%}',
            'AvgCPC': '\${:.2f}',
            'AvgConvRate': '{:.2%}'
        }),
    use_container_width=True
)

st.divider()

# --- FEATURE 2 & 3: UNIFIED OVERVIEW & SPEND EFFICIENCY ---
st.subheader("Unified Spend & Revenue Analysis")
st.markdown("Solves the 'fragmented data' problem by showing all your ad platforms in one place. The size of the bubble represents spend, while the color shows profitability (ROAS), quickly highlighting where your money is going and what return you're getting.")

fig_bubble = px.scatter(
    platform_summary,
    x="TotalSpend",
    y="TotalRevenue",
    size="TotalSpend",
    color="AvgROAS",
    hover_name="Platform",
    text="Platform",
    size_max=60,
    color_continuous_scale="RdYlGn",
    template="plotly_dark",
    title="Spend vs. Revenue by Platform (Bubble Size = Spend)"
)
fig_bubble.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_bubble, use_container_width=True)


st.divider()

# --- FEATURE 4: CREATIVE PERFORMANCE ANALYSIS ---
st.subheader("Creative Fatigue & Performance Analyzer")
st.markdown("Addresses the challenge of knowing which creatives are effective. Select a platform and KPI to see which images, videos, or text ads are your top performers, helping you make data-driven decisions on creative strategy.")

# User selection
selected_platform = st.selectbox("Select a Platform to Analyze Creatives", df['Platform'].unique())
kpi_to_analyze = st.selectbox("Select KPI to Rank Creatives By", ['ROAS', 'CTR', 'ConversionRate'])

# Filter and group by creative
creative_perf = df[df['Platform'] == selected_platform].groupby(['CreativeName', 'CreativeType']).agg(
    TotalSpend=('Spend', 'sum'),
    TotalRevenue=('Revenue', 'sum'),
    Impressions=('Impressions', 'sum'),
    Clicks=('Clicks', 'sum'),
    Conversions=('Conversions', 'sum')
).reset_index()

# Recalculate KPIs for the creative level
creative_perf['ROAS'] = creative_perf['TotalRevenue'] / creative_perf['TotalSpend']
creative_perf['CTR'] = creative_perf['Clicks'] / creative_perf['Impressions']
creative_perf['ConversionRate'] = creative_perf['Conversions'] / creative_perf['Clicks']
creative_perf.fillna(0, inplace=True)
creative_perf.replace([float('inf'), -float('inf')], 0, inplace=True)


top_creatives = creative_perf.sort_values(kpi_to_analyze, ascending=False).head(10)

# Bar chart of top creatives
fig_creatives = px.bar(
    top_creatives,
    x=kpi_to_analyze,
    y='CreativeName',
    orientation='h',
    color='CreativeType',
    template="plotly_dark",
    title=f"Top 10 Performing Creatives on {selected_platform} by {kpi_to_analyze}"
)
fig_creatives.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_creatives, use_container_width=True)


st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")