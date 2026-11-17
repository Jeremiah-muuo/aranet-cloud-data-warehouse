import logging
import time

import schedule

from db import init_db
from etl import sync_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def job():
    try:
        logging.info("Starting Aranet synchronization")
        inserted = sync_data()
        logging.info("Synchronization completed: %s records inserted", inserted)
    except Exception:
        logging.exception("Synchronization failed")


if __name__ == "__main__":
    init_db()
    job()

    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
