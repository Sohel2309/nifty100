"""
Sector Analysis Page for Nifty 100 Dashboard
URL Path: /sectors
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from utils.shared import render_navigation, load_query

# Set Page Config
st.set_page_config(
    page_title="Sector Analysis - Nifty 100",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar
render_navigation()

st.title("Sector Performance Analysis")
st.markdown("Compare sector-relative performance metrics and flag statistical outliers.")

# 1. Sector Selection
df_sectors = load_query("SELECT DISTINCT broad_sector FROM sectors WHERE broad_sector IS NOT NULL ORDER BY broad_sector")
sector_options = df_sectors['broad_sector'].tolist()

selected_sector = st.selectbox("Select Sector:", sector_options)

# 2. Load Sector Data (latest year 2024-03)
latest_year = "2024-03"

query_sector_data = f"""
    SELECT 
        c.id as Ticker,
        c.company_name as [Company Name],
        s.sub_sector as [Sub Sector],
        pl.sales as [Revenue (Cr)],
        r.return_on_equity_pct as [ROE %],
        m.market_cap_cr as [Market Cap (Cr)],
        m.pe_ratio as [P/E Ratio]
    FROM companies c
    JOIN sectors s ON c.id = s.company_id
    LEFT JOIN profitandloss pl ON c.id = pl.company_id AND pl.year = '{latest_year}'
    LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{latest_year}'
    LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
    WHERE s.broad_sector = '{selected_sector}'
"""

df_sec_data = load_query(query_sector_data)

# Drop incomplete records
df_sec_data = df_sec_data.dropna(subset=['Revenue (Cr)', 'ROE %', 'Market Cap (Cr)'])

if not df_sec_data.empty:
    st.subheader(f"Bubble Chart - {selected_sector} (FY24)")
    st.markdown("X-Axis: Revenue (Cr) | Y-Axis: ROE % | Size: Market Cap (Cr) | Color: Sub-Sector")
    
    # 3. Plot bubble chart
    fig_bubble = px.scatter(
        df_sec_data,
        x='Revenue (Cr)',
        y='ROE %',
        size='Market Cap (Cr)',
        color='Sub Sector',
        hover_name='Company Name',
        text='Ticker',
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig_bubble.update_layout(
        margin=dict(t=30, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman',
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
    )
    fig_bubble.update_traces(textposition='top center')
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)
    
    # 4. Outlier Detection (>2 std deviations or bottom decile)
    st.subheader("Sector Outlier Detection")
    st.markdown("Flagging companies with exceptionally high/low valuations or returns relative to their sector averages.")
    
    # Compute sector mean/std dev for ROE and P/E
    roe_mean = df_sec_data['ROE %'].mean()
    roe_std = df_sec_data['ROE %'].std()
    
    # Check for P/E
    pe_mean = df_sec_data['P/E Ratio'].mean()
    pe_std = df_sec_data['P/E Ratio'].std()
    
    outliers = []
    
    # Check bottom decile (P10) for ROE
    roe_p10 = df_sec_data['ROE %'].quantile(0.10)
    
    for _, row in df_sec_data.iterrows():
        ticker = row['Ticker']
        name = row['Company Name']
        roe = row['ROE %']
        pe = row['P/E Ratio']
        
        reason = []
        # ROE > 2 sigma
        if pd.notna(roe_std) and roe_std > 0:
            if roe > roe_mean + 2 * roe_std:
                reason.append(f"Outstanding ROE ({roe:.1f}%) > 2σ sector limit")
            elif roe < roe_mean - 2 * roe_std:
                reason.append(f"Severely low ROE ({roe:.1f}%) < 2σ sector limit")
                
        # ROE in bottom decile
        if roe <= roe_p10:
            reason.append(f"ROE ({roe:.1f}%) in bottom decile of sector")
            
        # P/E > 2 sigma
        if pd.notna(pe) and pd.notna(pe_std) and pe_std > 0:
            if pe > pe_mean + 2 * pe_std:
                reason.append(f"Highly overvalued P/E ({pe:.1f}) > 2σ sector limit")
                
        if reason:
            outliers.append({
                'Ticker': ticker,
                'Company Name': name,
                'ROE %': f"{roe:.2f}%",
                'P/E Ratio': f"{pe:.2f}" if pd.notna(pe) else "N/A",
                'Outlier Flags': " & ".join(reason)
            })
            
    if outliers:
        df_outliers = pd.DataFrame(outliers)
        st.dataframe(df_outliers.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
    else:
        st.write("No statistical outliers detected in this sector.")
else:
    st.info("No financial data available for the selected sector.")
