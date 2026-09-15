# Nifty 100 Financial Intelligence Platform

Fundamental analytics for India's largest listed companies. Ingests raw financial statements, validates them through 16 data-quality rules, computes 50+ KPIs, and serves insights through a Streamlit dashboard, FastAPI REST layer, and automated PDF reports.

**92 companies | 11 sectors | 10+ years of history | 114 passing tests**

---

## What it does

| Layer | Capability |
|-------|------------|
| Data | Excel-to-SQLite ETL with audit trails and FK-enforced schema |
| Analytics | Ratios, CAGR, peer percentiles, screener, clustering, cash-flow patterns |
| Interface | 8-page Streamlit dashboard with interactive Plotly charts |
| API | 16 REST endpoints with OpenAPI docs |
| Reports | Per-company tearsheets, sector PDFs, valuation exports |

---

## Quick start

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Build the database
python -m src.db.loader

# Optional: generate PDF reports
python -m src.analytics.pdf_generator

# Launch services
python -m uvicorn src.api.main:app --port 8000 --reload
python -m streamlit run src/dashboard/app.py
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

---

## Architecture

```
Excel datasets (12 files)
        |
        v
  ETL + 16 DQ rules  -->  load_audit.csv
        |
        v
  SQLite (nifty100.db)  -- 12 tables, 2 views
        |
   +----+----+----+
   v    v    v    v
Ratios  Peer  Screener  NLP / Clustering
engine  engine  engine    modules
   |    |    |    |
   +----+----+----+
        |
   +----+----+
   v         v
Streamlit   FastAPI
Dashboard   REST API
        |
        v
  PDF / Excel / CSV outputs
```

---

## Project layout

```
config/          Screener presets and thresholds
data/            Source Excel files and nifty100.db
src/
  db/            Schema, loader, persistence
  etl/           Excel ingestion and DQ validation
  analytics/     Ratios, CAGR, peers, screener, PDF, NLP, clustering
  api/           FastAPI endpoints
  dashboard/     Streamlit app and pages
tests/           Unit and integration tests
output/          Audits, exports, cluster labels, valuation flags
reports/         Tearsheets, sector reports, radar charts
```

---

## Dashboard pages

| Page | Route | Purpose |
|------|-------|---------|
| Home | `/` | Universe KPIs, sector breakdown, searchable company directory |
| Company Profile | `/company` | KPIs, pros/cons, P&L/BS/CF charts, annual report links |
| Financial Screener | `/screener` | 6 presets, custom filters, CSV export |
| Peer Comparison | `/peers` | Side-by-side metrics, best-in-class badges, radar charts |
| Trend Analysis | `/trends` | Multi-year metrics with YoY change tables |
| Sector Analysis | `/sectors` | Bubble charts, statistical outlier detection |
| Capital Allocation | `/capital` | Cash-flow pattern treemap and drill-down |
| Annual Reports | `/documents` | BSE filing links by company and year |

---

## API endpoints

`GET /api/v1/companies` | `GET /api/v1/companies/{ticker}` | `GET /api/v1/companies/{ticker}/pl|bs|cashflow|ratios|tearsheet|documents|peers/compare`

`GET /api/v1/screener` | `GET /api/v1/sectors` | `GET /api/v1/sectors/{sector}/companies`

`GET /api/v1/peers/{group_name}` | `GET /api/v1/market-cap/{ticker}` | `GET /api/v1/portfolio/stats` | `GET /api/v1/health`

Full interactive reference: `/docs`

---

## Testing

```powershell
python -m pytest -v
```

---

## Tech stack

Python 3.10+ | pandas | SQLite | FastAPI | Streamlit | Plotly | scikit-learn | ReportLab | NLTK | pytest

---

Developed by Abhinavpreet Singh
