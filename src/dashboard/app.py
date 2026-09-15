"""
Main Entry Point & Home / Overview Screen for Nifty 100 Dashboard
URL Path: /
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.shared import render_navigation, load_query

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Nifty 100 Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar Navigation
render_navigation()

# Description
st.markdown("<p style='font-size: 18px !important; font-weight: bold; margin-top: 5px; margin-bottom: 20px;'>A comprehensive intelligence platform analyzing performance, ratios, and valuation for Nifty 100 companies.</p>", unsafe_allow_html=True)

# 1. Load Data for Overview
latest_year = "2024-03"

# Query sectors and join company details, ratios, and market cap
query_summary = f"""
    SELECT 
        c.id as company_id, 
        c.company_name, 
        COALESCE(s.broad_sector, c.sector) as broad_sector,
        r.return_on_equity_pct, 
        m.pe_ratio, 
        m.market_cap_cr
    FROM companies c
    LEFT JOIN sectors s ON c.id = s.company_id
    LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{latest_year}'
    LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
"""
df_data = load_query(query_summary)

# 2. Compute Summary Metrics
total_companies = len(df_data)
median_roe = df_data['return_on_equity_pct'].median()
median_pe = df_data['pe_ratio'].median()
total_mcap_lakh_cr = df_data['market_cap_cr'].sum() / 100000.0  # Convert Cr to Lakh Cr

# Display KPIs in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Companies", value=f"{total_companies}")
with col2:
    st.metric(label="Median ROE % (FY24)", value=f"{median_roe:.2f}%" if pd.notna(median_roe) else "N/A")
with col3:
    st.metric(label="Median P/E (FY24)", value=f"{median_pe:.2f}" if pd.notna(median_pe) else "N/A")
with col4:
    st.metric(label="Total Market Cap (Lakh Cr)", value=f"₹{total_mcap_lakh_cr:.2f} L Cr")

st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

# 3. Sector Distribution (2-column layout for better aspect ratio compatibility)
st.subheader("Sector Breakdown")

col_table, col_chart = st.columns([5, 7])

# Sector counts table preparation
sector_counts = df_data['broad_sector'].value_counts().reset_index()
sector_counts.columns = ['Sector', 'Company Count']
sector_counts['Weight %'] = (sector_counts['Company Count'] / len(df_data) * 100).map(lambda x: f"{x:.2f}%")

with col_table:
    st.markdown("**Sector Representation Summary**")
    st.dataframe(sector_counts.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)

with col_chart:
    fig_donut = px.pie(
        sector_counts, 
        values='Company Count', 
        names='Sector', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_donut.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman',
        showlegend=True
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

# 4. Companies Directory Table
st.subheader("Nifty 100 Universe")

# Format columns for display
df_display = df_data.copy()
df_display.rename(columns={
    'company_id': 'Ticker',
    'company_name': 'Company Name',
    'broad_sector': 'Sector',
    'return_on_equity_pct': 'ROE %',
    'pe_ratio': 'P/E Ratio',
    'market_cap_cr': 'Market Cap (Cr)'
}, inplace=True)

# Format floats
for col in ['ROE %', 'P/E Ratio']:
    df_display[col] = df_display[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
df_display['Market Cap (Cr)'] = df_display['Market Cap (Cr)'].map(lambda x: f"₹{x:,.1f} Cr" if pd.notna(x) else "N/A")

# Text search input for filtering table
search_term = st.text_input("Search Company Name or Ticker:", "")
if search_term:
    df_display = df_display[
        df_display['Ticker'].str.contains(search_term, case=False) |
        df_display['Company Name'].str.contains(search_term, case=False)
    ]

st.dataframe(df_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
