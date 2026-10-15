"""Master pipeline orchestrator for STATEC Hackathon 2026.
Pure CSV Pipeline:
Eurostat Comext API -> data/raw/*.csv -> data/processed/*.csv -> Interactive Dash App.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ingestion.fetch_data import run_all_ingestion
from src.processing.process_data import run_all_processing
from src.dashboard.app import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("orchestrator")


def main():
    parser = argparse.ArgumentParser(description="STATEC Hackathon 2026 - Luxembourg External Trade (Pure CSV Pipeline)")
    parser.add_argument("--ingest", action="store_true", help="Extract trade data from Eurostat directly to data/raw/*.csv")
    parser.add_argument("--process", action="store_true", help="Transform raw CSVs into aggregated data/processed/*.csv tables")
    parser.add_argument("--app", action="store_true", help="Launch the interactive Dash dashboard")
    parser.add_argument("--all", action="store_true", help="Run end-to-end pipeline (Ingest CSV -> Process CSV -> Launch App)")
    parser.add_argument("--test", action="store_true", help="Execute the comprehensive automated test suite in tests/")
    parser.add_argument("--port", type=int, default=8050, help="Port for Dash server (default: 8050)")

    args = parser.parse_args()

    if args.test:
        logger.info("Executing Master Test Suite in tests/...")
        from tests.run_all_tests import run_all
        run_all()
        return

    # If no flags passed, default to launching app
    if not (args.ingest or args.process or args.app or args.all):
        args.app = True

    if args.all or args.ingest:
        logger.info("Executing Eurostat Comext Ingestion directly to data/raw/*.csv...")
        run_all_ingestion()

    if args.all or args.process:
        logger.info("Executing Data Processing directly to data/processed/*.csv...")
        run_all_processing()

    if args.all or args.app:
        logger.info(f"Starting Interactive Dash Application on http://127.0.0.1:{args.port} ...")
        app.run(debug=True, port=args.port, host="127.0.0.1")


if __name__ == "__main__":
    main()
