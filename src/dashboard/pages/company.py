"""
Company Profile Screen for Nifty 100 Dashboard
URL Path: /company
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils.shared import render_navigation, load_query

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Company Profile - Nifty 100",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar Navigation
render_navigation()

st.title("Company Profile & Financial Statements")

# Load list of tickers and names for selection
df_companies = load_query("SELECT id, company_name FROM companies ORDER BY id")
company_options = [f"{row['id']} - {row['company_name']}" for _, row in df_companies.iterrows()]

selected_option = st.selectbox("Select Ticker / Company Name:", company_options)
ticker = selected_option.split(" - ")[0]

# 1. Fetch Company Metadata
df_co = load_query(f"SELECT * FROM companies WHERE id = '{ticker}'")
df_sec = load_query(f"SELECT * FROM sectors WHERE company_id = '{ticker}'")

# Standardize display fields
about_company = df_co['about_company'].values[0] if not df_co.empty and pd.notna(df_co['about_company'].values[0]) else "No profile description available."
sector = df_sec['broad_sector'].values[0] if not df_sec.empty else (df_co['sector'].values[0] if not df_co.empty else "N/A")
sub_sector = df_sec['sub_sector'].values[0] if not df_sec.empty else (df_co['sub_sector'].values[0] if not df_co.empty else "N/A")

st.markdown(f"**Sector**: `{sector}` | **Sub-Sector**: `{sub_sector}`")
st.markdown(f"**Description**: {about_company}")

st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

# 2. Fetch latest ratios for Tiles (2024-03)
latest_year = "2024-03"
df_latest_ratios = load_query(f"SELECT * FROM financial_ratios WHERE company_id = '{ticker}' AND year = '{latest_year}'")

if not df_latest_ratios.empty:
    row_ratio = df_latest_ratios.iloc[0]
    
    # Calculate ROCE on the fly for company profile
    df_roce_raw = load_query(f"""
        SELECT 
            (pl.operating_profit - pl.depreciation) as ebit,
            (bs.equity_capital + bs.reserves + bs.borrowings) as cap_employed
        FROM profitandloss pl
        JOIN balancesheet bs ON pl.company_id = bs.company_id AND pl.year = bs.year
        WHERE pl.company_id = '{ticker}' AND pl.year = '{latest_year}'
    """)
    if not df_roce_raw.empty:
        ebit = df_roce_raw['ebit'].values[0]
        cap = df_roce_raw['cap_employed'].values[0]
        roce = (ebit / cap * 100) if (pd.notna(ebit) and pd.notna(cap) and cap > 0) else np.nan
    else:
        roce = np.nan
        
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="ROE % (FY24)", value=f"{row_ratio['return_on_equity_pct']:.2f}%" if pd.notna(row_ratio['return_on_equity_pct']) else "N/A")
    with col2:
        st.metric(label="ROCE % (FY24)", value=f"{roce:.2f}%" if pd.notna(roce) else "N/A")
    with col3:
        st.metric(label="NPM % (FY24)", value=f"{row_ratio['net_profit_margin_pct']:.2f}%" if pd.notna(row_ratio['net_profit_margin_pct']) else "N/A")
    with col4:
        st.metric(label="Debt to Equity (FY24)", value=f"{row_ratio['debt_to_equity']:.2f}" if pd.notna(row_ratio['debt_to_equity']) else "N/A")
    with col5:
        st.metric(label="Free Cash Flow (FY24)", value=f"₹{row_ratio['free_cash_flow_cr']:.2f} Cr" if pd.notna(row_ratio['free_cash_flow_cr']) else "N/A")
else:
    st.warning(f"No ratios calculated for the company '{ticker}' for financial year {latest_year}.")

st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

# 3. Qualitative Badges: Pros & Cons
st.subheader("Qualitative Analysis")
df_pc = load_query(f"SELECT pros, cons FROM prosandcons WHERE company_id = '{ticker}'")

if not df_pc.empty:
    pros_text = df_pc['pros'].values[0]
    cons_text = df_pc['cons'].values[0]
    
    col_p, col_c = st.columns(2)
    
    with col_p:
        st.markdown("<h4 style='color: #2ea043;'>Pros</h4>", unsafe_allow_html=True)
        if pd.notna(pros_text) and pros_text.strip():
            for pro in pros_text.split('\n'):
                if pro.strip():
                    st.markdown(f"- {pro.strip()}")
        else:
            st.write("No positive markers reported.")
            
    with col_c:
        st.markdown("<h4 style='color: #f85149;'>Cons</h4>", unsafe_allow_html=True)
        if pd.notna(cons_text) and cons_text.strip():
            for con in cons_text.split('\n'):
                if con.strip():
                    st.markdown(f"- {con.strip()}")
        else:
            st.write("No cautionary markers reported.")
else:
    st.info("No qualitative pros/cons recorded in database for this company.")

st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

# 4. Financial Charts
st.subheader("Financial Statements Visualization (2019-2024)")

# P&L Line Chart
st.write("**Income Statement Trends (Revenue & Profit)**")
df_pl = load_query(f"SELECT year, sales, net_profit FROM profitandloss WHERE company_id = '{ticker}' ORDER BY year")

if not df_pl.empty:
    fig_pl = go.Figure()
    fig_pl.add_trace(go.Scatter(x=df_pl['year'], y=df_pl['sales'], name='Revenue / Sales (Cr)', line=dict(color='#58a6ff', width=2.5)))
    fig_pl.add_trace(go.Scatter(x=df_pl['year'], y=df_pl['net_profit'], name='Net Profit (Cr)', line=dict(color='#2ea043', width=2.5)))
    fig_pl.update_layout(
        margin=dict(t=30, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman',
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
    )
    st.plotly_chart(fig_pl, use_container_width=True)
else:
    st.write("No P&L statements found.")

# Balance Sheet Stacked Bar Chart
st.write("**Balance Sheet Structure (Assets & Liabilities)**")
df_bs = load_query(f"SELECT year, fixed_assets, investments, cash_and_equivalents, current_assets, equity_capital, reserves, borrowings, other_liabilities FROM balancesheet WHERE company_id = '{ticker}' ORDER BY year")

if not df_bs.empty:
    # Compile assets and liabilities
    # Total Assets = fixed_assets + investments + cash_and_equivalents + current_assets (or similar)
    fig_bs = go.Figure()
    
    # We will show components
    fig_bs.add_trace(go.Bar(x=df_bs['year'], y=df_bs['fixed_assets'], name='Fixed Assets', marker_color='#1f77b4'))
    fig_bs.add_trace(go.Bar(x=df_bs['year'], y=df_bs['investments'], name='Investments', marker_color='#aec7e8'))
    fig_bs.add_trace(go.Bar(x=df_bs['year'], y=df_bs['cash_and_equivalents'], name='Cash & Equivalents', marker_color='#ff7f0e'))
    fig_bs.add_trace(go.Bar(x=df_bs['year'], y=df_bs['current_assets'], name='Current Assets', marker_color='#ffbb78'))
    
    # Let's add borrowings for comparison
    fig_bs.add_trace(go.Scatter(x=df_bs['year'], y=df_bs['borrowings'], name='Borrowings / Debt (Cr)', line=dict(color='#d62728', dash='dash')))
    
    fig_bs.update_layout(
        barmode='stack',
        margin=dict(t=30, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman',
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
    )
    st.plotly_chart(fig_bs, use_container_width=True)
else:
    st.write("No balance sheet statements found.")

# Cash Flow Chart
st.write("**Cash Flow Activity**")
df_cf = load_query(f"SELECT year, operating_activity, investing_activity, financing_activity, net_cash_flow FROM cashflow WHERE company_id = '{ticker}' ORDER BY year")

if not df_cf.empty:
    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(x=df_cf['year'], y=df_cf['operating_activity'], name='CFO (Operations)', marker_color='#2ea043'))
    fig_cf.add_trace(go.Bar(x=df_cf['year'], y=df_cf['investing_activity'], name='CFI (Investing)', marker_color='#d62728'))
    fig_cf.add_trace(go.Bar(x=df_cf['year'], y=df_cf['financing_activity'], name='CFF (Financing)', marker_color='#ff7f0e'))
    
    fig_cf.update_layout(
        barmode='group',
        margin=dict(t=30, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Times New Roman',
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.15)')
    )
    st.plotly_chart(fig_cf, use_container_width=True)
else:
    st.write("No cash flow statements found.")

# Clickable BSE PDF Links
st.subheader("Annual Reports")
df_docs = load_query(f"SELECT year, document_name, document_url FROM documents WHERE company_id = '{ticker}' ORDER BY year DESC")

if not df_docs.empty:
    for _, doc in df_docs.iterrows():
        st.markdown(f"- [{doc['year']} Annual Report]({doc['document_url']}) - {doc['document_name']}")
else:
    st.info("No annual report links found for this company.")
