# Nifty 100 Financial Intelligence Dashboard User Guide

Welcome to the Nifty 100 Financial Intelligence Dashboard! This web application is built using Python, SQLite, and Streamlit, providing interactive charting and multi-criteria stock screening for all 92 Nifty 100 companies.

---

## 1. Installation & Running Locally

Ensure that you have activated the virtual environment and installed the dependencies listed in `requirements.txt`.

### Step 1: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Start Streamlit App
Run the following command from the root directory (`E:\NIFTY100`):
```powershell
streamlit run src/dashboard/app.py
```

Streamlit will automatically build the server and open your default web browser to the dashboard at:
**`http://localhost:8501`**

---

## 2. Navigating the 8 Screens

The platform is structured with native Streamlit multi-page routing mapping directly to clean URL paths. Use the custom-ordered navigation links in the sidebar to move between screens:

1. **🏠 Home / Overview (`/`)**:
   - Provides summary KPIs (Total Companies, Median P/E, Average ROE %, Total Market Cap) for Nifty 100.
   - Shows an interactive sector breakdown donut chart.
   - Features a searchable, sortable directory of the 92 companies.

2. **🏢 Company Profile (`/company`)**:
   - Pick any company via the dropdown selection.
   - View financial health KPI cards (ROE, ROCE, NPM, Debt-to-Equity, FCF) and qualitative **Pros & Cons** badges.
   - Analyze P&L trends, stacked Balance Sheet assets, and Cash Flow activity grouped bar charts.
   - Access direct links to BSE Annual Report PDF filings.

3. **🔍 Financial Screener (`/screener`)**:
   - Slide interactive sliders to filter by ROE, D/E, FCF, CAGR, P/E, and P/B.
   - Select from 6 preset analyst screener configurations (e.g. Quality Compounder, Value Pick, Turnaround Watch) to auto-fill thresholds.
   - Export results to CSV.

4. **👥 Peer Comparison (`/peers`)**:
   - Compare companies side-by-side within their peer group.
   - View composite ranks, **Best in Class** badges, and **Watch List** flags.
   - View the 8-axis polar radar chart comparing the company's percentiles against peer group averages and benchmark companies.

5. **📈 Trend Analysis (`/trends`)**:
   - Select a company and a financial metric to view a multi-year line chart.
   - Inspect YoY absolute and percentage change tables.

6. **📊 Sector Analysis (`/sectors`)**:
   - Select a broad sector to view a bubble chart plotting Revenue vs ROE (sized by Market Cap, colored by Sub-sector).
   - Inspect statistical outliers (e.g. >2σ deviation or bottom decile ROE).

7. **🗺️ Capital Allocation Map (`/capital`)**:
   - Visualizes Nifty 100 cash flow allocation profiles using a Plotly treemap based on CFO, CFI, and CFF cash flow sign patterns.
   - Click/drill down into categories (such as Standard Operations or Cash Burn) to view members.

8. **📄 Annual Reports (`/documents`)**:
   - Pick a company to view its annual report filngs.
   - Click the green button to open BSE PDF document links.

---

## 3. Valuation Summary Reports

The platform generates and exports offline spreadsheets:
- **`output/valuation_summary.xlsx`**: Excel workbook containing tabs for P/E Trends, EV/EBITDA comparisons, Dividend Yield Ranks, FCF Yield Ranks, and Overvaluation flags.
- **`output/valuation_flags.csv`**: Flat table flagging companies as `Caution` (P/E > 1.5× sector median) or `Discount` (P/E < 0.7× sector median) for quick portfolio screenings.
