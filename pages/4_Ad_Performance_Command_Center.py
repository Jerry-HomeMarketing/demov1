# pages/4_🎯_Ad_Performance_Command_Center.py

import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ad Performance Command Center", page_icon="🎯", layout="wide")

# --- CSS & DATA ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

@st.cache_data
def load__data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    data['ROAS'] = (data['Revenue'] / data['Spend']).replace([float('inf'), -float('inf')], 0).fillna(0)
    data['CTR'] = (data['Clicks'] / data['Impressions']).fillna(0)
    data['CPC'] = (data['Spend'] / data['Clicks']).replace([float('inf'), -float('inf')], 0).fillna(0)
    data['ConversionRate'] = (data['Conversions'] / data['Clicks']).replace([float('inf'), -float('inf')], 0).fillna(0)
    return data
try:
    df = load_data("data/ad_performance_data.csv")
except FileNotFoundError:
    st.error("Data file not found. Please run 'generate_ad_data.py' first.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Performance Grade Tuner")
weight_roas = st.sidebar.slider("ROAS Weight", 0, 100, 50)
weight_ctr = st.sidebar.slider("CTR Weight", 0, 100, 15)
weight_cpc = st.sidebar.slider("CPC Weight (lower is better)", 0, 100, 20)
weight_conv_rate = st.sidebar.slider("Conversion Rate Weight", 0, 100, 15)
total_weight = weight_roas + weight_ctr + weight_cpc + weight_conv_rate
if total_weight == 0: total_weight = 1
st.sidebar.markdown("---")
st.sidebar.info("This is a demo dashboard built by Home Marketing & Consulting.")

# --- MAIN LAYOUT ---
st.title("🎯 Ad Performance Command Center")
st.markdown("### A Unified View to Conquer Ad Complexity")

# --- Ranking & Analysis Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Customizable Performance Ranking & Spend Analysis")
platform_summary = df.groupby('Platform').agg(TotalSpend=('Spend', 'sum'), TotalRevenue=('Revenue', 'sum'), TotalImpressions=('Impressions', 'sum'), TotalClicks=('Clicks', 'sum'), TotalConversions=('Conversions', 'sum')).reset_index()
platform_summary['AvgROAS'] = (platform_summary['TotalRevenue'] / platform_summary['TotalSpend']).fillna(0)
platform_summary['AvgCTR'] = (platform_summary['TotalClicks'] / platform_summary['TotalImpressions']).fillna(0)
platform_summary['AvgCPC'] = (platform_summary['TotalSpend'] / platform_summary['TotalClicks']).fillna(0)
platform_summary['AvgConvRate'] = (platform_summary['TotalConversions'] / platform_summary['TotalClicks']).fillna(0)

for kpi in ['AvgROAS', 'AvgCTR', 'AvgConvRate', 'AvgCPC']:
    min_val, max_val = platform_summary[kpi].min(), platform_summary[kpi].max()
    if (max_val - min_val) == 0: platform_summary[f'{kpi}_norm'] = 0.5; continue
    if kpi == 'AvgCPC': platform_summary[f'{kpi}_norm'] = 1 - ((platform_summary[kpi] - min_val) / (max_val - min_val))
    else: platform_summary[f'{kpi}_norm'] = (platform_summary[kpi] - min_val) / (max_val - min_val)

platform_summary['PerformanceGrade'] = ((platform_summary['AvgROAS_norm'] * (weight_roas/total_weight)) + (platform_summary['AvgCTR_norm'] * (weight_ctr/total_weight)) + (platform_summary['AvgCPC_norm'] * (weight_cpc/total_weight)) + (platform_summary['AvgConvRate_norm'] * (weight_conv_rate/total_weight))) * 100

col1, col2 = st.columns((4, 6))
with col1:
    ranked_platforms = platform_summary[['Platform', 'PerformanceGrade', 'AvgROAS', 'AvgCPC']].sort_values('PerformanceGrade', ascending=False)
    st.dataframe(ranked_platforms.style.background_gradient(cmap='Greens', subset=['PerformanceGrade']).format({'PerformanceGrade': '{:.1f}', 'AvgROAS': '{:.2f}x', 'AvgCPC': '\${:.2f}'}), use_container_width=True)
with col2:
    fig_bubble = px.scatter(platform_summary, x="TotalSpend", y="TotalRevenue", size="TotalSpend", color="AvgROAS", hover_name="Platform", text="Platform", size_max=60, color_continuous_scale="RdYlGn", template="plotly_dark")
    fig_bubble.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bubble, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Creative Analysis Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Creative Fatigue & Performance Analyzer")
selected_platform = st.selectbox("Select a Platform to Analyze Creatives", df['Platform'].unique())
kpi_to_analyze = st.selectbox("Select KPI to Rank Creatives By", ['ROAS', 'CTR', 'ConversionRate'])
creative_perf = df[df['Platform'] == selected_platform].groupby(['CreativeName', 'CreativeType']).agg(TotalSpend=('Spend', 'sum'), TotalRevenue=('Revenue', 'sum'), Impressions=('Impressions', 'sum'), Clicks=('Clicks', 'sum'), Conversions=('Conversions', 'sum')).reset_index()
creative_perf['ROAS'] = (creative_perf['TotalRevenue'] / creative_perf['TotalSpend']).replace([float('inf'), -float('inf')], 0).fillna(0)
creative_perf['CTR'] = (creative_perf['Clicks'] / creative_perf['Impressions']).fillna(0)
creative_perf['ConversionRate'] = (creative_perf['Conversions'] / creative_perf['Clicks']).replace([float('inf'), -float('inf')], 0).fillna(0)
top_creatives = creative_perf.sort_values(kpi_to_analyze, ascending=False).head(10)
fig_creatives = px.bar(top_creatives, x=kpi_to_analyze, y='CreativeName', orientation='h', color='CreativeType', template="plotly_dark")
fig_creatives.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_creatives, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
