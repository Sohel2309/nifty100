"""
Peer Comparison Page for Nifty 100 Dashboard
URL Path: /peers
"""

import os
import streamlit as st
import pandas as pd
from PIL import Image

from utils.shared import render_navigation, load_query

# Set Page Config
st.set_page_config(
    page_title="Peer Comparison - Nifty 100",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar
render_navigation()

st.title("Peer Comparison Engine")
st.markdown("Compare Nifty 100 companies with their peers and benchmarks.")

# 1. Select Peer Group
df_groups = load_query("SELECT DISTINCT peer_group_name FROM peer_groups ORDER BY peer_group_name")
peer_group_options = df_groups['peer_group_name'].tolist()

selected_group = st.selectbox("Select Peer Group:", peer_group_options)

# 2. Load side-by-side table for selected group (latest year 2024-03)
latest_year = "2024-03"

query_peers = f"""
    SELECT 
        c.id as Ticker, 
        c.company_name as [Company Name],
        pg.is_benchmark as [Is Benchmark],
        r.return_on_equity_pct as [ROE %],
        r.debt_to_equity as [D/E],
        r.net_profit_margin_pct as [NPM %],
        r.operating_profit_margin_pct as [OPM %],
        r.interest_coverage as [ICR],
        r.free_cash_flow_cr as [FCF (Cr)],
        r.asset_turnover as [Asset Turnover],
        r.earnings_per_share as [EPS (₹)],
        r.book_value_per_share as [Book Value (₹)],
        r.dividend_payout_ratio_pct as [Div Payout %],
        a.revenue_5yr_cagr as [Revenue 5yr CAGR %],
        a.pat_5yr_cagr as [PAT 5yr CAGR %],
        m.pe_ratio as [P/E],
        m.pb_ratio as [P/B],
        m.ev_ebitda as [EV/EBITDA],
        m.dividend_yield as [Dividend Yield %],
        pp.best_in_class as [Best in Class],
        pp.watch_list as [Watch List]
    FROM peer_groups pg
    JOIN companies c ON pg.company_id = c.id
    LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{latest_year}'
    LEFT JOIN analysis a ON c.id = a.company_id
    LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
    LEFT JOIN peer_percentiles pp ON c.id = pp.company_id AND pp.year = '{latest_year}'
    WHERE pg.peer_group_name = '{selected_group}'
    ORDER BY pg.is_benchmark DESC, r.return_on_equity_pct DESC
"""

df_peers = load_query(query_peers)

# 3. Render side-by-side table
st.subheader(f"Comparison Table: {selected_group}")

# Copy for formatting
df_peers_display = df_peers.copy()

# Add badges for Best in Class and Watch List
df_peers_display['Badges'] = df_peers_display.apply(
    lambda r: ("Best in Class" if r['Best in Class'] == 1 else "") + 
              ("Watch List" if r['Watch List'] == 1 else ""),
    axis=1
)

df_peers_display['Is Benchmark'] = df_peers_display['Is Benchmark'].map(lambda x: "Yes" if x == 1 else "No")

# Drop raw flag columns
df_peers_display.drop(columns=['Best in Class', 'Watch List'], inplace=True, errors='ignore')

# Format columns
cols_to_format_pct = ['ROE %', 'NPM %', 'OPM %', 'Div Payout %', 'Revenue 5yr CAGR %', 'PAT 5yr CAGR %', 'Dividend Yield %']
cols_to_format_float = ['D/E', 'ICR', 'Asset Turnover', 'EPS (₹)', 'Book Value (₹)', 'P/E', 'P/B', 'EV/EBITDA']

for col in cols_to_format_pct:
    if col in df_peers_display.columns:
        df_peers_display[col] = df_peers_display[col].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
for col in cols_to_format_float:
    if col in df_peers_display.columns:
        df_peers_display[col] = df_peers_display[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        
if 'FCF (Cr)' in df_peers_display.columns:
    df_peers_display['FCF (Cr)'] = df_peers_display['FCF (Cr)'].map(lambda x: f"₹{x:,.2f} Cr" if pd.notna(x) else "N/A")

st.dataframe(df_peers_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)

st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

# 4. Radar Chart Display
st.subheader("Radar Chart Performance Comparison")
st.markdown("Shows company performance percentiles against the peer average and group benchmark.")

# Select company from the peer group
company_options = df_peers['Ticker'].tolist()
selected_co = st.selectbox("Select Company for Radar Chart:", company_options)

# Load pre-computed PNG
chart_path = f"reports/radar_charts/{selected_co}_radar.png"
if os.path.exists(chart_path):
    img = Image.open(chart_path)
    # Use columns to center image
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.image(img, caption=f"8-Axis Polar Radar Chart for {selected_co} (Peer Group: {selected_group})", use_column_width=True)
else:
    st.info(f"No pre-computed radar chart found for company {selected_co} at path `{chart_path}`.")
