import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------------------------------------
# Page configuration
st.set_page_config(page_title="ESG & Financial Dashboard", layout="wide")
st.title("🌍 ESG & Financial Performance Dashboard")
st.markdown("Analyse the relationship between **ESG scores** and **financial metrics** across industries and regions.")

# ------------------------------------------------------------------------------
# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("esg_analysis_full_data.csv")
    # Ensure numeric columns
    numeric_cols = ['Revenue', 'ProfitMargin', 'MarketCap', 'GrowthRate',
                    'ESG_Overall', 'ESG_Environmental', 'ESG_Social', 'ESG_Governance',
                    'CarbonEmissions', 'WaterUsage', 'EnergyConsumption']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# ------------------------------------------------------------------------------
# Sidebar filters
st.sidebar.header("Filters")

years = sorted(df['Year'].unique())
year_range = st.sidebar.slider("Select year range",
                                min_value=min(years), max_value=max(years),
                                value=(min(years), max(years)), step=1)

industries = sorted(df['Industry'].unique())
selected_industries = st.sidebar.multiselect("Industry", industries, default=industries)

regions = sorted(df['Region'].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

filtered_df = df[(df['Year'].between(year_range[0], year_range[1])) &
                 (df['Industry'].isin(selected_industries)) &
                 (df['Region'].isin(selected_regions))]

if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust your filters.")
    st.stop()

# ------------------------------------------------------------------------------
# Key metrics
st.header("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Average ESG Overall Score", f"{filtered_df['ESG_Overall'].mean():.1f}")
with col2:
    st.metric("Average Profit Margin (%)", f"{filtered_df['ProfitMargin'].mean():.1f}")
with col3:
    st.metric("Average Revenue (M)", f"{filtered_df['Revenue'].mean():,.0f}")
with col4:
    st.metric("Number of Companies", f"{filtered_df['CompanyID'].nunique()}")

# ------------------------------------------------------------------------------
# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 ESG Trends", "💼 Financial Metrics", "🔍 Correlations", "🌍 Geographic View"
])

# ------------------------------------------------------------------------------
# Tab 1: ESG Trends
with tab1:
    st.subheader("ESG Score Evolution Over Time")
    yearly_esg = filtered_df.groupby(['Year', 'Industry'])[['ESG_Overall', 'ESG_Environmental', 'ESG_Social', 'ESG_Governance']].mean().reset_index()

    fig1 = px.line(yearly_esg, x='Year', y='ESG_Overall', color='Industry',
                   title='Average ESG Overall Score by Industry',
                   labels={'ESG_Overall': 'ESG Score'})
    st.plotly_chart(fig1, use_container_width=True)

    pillars = ['ESG_Environmental', 'ESG_Social', 'ESG_Governance']
    fig2 = px.box(filtered_df.melt(id_vars=['Industry'], value_vars=pillars,
                                   var_name='Pillar', value_name='Score'),
                  x='Pillar', y='Score', color='Industry',
                  title='Distribution of ESG Pillar Scores')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------------------------
# Tab 2: Financial Metrics
with tab2:
    st.subheader("Profit Margin vs. Revenue")
    fig3 = px.scatter(filtered_df, x='Revenue', y='ProfitMargin',
                      color='ESG_Overall', size='MarketCap',
                      hover_data=['CompanyName', 'Industry', 'Year'],
                      title='Profit Margin vs. Revenue (size = Market Cap)',
                      labels={'ProfitMargin': 'Profit Margin (%)', 'Revenue': 'Revenue (M)'})
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Financial Performance Over Time")
    fin_metrics = ['Revenue', 'ProfitMargin', 'GrowthRate', 'MarketCap']
    for metric in fin_metrics:
        yearly_metric = filtered_df.groupby(['Year', 'Industry'])[metric].mean().reset_index()
        fig = px.line(yearly_metric, x='Year', y=metric, color='Industry',
                      title=f'Average {metric} by Industry')
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# Tab 3: Correlations
with tab3:
    st.subheader("Correlation Heatmap")
    corr_cols = ['ESG_Overall', 'ProfitMargin', 'GrowthRate', 'Revenue', 'MarketCap',
                 'CarbonEmissions', 'WaterUsage', 'EnergyConsumption']
    corr_matrix = filtered_df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
    ax.set_title("Correlation between ESG and Financial Indicators")
    st.pyplot(fig)

    st.subheader("ESG Score vs. Profit Margin by Industry")
    # Removed trendline='ols' to avoid fitting errors with small groups
    fig5 = px.scatter(filtered_df, x='ESG_Overall', y='ProfitMargin',
                      color='Industry', facet_col='Industry',
                      title='ESG Overall vs Profit Margin (faceted by Industry)')
    st.plotly_chart(fig5, use_container_width=True)

# ------------------------------------------------------------------------------
# Tab 4: Geographic View
with tab4:
    st.subheader("Regional Performance")
    region_stats = filtered_df.groupby('Region')[['ESG_Overall', 'ProfitMargin', 'Revenue']].mean().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig6 = px.bar(region_stats, x='Region', y='ESG_Overall',
                      title='Average ESG Score by Region', color='Region')
        st.plotly_chart(fig6, use_container_width=True)
    with col2:
        fig7 = px.bar(region_stats, x='Region', y='ProfitMargin',
                      title='Average Profit Margin by Region', color='Region')
        st.plotly_chart(fig7, use_container_width=True)

    region_counts = filtered_df.groupby('Region')['CompanyID'].nunique().reset_index(name='Number of Companies')
    fig8 = px.bar(region_counts, x='Region', y='Number of Companies',
                  title='Number of Companies per Region', color='Region')
    st.plotly_chart(fig8, use_container_width=True)

# ------------------------------------------------------------------------------
st.markdown("---")
st.caption("Data source: ESG & Financial Performance Dataset (2016–2025). Dashboard created with Streamlit.")
