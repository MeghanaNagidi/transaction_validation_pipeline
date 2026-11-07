
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
from fastapi.responses import HTMLResponse
import sqlite3
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from txn_pipeline.config import Config
from txn_pipeline.pipeline import run_pipeline
from txn_pipeline.reports import write_report, export_csv


# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Existing SQLite database
DB_PATH = PROJECT_DIR / "output" / "curated.db"

# Static files directory
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Reports and exports directories
REPORTS_DIR = PROJECT_DIR / "output" / "reports"
EXPORTS_DIR = PROJECT_DIR / "output" / "exports"


# Create the FastAPI application
app = FastAPI(
    title="Transaction Data Engineering Dashboard",
    description="Monitor and explore the transaction data pipeline.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(STATIC_DIR / "index.html")


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "running",
        "database": str(DB_PATH),
        "database_exists": DB_PATH.exists(),
    }


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------


@app.get("/api/dashboard/summary")
def dashboard_summary():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        result = conn.execute("""
            SELECT
                COUNT(*) AS total_runs,
                COALESCE(SUM(rows_read), 0) AS total_rows,
                COALESCE(SUM(rows_accepted), 0) AS accepted_rows,
                COALESCE(SUM(rows_rejected), 0) AS rejected_rows,
                COALESCE(SUM(duration_seconds), 0) AS total_duration,
                (SELECT COUNT(*) FROM rejected_record) AS quarantined_records
            FROM pipeline_run
            WHERE status IN ('SUCCESS', 'EMPTY_INPUT')
        """).fetchone()

        total_rows = result["total_rows"]
        accepted_rows = result["accepted_rows"]
        rejected_rows = result["rejected_rows"]

        success_rate = (
            accepted_rows / total_rows * 100
            if total_rows > 0 else 0
        )

        return {
            "total_runs": result["total_runs"],
            "total_transactions_processed": total_rows,
            "accepted_transactions": accepted_rows,
            "rejected_transactions": rejected_rows,
            "quarantined_records": result["quarantined_records"],
            "data_quality_success_rate": round(success_rate, 2),
            "total_execution_time_seconds": round(
                result["total_duration"], 2
            )
        }

    finally:
        conn.close()


# --------------------------------------------------
# TRANSACTION VOLUME
# --------------------------------------------------

@app.get("/api/dashboard/transaction-volume")
def transaction_volume():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                run_id,
                started_at,
                rows_accepted,
                rows_rejected
            FROM pipeline_run
            ORDER BY started_at ASC
        """)

        results = cursor.fetchall()

        return [
            {
                "run_id": row["run_id"],
                "started_at": row["started_at"],
                "accepted": row["rows_accepted"] or 0,
                "rejected": row["rows_rejected"] or 0
            }
            for row in results
        ]

    finally:
        conn.close()


# --------------------------------------------------
# REJECTION ANALYSIS
# --------------------------------------------------

@app.get("/api/dashboard/rejection-analysis")
def rejection_analysis():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                reason_code,
                COUNT(*) AS total_rejected
            FROM rejected_record
            GROUP BY reason_code
            ORDER BY total_rejected DESC
        """

        rows = conn.execute(query).fetchall()

        return [
            {
                "reason": row["reason_code"],
                "count": row["total_rejected"]
            }
            for row in rows
        ]

    finally:
        conn.close()


# --------------------------------------------------
# PIPELINE RUN HISTORY
# --------------------------------------------------

@app.get("/api/dashboard/run-history")
def run_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                run_id,
                started_at,
                status,
                rows_read,
                rows_accepted,
                rows_rejected,
                duration_seconds
            FROM pipeline_run
            ORDER BY started_at DESC
        """

        rows = conn.execute(query).fetchall()

        return [
            {
                "run_id": row["run_id"],
                "started_at": row["started_at"],
                "status": row["status"],
                "rows_read": row["rows_read"],
                "accepted": row["rows_accepted"],
                "rejected": row["rows_rejected"],
                "duration": row["duration_seconds"]
            }
            for row in rows
        ]

    finally:
        conn.close()


# --------------------------------------------------
# INDIVIDUAL RUN DETAILS
# --------------------------------------------------

@app.get("/api/dashboard/run-details/{run_id}")
def run_details(run_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                run_id,
                started_at,
                status,
                rows_read,
                rows_accepted,
                rows_rejected,
                duration_seconds
            FROM pipeline_run
            WHERE run_id = ?
        """

        row = conn.execute(query, (run_id,)).fetchone()

        if row is None:
            return {
                "error": "Pipeline run not found"
            }

        return {
            "run_id": row["run_id"],
            "started_at": row["started_at"],
            "status": row["status"],
            "rows_read": row["rows_read"],
            "accepted": row["rows_accepted"],
            "rejected": row["rows_rejected"],
            "duration": row["duration_seconds"]
        }

    finally:
        conn.close()


# --------------------------------------------------
# CURATED DATA EXPLORER
# --------------------------------------------------

@app.get("/api/curated-data")
def get_curated_data(
    search: str = "",
    currency: str = "",
    txn_type: str = "",
    limit: int = 50,
    offset: int = 0
):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                txn_id,
                txn_type,
                currency,
                leg_count,
                total_amount_minor,
                first_event_ts,
                last_event_ts,
                is_late_arriving,
                source_file,
                run_id
            FROM fact_txn
            WHERE
                (? = '' OR txn_id LIKE ? OR source_file LIKE ? OR run_id LIKE ?)
                AND (? = '' OR currency = ?)
                AND (? = '' OR txn_type = ?)
            ORDER BY first_event_ts DESC
            LIMIT ? OFFSET ?
        """

        search_value = f"%{search}%"

        params = (
            search, search_value, search_value, search_value,
            currency, currency,
            txn_type, txn_type,
            max(1, min(limit, 200)),
            max(0, offset)
        )

        records = conn.execute(query, params).fetchall()

        count_query = """
            SELECT COUNT(*) FROM fact_txn
            WHERE
                (? = '' OR txn_id LIKE ? OR source_file LIKE ? OR run_id LIKE ?)
                AND (? = '' OR currency = ?)
                AND (? = '' OR txn_type = ?)
        """

        total = conn.execute(
            count_query,
            params[:8]
        ).fetchone()[0]

        return {
            "total_records": total,
            "limit": max(1, min(limit, 200)),
            "offset": max(0, offset),
            "records": [dict(row) for row in records]
        }

    finally:
        conn.close()


# --------------------------------------------------
# CURATED DATA FILTERS
# --------------------------------------------------

@app.get("/api/curated-data/filters")
def get_curated_data_filters():
    conn = sqlite3.connect(DB_PATH)

    try:
        currencies = conn.execute(
            "SELECT DISTINCT currency FROM fact_txn ORDER BY currency"
        ).fetchall()

        txn_types = conn.execute(
            "SELECT DISTINCT txn_type FROM fact_txn ORDER BY txn_type"
        ).fetchall()

        return {
            "currencies": [row[0] for row in currencies],
            "txn_types": [row[0] for row in txn_types]
        }

    finally:
        conn.close()


# --------------------------------------------------
# QUARANTINED DATA EXPLORER
# --------------------------------------------------

@app.get("/api/quarantined-data")
def get_quarantined_data(
    search: str = "",
    reason: str = "",
    limit: int = 50,
    offset: int = 0
):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        search_value = f"%{search}%"

        query = """
            SELECT
                reject_id,
                txn_id,
                source_file,
                source_row_no,
                leg_no,
                reason_code,
                reason_detail,
                rejected_at
            FROM rejected_record
            WHERE
                (
                    ? = ''
                    OR txn_id LIKE ?
                    OR source_file LIKE ?
                    OR reason_detail LIKE ?
                )
                AND (? = '' OR reason_code = ?)
            ORDER BY rejected_at DESC
            LIMIT ? OFFSET ?
        """

        params = (
            search, search_value, search_value, search_value,
            reason, reason, limit, offset
        )

        records = conn.execute(query, params).fetchall()

        count_query = """
            SELECT COUNT(*)
            FROM rejected_record
            WHERE
                (
                    ? = ''
                    OR txn_id LIKE ?
                    OR source_file LIKE ?
                    OR reason_detail LIKE ?
                )
                AND (? = '' OR reason_code = ?)
        """

        total = conn.execute(
            count_query, params[:6]
        ).fetchone()[0]

        return {
            "total_records": total,
            "limit": limit,
            "offset": offset,
            "records": [dict(row) for row in records]
        }

    finally:
        conn.close()


# --------------------------------------------------
# QUARANTINED DATA FILTERS
# --------------------------------------------------

@app.get("/api/quarantined-data/filters")
def get_quarantined_data_filters():
    conn = sqlite3.connect(DB_PATH)

    try:
        reasons = conn.execute("""
            SELECT DISTINCT reason_code
            FROM rejected_record
            ORDER BY reason_code
        """).fetchall()

        return {
            "reasons": [row[0] for row in reasons]
        }

    finally:
        conn.close()


# --------------------------------------------------
# DATA QUALITY
# --------------------------------------------------


@app.get("/api/data-quality")
def get_data_quality():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        result = conn.execute("""
            SELECT
                COUNT(*) AS total_runs,
                COALESCE(SUM(rows_read), 0) AS total_read,
                COALESCE(SUM(rows_rejected), 0) AS total_rejected,
                (SELECT COUNT(*) FROM rejected_record) AS quarantined_records
            FROM pipeline_run
            WHERE status IN ('SUCCESS', 'EMPTY_INPUT')
        """).fetchone()

        total_read = result["total_read"]
        total_rejected = result["total_rejected"]

        rejection_rate = (
            total_rejected / total_read * 100
            if total_read > 0 else 0
        )

        return {
            "total_runs": result["total_runs"],
            "total_records": total_read,
            "total_rejected": total_rejected,
            "quarantined_records": result["quarantined_records"],
            "rejection_rate": round(rejection_rate, 2),
            "quality_rate": round(100 - rejection_rate, 2)
        }

    finally:
        conn.close()



# --------------------------------------------------
# PIPELINE EXECUTION
# --------------------------------------------------

@app.post("/api/pipeline/run")
async def execute_pipeline(
    transaction_file: UploadFile = File(...),
    accounts_file: UploadFile = File(...)
):
    if not transaction_file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Transaction file must be a CSV."
        )

    if not accounts_file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Accounts file must be a CSV."
        )

    try:
        with tempfile.TemporaryDirectory(prefix="txn_pipeline_") as temp_dir:

            transaction_path = (
                Path(temp_dir) / Path(transaction_file.filename).name
            )
            accounts_path = (
                Path(temp_dir) / Path(accounts_file.filename).name
            )

            transaction_path.write_bytes(await transaction_file.read())
            accounts_path.write_bytes(await accounts_file.read())

            result = run_pipeline(
                input_path=str(transaction_path),
                accounts_path=str(accounts_path),
                cfg=Config(db_path=str(DB_PATH))
            )

            return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# --------------------------------------------------
# REPORT GENERATION
# --------------------------------------------------

@app.post("/api/reports/generate")
def generate_reports():

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    try:
        # Generate Markdown and JSON reports
        checks = write_report(conn, str(REPORTS_DIR))

        # Generate CSV exports
        export_csv(conn, str(EXPORTS_DIR))

        return {
            "status": "SUCCESS",
            "message": "Reports generated successfully.",
            "total_checks": len(checks),
            "passed_checks": sum(1 for c in checks if c["passed"]),
            "failed_checks": sum(1 for c in checks if not c["passed"]),
            "reports": [
                "validation_report.md",
                "validation_report.json",
                "execution_report.md",
                "fact_txn.csv",
                "fact_txn_leg.csv",
                "rejected_record.csv",
                "account_balance.csv",
                "pipeline_run.csv"
            ]
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        conn.close()


# --------------------------------------------------
# REPORT DOWNLOAD
# --------------------------------------------------

@app.get("/api/reports/download/{filename}")
def download_report(filename: str):

    allowed_files = {
        "validation_report.md": REPORTS_DIR / "validation_report.md",
        "validation_report.json": REPORTS_DIR / "validation_report.json",
        "execution_report.md": REPORTS_DIR / "execution_report.md",
        "fact_txn.csv": EXPORTS_DIR / "fact_txn.csv",
        "fact_txn_leg.csv": EXPORTS_DIR / "fact_txn_leg.csv",
        "rejected_record.csv": EXPORTS_DIR / "rejected_record.csv",
        "account_balance.csv": EXPORTS_DIR / "account_balance.csv",
        "pipeline_run.csv": EXPORTS_DIR / "pipeline_run.csv"
    }

    if filename not in allowed_files:
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    file_path = allowed_files[filename]

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Generate reports first."
        )

    return FileResponse(
        path=file_path,
        filename=filename
    )
