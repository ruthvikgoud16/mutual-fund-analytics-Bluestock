"""Master ETL & Analytics Pipeline Orchestrator for Bluestock Mutual Fund Platform.

Executes all 7 days of the Bluestock Capstone project sequentially:
1. Ingestion & Live NAV API Fetch
2. Data Cleaning & SQLite Database Load
3. Exploratory Data Analysis (EDA Visualizations)
4. Performance & Risk Engine Execution
5. Advanced Analytics (VaR, Cohorts, Recommender, Sector HHI)
6. Interactive Dashboard PDF Export & Presentation Deck Generation
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "scripts"))

from cohort_analysis import main as run_cohort_main
from data_ingestion import main as run_data_ingestion
from export_dashboard_pdf import generate_dashboard_pdf
from generate_eda import generate_visualizations as generate_all_eda_visualizations
from generate_final_pdf import build_pdf_report
from generate_presentation import build_presentation
from generate_risk_charts import generate_all_risk_charts
from live_nav_fetch import run_live_nav_ingestion
from load_sql import main as run_etl_load
from recommender import print_recommendations
from risk_metrics import compute_all_scheme_risk_metrics, save_risk_metrics_to_db
from utils import setup_logging

logger = setup_logging("run_pipeline")


def execute_master_pipeline():
    """Execute the complete end-to-end Bluestock Mutual Fund Analytics pipeline."""
    start_time = time.time()
    logger.info("==========================================================")
    logger.info(" STARTING MASTER BLUESTOCK MUTUAL FUND ANALYTICS PIPELINE")
    logger.info("==========================================================")

    # Step 1: Ingestion & Live NAV Fetch
    logger.info("Step 1: Running Data Ingestion & Live NAV Fetch...")
    run_data_ingestion()
    run_live_nav_ingestion()

    # Step 2: Data Cleaning & SQLite DB Load
    logger.info("Step 2: Cleaning Datasets & Loading SQLite Database...")
    run_etl_load()

    # Step 3: EDA Visualizations
    logger.info("Step 3: Generating EDA Visualizations...")
    generate_all_eda_visualizations()

    # Step 4: Risk Analytics & Metrics DB Sync
    logger.info("Step 4: Computing Performance & Risk Metrics...")
    df_metrics = compute_all_scheme_risk_metrics()
    save_risk_metrics_to_db(df_metrics)
    generate_all_risk_charts()

    # Step 5: Advanced Analytics (VaR, Cohorts, Recommender)
    logger.info("Step 5: Executing Advanced Analytics & Cohorts Engine...")
    run_cohort_main()
    print_recommendations(risk_appetite="Moderate", top_n=3)

    # Step 6: Export Dashboard PDF, Final PDF & PowerPoint Presentation
    logger.info(
        "Step 6: Generating Final PDF Report, Presentation Deck & Dashboard Exports..."
    )
    generate_dashboard_pdf()
    build_pdf_report()
    build_presentation()

    elapsed = time.time() - start_time
    logger.info("==========================================================")
    logger.info(f" MASTER PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS")
    logger.info("==========================================================")


if __name__ == "__main__":
    execute_master_pipeline()
