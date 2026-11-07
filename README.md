# Transaction Data Engineering Pipeline

## Project Overview

The Transaction Data Engineering Pipeline is a Python-based data processing application designed to ingest, validate, transform, and publish financial transaction data.

The main objective is to ensure that only clean and validated transaction data enters the curated database, while invalid records are isolated in a quarantine table for investigation.

The project also provides a web-based dashboard to monitor pipeline executions, analyze data quality, explore transaction records, and generate reports.

## Key Features

- **Data Ingestion:** Reads transaction and account information from CSV files.
- **Data Validation:** Checks required fields, data types, account details, currencies, duplicate records, and transaction-level consistency.
- **Data Transformation:** Processes and organizes validated transaction records.
- **Duplicate Detection:** Identifies exact duplicates and conflicting transaction records.
- **Data Quarantine:** Separates rejected records and stores their rejection reasons independently.
- **Curated Data Storage:** Publishes only accepted transactions into curated database tables.
- **Pipeline Monitoring:** Tracks execution history, accepted records, rejected records, and processing time.
- **Data Quality Monitoring:** Provides validation metrics and rejection analysis.
- **Report Generation:** Generates Markdown, JSON, and CSV reports.
- **Interactive Dashboard:** Displays transaction volume, rejection analysis, pipeline history, and data quality information.

## Project Architecture

The pipeline follows four major stages:

1. **Ingest:** Read transaction data from input CSV files.
2. **Validate:** Perform row-level and transaction-level validation.
3. **Transform:** Prepare validated records for database loading.
4. **Publish:** Store accepted records in curated tables and rejected records separately in quarantine.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline development and backend logic |
| FastAPI | Backend API development |
| SQLite | Database storage |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Frontend functionality |
| Chart.js | Data visualization |
| Pandas / CSV | Data handling and exports |
| Pytest | Testing |

## Database Design

The project uses SQLite for persistent storage.

**Curated tables:**

- `fact_txn` – Accepted transaction records.
- `fact_txn_leg` – Accepted transaction leg details.
- `dim_account` – Account information.
- `dim_account_history` – Historical account information.

**Monitoring and quarantine tables:**

- `rejected_record` – Rejected records and rejection reasons.
- `pipeline_run` – Pipeline execution history.

Rejected records are stored separately and are never published into the curated transaction tables.

## Web Application Features

The dashboard contains:

1. Pipeline Overview
2. Transaction Volume Analysis
3. Rejection Analysis
4. Curated Data Explorer
5. Quarantined Data Explorer
6. Data Quality Monitoring
7. Pipeline Execution
8. Pipeline Run History
9. Reports and Data Exports

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Check application health |
| `/api/dashboard/summary` | GET | Dashboard summary |
| `/api/dashboard/transaction-volume` | GET | Transaction volume analysis |
| `/api/dashboard/rejection-analysis` | GET | Rejection analysis |
| `/api/dashboard/run-history` | GET | Pipeline execution history |
| `/api/dashboard/run-details/{run_id}` | GET | View execution details |
| `/api/curated-data` | GET | Retrieve accepted data |
| `/api/curated-data/filters` | GET | Curated data filters |
| `/api/quarantined-data` | GET | Retrieve rejected data |
| `/api/quarantined-data/filters` | GET | Quarantine filters |
| `/api/data-quality` | GET | Data quality metrics |
| `/api/pipeline/run` | POST | Execute the pipeline |
| `/api/reports/generate` | POST | Generate reports |
| `/api/reports/download/{filename}` | GET | Download reports |

## Project Structure

```text
txn_pipeline_project/
│
├── data/
│   └── sample/
│
├── output/
│   ├── curated/
│   ├── reports/
│   ├── exports/
│   └── curated.db
│
├── tests/
│   └── test_pipeline.py
│
├── txn_pipeline/
│   ├── __main__.py
│   ├── config.py
│   ├── db.py
│   ├── generator.py
│   ├── pipeline.py
│   ├── reports.py
│   └── validators.py
│
├── web_app/
│   ├── main.py
│   └── static/
│       └── index.html
│
└── README.md
```

## Installation and Execution

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd txn_pipeline_project
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn pytest
```

### 3. Run the web application

From the project root directory:

```bash
python -m uvicorn web_app.main:app --reload
```

### 4. Open the application

- Dashboard: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 5. Run tests

```bash
python -m pytest -q
```

## Validation and Testing Results

- 27 automated tests passed.
- Validation report: 12 out of 12 checks passed.
- Database integrity check: 0 orphan transaction legs.
- Report generation and CSV downloads successfully verified.
- Dashboard and API functionality tested.

## Project Objective

The primary objective is to build a reliable transaction processing system that maintains data quality, prevents invalid records from entering curated transaction tables, and provides transparency through monitoring, quarantine management, and reporting.

## Future Enhancements

- Role-based authentication and access control.
- Automated scheduled pipeline execution.
- Advanced data quality monitoring.
- Improved pipeline performance for large datasets.
- Cloud database integration.