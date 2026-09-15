"""
Shared Utilities for Nifty 100 Dashboard
Handles SQLite database loading, caching, and custom sidebar navigation.
Implements dual dark/light responsive layout using CSS variables, defaulting to Light Mode.
Optimized for full width with compact spacing and Times New Roman typography.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

# Strictly modern hybrid CSS Theme supporting both Dark and Light modes natively
THEME_CSS = """
<style>
/* Hide default streamlit page list in sidebar */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Make top header transparent and compact so the settings menu stays accessible */
[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0) !important;
    color: var(--text-color) !important;
}

/* Base styling - Times New Roman override */
.stApp {
    font-family: 'Times New Roman', Georgia, Times, serif !important;
}

h1, h2, h3, h4, h5, h6, p, span, div, label, input, button, select, table, th, td {
    font-family: 'Times New Roman', Georgia, Times, serif !important;
}

/* Compact spacing and Full-Width layout (No wastage) */
.block-container {
    padding-top: 0.2rem !important;
    padding-bottom: 1.0rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 96% !important; /* Full width optimization */
}

/* Enlarge typography with clean, compact margins */
h1 {
    font-size: 38px !important;
    font-weight: 800 !important;
    margin-bottom: 12px !important;
}
h2 {
    font-size: 28px !important;
    font-weight: 700 !important;
    margin-top: 12px !important;
    margin-bottom: 8px !important;
}
h3 {
    font-size: 21px !important;
    font-weight: 600 !important;
}
p, span, label, td, th {
    font-size: 15px !important;
    line-height: 1.5 !important;
}

/* Metric tile styling - adaptive to both light and dark modes */
div[data-testid="metric-container"] {
    background-color: rgba(128, 128, 128, 0.05) !important;
    border: 1px solid rgba(128, 128, 128, 0.15) !important;
    padding: 10px 15px !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}

/* Text inside metric */
div[data-testid="metric-container"] label {
    font-size: 13px !important;
    font-weight: 600 !important;
}

div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #0969da !important;
    font-size: 26px !important;
    font-weight: bold !important;
}

/* Custom sidebar borders and links */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.15) !important;
}

[data-testid="stSidebar"] a p {
    font-size: 16px !important;
    font-weight: 500 !important;
}

/* Input boxes & selectbox styling */
.stTextInput>div>div>input, .stSelectbox>div>div>div {
    border-radius: 6px !important;
    font-size: 15px !important;
}

/* Buttons and primary color - modern green */
.stButton>button {
    background-color: #1a7f37 !important;
    color: white !important;
    border-radius: 6px !important;
    border: 1px solid rgba(27, 31, 36, 0.15) !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
    font-size: 15px !important;
    transition: background-color 0.2s ease !important;
}
.stButton>button:hover {
    background-color: #1b8c3f !important;
}

/* Custom horizontal line */
hr {
    border-top: 1px solid rgba(128, 128, 128, 0.15) !important;
    margin: 12px 0 !important;
}

/* Align table cell info and headers cleanly */
table, th, td {
    text-align: center !important;
}

/* Sidebar flexbox layout to pin footer to absolute bottom */
[data-testid="stSidebarUserContent"] {
    display: flex !important;
    flex-direction: column !important;
    height: calc(100vh - 20px) !important;
    padding-bottom: 5px !important;
}

/* Sidebar title - responsive to light/dark mode */
.sidebar-title {
    color: var(--text-color) !important;
    font-family: 'Times New Roman', Georgia, Times, serif !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    margin-bottom: 2px !important;
}

/* Sidebar footer - pinned to bottom using flexbox auto-margin */
.sidebar-footer-container {
    margin-top: auto !important;
    padding-bottom: 15px !important;
    text-align: center !important;
}

.sidebar-footer {
    font-size: 11px !important;
    font-family: 'Times New Roman', Georgia, Times, serif !important;
    color: var(--text-color) !important;
}

.sidebar-footer a {
    color: var(--text-color) !important;
    text-decoration: underline !important;
    font-weight: bold !important;
}
</style>
"""

@st.cache_data
def get_db_path() -> str:
    """Gets db path from environment or default"""
    return os.getenv("DB_PATH", "./data/nifty100.db")

@st.cache_data
def load_query(query: str) -> pd.DataFrame:
    """Loads query into dataframe and caches it"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def apply_custom_theme():
    """Applies clean premium CSS theme to page"""
    st.markdown(THEME_CSS, unsafe_allow_html=True)

def render_navigation():
    """Renders custom ordered sidebar navigation menu"""
    apply_custom_theme()
    
    st.sidebar.markdown(
        "<div style='text-align: center; padding: 15px 0;'>"
        "<h1 class='sidebar-title'>Nifty 100</h1>"
        "<p style='font-size: 13px !important; font-family: \"Times New Roman\", serif; color: #57606a; margin-top: 0;'>Financial Intelligence Platform</p>"
        "</div>"
        "<hr style='margin: 8px 0;'>",
        unsafe_allow_html=True
    )
    
    # Custom links relative to the script's directory (dashboard/) using consistent professional indicator chevrons
    st.sidebar.page_link("app.py", label="› Home / Overview")
    st.sidebar.page_link("pages/company.py", label="› Company Profile")
    st.sidebar.page_link("pages/screener.py", label="› Financial Screener")
    st.sidebar.page_link("pages/peers.py", label="› Peer Comparison")
    st.sidebar.page_link("pages/trends.py", label="› Trend Analysis")
    st.sidebar.page_link("pages/sectors.py", label="› Sector Analysis")
    st.sidebar.page_link("pages/capital.py", label="› Capital Allocation Map")
    st.sidebar.page_link("pages/documents.py", label="› Annual Reports")
    
    st.sidebar.markdown(
        "<div class='sidebar-footer-container'>"
        "<hr style='margin: 10px 0 10px 0;'>"
        "<div class='sidebar-footer'>"
        "Developed by Abhinavpreet Singh<br>"
        "<a href='https://www.linkedin.com/in/abhinavpreet-singh-arora' target='_blank'>LinkedIn</a> | "
        "<a href='https://github.com/Abhinavpreet-Singh' target='_blank'>GitHub</a>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )
