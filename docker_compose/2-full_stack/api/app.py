import logging
import os
import sys

import psycopg
import redis
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("api")

app = Flask(__name__)

CACHE_KEY = "db_version"
CACHE_TTL = int(os.environ.get("CACHE_TTL", "30"))

cache = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


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


def get_db_version_cached():
    """Cache-aside: read Redis first, query Postgres only on a miss."""
    try:
        db_version = cache.get(CACHE_KEY)
        if db_version is not None:
            logger.info("Cache hit for %s", CACHE_KEY)
            return db_version, "hit"
        db_version = get_db_version()
        cache.set(CACHE_KEY, db_version, ex=CACHE_TTL)
        logger.info("Cache miss for %s, stored for %ds", CACHE_KEY, CACHE_TTL)
        return db_version, "miss"
    except redis.RedisError as error:
        # The cache is optional: without Redis, read Postgres directly.
        logger.warning("Redis unavailable, skipping the cache: %s", error)
        return get_db_version(), "bypass"


@app.route("/api")
def api():
    try:
        db_version, cache_status = get_db_version_cached()
    except psycopg.OperationalError as error:
        logger.warning("Database unavailable: %s", error)
        return jsonify(
            message="Hello from the API!",
            error="Database is unavailable, try again in a few seconds.",
        ), 503
    return jsonify(
        message="Hello from the API!",
        db_version=db_version,
        cache=cache_status,
    )


if __name__ == "__main__":
    # No retry on purpose: Compose must only start the API once the
    # database and Redis are healthy, so a failure here means the order
    # is wrong.
    try:
        logger.info("Connected to database: %s", get_db_version())
        cache.ping()
        logger.info("Connected to Redis")
    except (psycopg.OperationalError, redis.RedisError) as error:
        logger.error("Startup check failed, exiting: %s", error)
        sys.exit(1)
    app.run(host="0.0.0.0", port=5000)
