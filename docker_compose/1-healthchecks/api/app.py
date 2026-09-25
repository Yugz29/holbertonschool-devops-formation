import logging
import os
import sys

import psycopg
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("api")

app = Flask(__name__)


def get_db_version():
    """Connect to Postgres and return the result of SELECT version()."""
    with psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "app"),
        user=os.environ.get("DB_USER", "app"),
        password=os.environ.get("DB_PASSWORD"),
        connect_timeout=3,
    ) as conn:
        return conn.execute("SELECT version()").fetchone()[0]


@app.route("/api")
def api():
    try:
        db_version = get_db_version()
    except psycopg.OperationalError as error:
        logger.warning("Database unavailable: %s", error)
        return jsonify(
            message="Hello from the API!",
            error="Database is unavailable, try again in a few seconds.",
        ), 503
    return jsonify(message="Hello from the API!", db_version=db_version)


if __name__ == "__main__":
    # No retry on purpose: Compose must only start the API once the
    # database is healthy, so a failure here means the order is wrong.
    try:
        logger.info("Connected to database: %s", get_db_version())
    except psycopg.OperationalError as error:
        logger.error("Cannot connect to database, exiting: %s", error)
        sys.exit(1)
    app.run(host="0.0.0.0", port=5000)
