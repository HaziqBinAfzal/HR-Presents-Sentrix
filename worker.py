import os
import time

from app import create_app
from helpers.background_analysis import claim_next_job, fail_job, process_job


def run_worker():
    app = create_app()
    poll_seconds = float(os.getenv("ANALYSIS_WORKER_POLL_SECONDS", "2"))
    once = os.getenv("ANALYSIS_WORKER_ONCE", "0").lower() in {"1", "true", "yes", "on"}

    with app.app_context():
        while True:
            job = claim_next_job()
            if job is None:
                if once:
                    return
                time.sleep(poll_seconds)
                continue

            try:
                app.logger.info("Processing analysis job %s", job.id)
                process_job(job)
            except Exception as exc:
                app.logger.exception("Analysis job %s failed", job.id)
                fail_job(job, exc)

            if once:
                return


if __name__ == "__main__":
    run_worker()
