"""
Financial Screener Page for Nifty 100 Dashboard
URL Path: /screener
"""

import streamlit as st
import pandas as pd
import yaml

from utils.shared import render_navigation, load_query

# Set Page Config
st.set_page_config(
    page_title="Financial Screener - Nifty 100",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Custom Sidebar
render_navigation()

st.title("Financial Screener & Filter Engine")
st.markdown("Screen Nifty 100 companies based on ratios, growth, and valuations.")

# Load screener presets configuration
@st.cache_data
def load_screener_presets():
    config_path = "config/screener_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_screener_presets()
presets = config.get('presets', {})

# Load screener base dataset for latest year (2024-03)
latest_year = "2024-03"
query_screener = f"""
    SELECT 
        c.id as Ticker, 
        c.company_name as [Company Name], 
        COALESCE(s.broad_sector, c.sector) as Sector,
        r.return_on_equity_pct as [ROE %], 
        r.net_profit_margin_pct as [NPM %],
        r.operating_profit_margin_pct as [OPM %],
        r.debt_to_equity as [D/E],
        r.interest_coverage as [ICR],
        r.free_cash_flow_cr as [FCF (Cr)],
        r.asset_turnover as [Asset Turnover],
        r.dividend_payout_ratio_pct as [Dividend Payout %],
        a.revenue_5yr_cagr as [Revenue 5yr CAGR %],
        a.pat_5yr_cagr as [PAT 5yr CAGR %],
        a.revenue_3yr_cagr as [Revenue 3yr CAGR %],
        pl.sales as [Revenue / Sales (Cr)],
        m.pe_ratio as [P/E],
        m.pb_ratio as [P/B],
        m.dividend_yield as [Dividend Yield %],
        (r.free_cash_flow_cr / m.market_cap_cr * 100) as [FCF Yield %]
    FROM companies c
    LEFT JOIN sectors s ON c.id = s.company_id
    LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{latest_year}'
    LEFT JOIN analysis a ON c.id = a.company_id
    LEFT JOIN profitandloss pl ON c.id = pl.company_id AND pl.year = '{latest_year}'
    LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
"""
df_base = load_query(query_screener)

# Drop columns that are completely null, keep data clean
df_base = df_base.dropna(subset=['Ticker', 'Company Name'])

# 1. Reserve results container at the top of the page (below title)
results_container = st.container()

# Initialize default values
def_min_roe = 0.0
def_max_de = 10.0
def_min_fcf = -5000.0
def_min_rev_cagr = -50.0
def_max_pe = 200.0
def_max_pb = 50.0
def_min_div_yield = 0.0

# 2. Render Filter Controls & Presets at the bottom
st.markdown("<hr style='border-top: 1px solid rgba(128, 128, 128, 0.15); margin: 25px 0;'>", unsafe_allow_html=True)
st.subheader("Filter Controls")

preset_options = ["None"] + list(presets.keys())
selected_preset = st.selectbox("Choose a screener preset:", preset_options)
    
# If preset is selected, load thresholds
if selected_preset != "None":
    p_config = presets[selected_preset]
    filters = p_config.get('filters', {})
    
    if 'return_on_equity_pct' in filters:
        def_min_roe = float(filters['return_on_equity_pct'].get('min', 0.0))
    if 'debt_to_equity' in filters:
        def_max_de = float(filters['debt_to_equity'].get('max', 10.0))
    if 'free_cash_flow_cr' in filters:
        def_min_fcf = float(filters['free_cash_flow_cr'].get('min', -5000.0))
    if 'revenue_5yr_cagr' in filters:
        def_min_rev_cagr = float(filters['revenue_5yr_cagr'].get('min', -50.0))
    if 'pe_ratio' in filters:
        def_max_pe = float(filters['pe_ratio'].get('max', 200.0))
    if 'pb_ratio' in filters:
        def_max_pb = float(filters['pb_ratio'].get('max', 50.0))
    if 'dividend_yield' in filters:
        def_min_div_yield = float(filters['dividend_yield'].get('min', 0.0))
        
    st.info(f"Loaded filters for: **{selected_preset}**")
    
st.markdown("**Custom Threshold Filters**")

col1, col2, col3 = st.columns(3)
with col1:
    val_roe = st.slider("Min ROE %", -50.0, 100.0, def_min_roe, step=1.0)
    val_de = st.slider("Max Debt to Equity", 0.0, 10.0, def_max_de, step=0.1)
with col2:
    val_fcf = st.slider("Min FCF (Cr)", -2000.0, 10000.0, def_min_fcf, step=10.0)
    val_rev_cagr = st.slider("Min Revenue 5yr CAGR %", -20.0, 50.0, def_min_rev_cagr, step=1.0)
with col3:
    val_pe = st.slider("Max P/E Ratio", 0.0, 150.0, def_max_pe, step=1.0)
    val_pb = st.slider("Max P/B Ratio", 0.0, 30.0, def_max_pb, step=0.5)
    val_div_yield = st.slider("Min Dividend Yield %", 0.0, 10.0, def_min_div_yield, step=0.1)

# 3. Apply Filters
df_filtered = df_base.copy()

# Filter ROE
if val_roe > -50.0:
    df_filtered = df_filtered[df_filtered['ROE %'] >= val_roe]
# Filter D/E
df_filtered = df_filtered[df_filtered['D/E'] <= val_de]
# Filter FCF
if val_fcf > -2000.0:
    df_filtered = df_filtered[df_filtered['FCF (Cr)'] >= val_fcf]
# Filter Rev CAGR
if val_rev_cagr > -20.0:
    df_filtered = df_filtered[df_filtered['Revenue 5yr CAGR %'] >= val_rev_cagr]
# Filter PE
df_filtered = df_filtered[df_filtered['P/E'] <= val_pe]
# Filter PB
df_filtered = df_filtered[df_filtered['P/B'] <= val_pb]
# Filter Dividend Yield
df_filtered = df_filtered[df_filtered['Dividend Yield %'] >= val_div_yield]

# Check preset-specific custom filters
if selected_preset == "Turnaround Watch":
    df_hist = load_query("SELECT company_id, year, free_cash_flow_cr, debt_to_equity FROM financial_ratios")
    df_hist['company_id'] = df_hist['company_id'].str.strip().str.upper()
    df_hist['year'] = df_hist['year'].str.strip()
    
    valid_tickers = []
    for ticker in df_filtered['Ticker'].unique():
        co_hist = df_hist[df_hist['company_id'] == ticker].sort_values('year')
        if len(co_hist) >= 2:
            fcf_hist = co_hist['free_cash_flow_cr'].tolist()
            de_hist = co_hist['debt_to_equity'].tolist()
            
            fcf_ok = fcf_hist[-1] > fcf_hist[-2] and fcf_hist[-1] > 0
            
            if de_hist[-1] is not None and de_hist[-2] is not None:
                de_ok = de_hist[-1] < de_hist[-2]
            elif de_hist[-1] == 0.0 and de_hist[-2] is not None and de_hist[-2] > 0.0:
                de_ok = True
            else:
                de_ok = False
                
            if fcf_ok and de_ok:
                valid_tickers.append(ticker)
                
    df_filtered = df_filtered[df_filtered['Ticker'].isin(valid_tickers)]

elif selected_preset == "Debt-Free Blue Chip":
    df_filtered = df_filtered[df_filtered['Revenue / Sales (Cr)'] >= 5000.0]

# 4. Render Results into the reserved top container
with results_container:
    st.subheader(f"Filtered Results ({len(df_filtered)} companies)")
    
    if not df_filtered.empty:
        # Sort
        sort_col = "ROE %"
        if selected_preset == "Value Pick":
            sort_col = "FCF Yield %"
        elif selected_preset == "Growth Accelerator":
            sort_col = "PAT 5yr CAGR %"
        elif selected_preset == "Dividend Champion":
            sort_col = "Dividend Yield %"
        elif selected_preset == "Turnaround Watch":
            sort_col = "Revenue 3yr CAGR %"
            
        df_sorted = df_filtered.sort_values(sort_col, ascending=False)
        
        # Select columns to display
        display_cols = [
            'Ticker', 'Company Name', 'Sector', 'ROE %', 'D/E', 'FCF (Cr)', 
            'Revenue 5yr CAGR %', 'P/E', 'P/B', 'Dividend Yield %', 'FCF Yield %'
        ]
        df_sorted_display = df_sorted[display_cols].copy()
        
        # Formatting floats
        for col in ['ROE %', 'Revenue 5yr CAGR %', 'Dividend Yield %', 'FCF Yield %']:
            df_sorted_display[col] = df_sorted_display[col].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        for col in ['D/E', 'P/E', 'P/B']:
            df_sorted_display[col] = df_sorted_display[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        df_sorted_display['FCF (Cr)'] = df_sorted_display['FCF (Cr)'].map(lambda x: f"₹{x:,.2f} Cr" if pd.notna(x) else "N/A")
        
        st.dataframe(df_sorted_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
        
        # Export options
        csv = df_sorted.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Results as CSV",
            data=csv,
            file_name='screener_results.csv',
            mime='text/csv'
        )
    else:
        st.info("No companies match the selected criteria.")
