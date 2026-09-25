import os
import time

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)

DB_ATTEMPTS = 3
DB_RETRY_DELAY = 1


def get_db_version():
    """Run SELECT version(), retrying a few times while Postgres starts."""
    for attempt in range(1, DB_ATTEMPTS + 1):
        try:
            with psycopg.connect(
                host=os.environ.get("DB_HOST", "db"),
                dbname=os.environ.get("DB_NAME", "app"),
                user=os.environ.get("DB_USER", "app"),
                password=os.environ.get("DB_PASSWORD"),
                connect_timeout=3,
            ) as conn:
                return conn.execute("SELECT version()").fetchone()[0]
        except psycopg.OperationalError as error:
            app.logger.warning(
                "Database not ready (attempt %d/%d): %s",
                attempt, DB_ATTEMPTS, error,
            )
            if attempt == DB_ATTEMPTS:
                raise
            time.sleep(DB_RETRY_DELAY)


@app.route("/api")
def api():
    try:
        db_version = get_db_version()
    except psycopg.OperationalError:
        return jsonify(
            message="Hello from the API!",
            error="Database is not ready yet, try again in a few seconds.",
        ), 503
    return jsonify(message="Hello from the API!", db_version=db_version)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
