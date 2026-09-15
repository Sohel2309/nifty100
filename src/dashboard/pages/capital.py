"""
Capital Allocation Map Page for Nifty 100 Dashboard
URL Path: /capital
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.shared import render_navigation, load_query

# Set Page Config
st.set_page_config(
    page_title="Capital Allocation Map - Nifty 100",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar
render_navigation()

st.title("Capital Allocation Pattern Map")
st.markdown("Treemap visualization categorizing Nifty 100 companies by their CFO, CFI, and CFF cash flow patterns.")

# 1. Load latest year (2024-03) cash flows
latest_year = "2024-03"

query_cf = f"""
    SELECT 
        c.id as Ticker,
        c.company_name as [Company Name],
        COALESCE(s.broad_sector, c.sector) as Sector,
        cf.operating_activity as CFO,
        cf.investing_activity as CFI,
        cf.financing_activity as CFF,
        m.market_cap_cr as [Market Cap (Cr)]
    FROM companies c
    JOIN cashflow cf ON c.id = cf.company_id AND cf.year = '{latest_year}'
    LEFT JOIN sectors s ON c.id = s.company_id
    LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
"""

df_cf = load_query(query_cf)

# 2. Categorize companies into 8 allocation patterns
def get_cf_pattern(row):
    cfo = "+" if row['CFO'] >= 0 else "-"
    cfi = "+" if row['CFI'] >= 0 else "-"
    cff = "+" if row['CFF'] >= 0 else "-"
    return f"[{cfo}, {cfi}, {cff}]"

# Description mapping for the 8 pattern labels
pattern_descriptions = {
    "[+, -, -]": "Standard Operations: Reinvesting CFO, repaying debt/paying dividends (Healthy)",
    "[+, -, +]": "Growth Expansion: CFO + financing used for investing (Aggressive Growth)",
    "[+, +, -]": "Cash Harvester: Divesting assets, paying down debt",
    "[+, +, +]": "High Liquidity Accumulation: Inflows from all activities",
    "[-, -, +]": "Startup Stage: Funding operations & investing through debt/equity",
    "[-, -, -]": "Cash Burn: Outflows in all activities (High Risk)",
    "[-, +, +]": "Survival Mode: Selling assets & raising cash to fund operations",
    "[-, +, -]": "Liquidation/Restructuring: CFO/CFF negative, asset sales positive"
}

df_cf['Pattern'] = df_cf.apply(get_cf_pattern, axis=1)
df_cf['Pattern Description'] = df_cf['Pattern'].map(pattern_descriptions)

# Drop any NaNs in crucial columns
df_cf_clean = df_cf.dropna(subset=['Market Cap (Cr)'])

if not df_cf_clean.empty:
    # 2b. Compute Capital Allocation Category metrics
    healthy_count = len(df_cf[df_cf['Pattern'] == '[+, -, -]'])
    growth_count = len(df_cf[df_cf['Pattern'] == '[+, -, +]'])
    risk_count = len(df_cf[df_cf['Pattern'].isin(['[-, -, -]', '[-, +, +]', '[-, +, -]'])])
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="Stable Operations [+, -, -]", value=f"{healthy_count} Companies", delta="Reinvesting CFO / Stable")
    with col_m2:
        st.metric(label="Aggressive Growth [+, -, +]", value=f"{growth_count} Companies", delta="CFO + Debt for Capex")
    with col_m3:
        st.metric(label="Distressed / Cash Burn", value=f"{risk_count} Companies", delta="Negative CFO / High Risk", delta_color="inverse")
        
    st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)
    
    st.subheader("Nifty 100 Cash Allocation Map (FY24)")
    st.markdown("Size: Market Cap (Cr) | Color: Capital Allocation Pattern Category")
    
    # 3. Plot Treemap with premium custom colors representing financial health
    custom_colors = {
        "[+, -, -]": "#1a7f37",  # Soft Green (Healthy)
        "[+, -, +]": "#0969da",  # Soft Blue (Growth)
        "[+, +, -]": "#6e7781",  # Soft Grey (Harvester)
        "[+, +, +]": "#8250df",  # Soft Purple (Liquidity)
        "[-, -, +]": "#d97706",  # Soft Amber (Startup)
        "[-, -, -]": "#cf222e",  # Soft Red (Cash Burn)
        "[-, +, +]": "#bc4c00",  # Soft Orange (Survival)
        "[-, +, -]": "#8c1d1d"   # Dark Red (Liquidation)
    }
    
    fig_sun = px.sunburst(
        df_cf_clean,
        path=['Pattern Description', 'Ticker'],
        values='Market Cap (Cr)',
        color='Pattern',
        hover_data=['Company Name', 'CFO', 'CFI', 'CFF'],
        color_discrete_map=custom_colors
    )
    fig_sun.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=650,
        paper_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman'
    )
    st.plotly_chart(fig_sun, use_container_width=True)
    
    st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 25px 0;'>", unsafe_allow_html=True)
    
    # 4. Filter List by Pattern Category - Redesigned Side-by-Side Layout
    st.subheader("Pattern Group Drill-Down")
    
    col_drill_left, col_drill_right = st.columns([5, 7])
    
    with col_drill_left:
        st.markdown("**Select Category to Inspect**")
        selected_pattern = st.selectbox("Capital Pattern Category:", list(pattern_descriptions.keys()))
        
        df_filtered = df_cf[df_cf['Pattern'] == selected_pattern].copy()
        
        # Style details as a clean container card
        st.markdown(
            f"<div style='background-color: rgba(128, 128, 128, 0.05); border: 1px solid rgba(128, 128, 128, 0.15); padding: 20px; border-radius: 6px; margin-top: 15px;'>"
            f"<h5 style='margin-top: 0; color: #0969da;'>Category Profile: {selected_pattern}</h5>"
            f"<p style='font-size: 14px; margin-bottom: 8px;'><b>Description:</b> {pattern_descriptions[selected_pattern]}</p>"
            f"<p style='font-size: 14px; margin-bottom: 0;'><b>Represented Tickers:</b> {len(df_filtered)} companies</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    with col_drill_right:
        st.markdown(f"**Member Companies ({len(df_filtered)})**")
        df_filtered_display = df_filtered[['Ticker', 'Company Name', 'Sector', 'CFO', 'CFI', 'CFF']].copy()
        for col in ['CFO', 'CFI', 'CFF']:
            df_filtered_display[col] = df_filtered_display[col].map(lambda x: f"₹{x:,.2f} Cr" if pd.notna(x) else "N/A")
            
        st.dataframe(df_filtered_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
else:
    st.info("No cash flow data available for treemap generation.")
