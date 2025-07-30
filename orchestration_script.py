import subprocess
import logging
import sys
import os
from datetime import datetime

# Setup log file
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "scrapy_run.log")

logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

def run_spider():
    logging.info("🕷 Starting Scrapy spider...")

    # ✅ Use relative path to spider inside "spiders/" subfolder
    spider_path = os.path.join(os.path.dirname(__file__), "spiders", "bankrate_rates_spider.py")
    logging.info(f"Using spider file: {spider_path}")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "scrapy", "runspider", spider_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info("✅ Spider completed successfully.")
        logging.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("❌ Spider failed.")
        logging.error(e.stderr)
        return False

def run_transformer():
    logging.info("📦 Running transformation script...")

    transformer_path = os.path.join(os.path.dirname(__file__), "spiders", "append_json_to_csv.py")
    logging.info(f"Using transformer script: {transformer_path}")

    try:
        result = subprocess.run(
            [sys.executable, transformer_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info("✅ Transformation completed successfully.")
        logging.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("❌ Transformation script failed.")
        logging.error(e.stderr)
        return False

def main():
    logging.info("🚀 Orchestrator started.")

    success_spider = run_spider()
    success_transform = False

    if success_spider:
        success_transform = run_transformer()
    else:
        logging.warning("⚠ Skipping transformation because spider failed.")

    if success_spider and success_transform:
        logging.info("✅ Full pipeline succeeded.")
        sys.exit(0)
    else:
        logging.error("❌ Pipeline failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
