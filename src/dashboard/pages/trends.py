"""
Trend Analysis Page for Nifty 100 Dashboard
URL Path: /trends
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.shared import render_navigation, load_query

# Set Page Config
st.set_page_config(
    page_title="Trend Analysis - Nifty 100",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar
render_navigation()

st.title("Multi-Year Trend Analysis")
st.markdown("Analyze time-series financial metrics and YoY percentage changes.")

# 1. Select Ticker and Metric
df_companies = load_query("SELECT id, company_name FROM companies ORDER BY id")
company_options = [f"{row['id']} - {row['company_name']}" for _, row in df_companies.iterrows()]

selected_option = st.selectbox("Select Company:", company_options)
ticker = selected_option.split(" - ")[0]

metrics_list = {
    'Sales / Revenue': ('profitandloss', 'sales', 'Revenue (Cr)'),
    'Net Profit': ('profitandloss', 'net_profit', 'Net Profit (Cr)'),
    'Operating Profit': ('profitandloss', 'operating_profit', 'Operating Profit (Cr)'),
    'EPS': ('profitandloss', 'eps', 'Earnings Per Share (₹)'),
    'Total Equity': ('balancesheet', 'total_equity', 'Total Equity (Cr)'),
    'Borrowings': ('balancesheet', 'borrowings', 'Borrowings (Cr)'),
    'Total Assets': ('balancesheet', 'total_assets', 'Total Assets (Cr)'),
    'Operating Cash Flow (CFO)': ('cashflow', 'operating_activity', 'CFO (Cr)'),
    'Net Cash Flow': ('cashflow', 'net_cash_flow', 'Net Cash Flow (Cr)')
}

selected_metric_name = st.selectbox("Select Financial Metric:", list(metrics_list.keys()))
table_name, col_name, display_name = metrics_list[selected_metric_name]

# 2. Fetch Time Series Data
query_ts = f"""
    SELECT year, {col_name} as value
    FROM {table_name}
    WHERE company_id = '{ticker}'
    ORDER BY year
"""
df_ts = load_query(query_ts)

# 3. Plot Sparkline / Time-Series
if not df_ts.empty:
    st.subheader(f"{display_name} Time-Series")
    
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=df_ts['year'], y=df_ts['value'], 
        mode='lines+markers', 
        name=display_name,
        line=dict(color='#58a6ff', width=3),
        marker=dict(size=8, color='#1f77b4')
    ))
    
    fig_ts.update_layout(
        margin=dict(t=30, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman',
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
    )
    st.plotly_chart(fig_ts, use_container_width=True)
    
    # 4. Compute YoY % Change
    df_yoy = df_ts.copy()
    df_yoy['YoY Change %'] = df_yoy['value'].pct_change() * 100
    df_yoy['YoY Change (Absolute)'] = df_yoy['value'].diff()
    
    st.subheader("YoY Growth Performance")
    
    # Format table for presentation
    df_yoy_display = df_yoy.copy()
    df_yoy_display.rename(columns={
        'year': 'Year',
        'value': display_name
    }, inplace=True)
    
    df_yoy_display[display_name] = df_yoy_display[display_name].map(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "N/A")
    df_yoy_display['YoY Change %'] = df_yoy_display['YoY Change %'].map(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
    df_yoy_display['YoY Change (Absolute)'] = df_yoy_display['YoY Change (Absolute)'].map(lambda x: f"₹{x:+,.2f}" if pd.notna(x) else "N/A")
    
    st.dataframe(df_yoy_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
else:
    st.info(f"No multi-year records found for metric '{selected_metric_name}' for company '{ticker}'.")
