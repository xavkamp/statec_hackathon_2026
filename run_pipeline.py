"""Master pipeline orchestrator for STATEC Hackathon 2026.
Runs ingestion, silver transforms, gold analytics, and starts the dashboard.
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
from src.processing.transform_silver import run_all_silver_transforms
from src.processing.transform_gold import run_all_gold_transforms
from src.dashboard.app import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("orchestrator")


def main():
    parser = argparse.ArgumentParser(description="STATEC Hackathon 2026 - Luxembourg External Trade")
    parser.add_argument("--ingest", action="store_true", help="Run Eurostat Comext Bronze data ingestion")
    parser.add_argument("--silver", action="store_true", help="Run Silver data transformations")
    parser.add_argument("--gold", action="store_true", help="Run Gold analytical transformations")
    parser.add_argument("--app", action="store_true", help="Launch the interactive Dash dashboard")
    parser.add_argument("--all", action="store_true", help="Run all pipelines from Bronze to Gold and launch app")
    parser.add_argument("--port", type=int, default=8050, help="Port for Dash server (default: 8050)")

    args = parser.parse_args()

    # If no flags passed, default to launching app
    if not (args.ingest or args.silver or args.gold or args.app or args.all):
        args.app = True

    if args.all or args.ingest:
        logger.info("Executing Bronze Data Ingestion...")
        run_all_ingestion()

    if args.all or args.silver:
        logger.info("Executing Silver Transformations...")
        run_all_silver_transforms()

    if args.all or args.gold:
        logger.info("Executing Gold Transformations...")
        run_all_gold_transforms()

    if args.all or args.app:
        logger.info(f"Starting Interactive Dash Application on http://127.0.0.1:{args.port} ...")
        app.run(debug=False, port=args.port, host="127.0.0.1")


if __name__ == "__main__":
    main()
