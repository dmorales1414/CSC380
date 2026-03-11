from flask import Flask, Response, request
from database import db
from db_models import User, Game, Offer
from routes.users import bp_users
from routes.games import bp_games
from routes.offers import bp_offers

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, start_http_server
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import redis
import json

import os

# Creates a request counter metric with method and endpoint labels
REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total HTTP requests", 
    ["method", "endpoint"]
)

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL", "postgresql://user:password@db/retro_games")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.redis_client = redis.Redis(
        host="redis",
        port=6379,
        decode_responses=True
    )

    app.register_blueprint(bp_users)
    app.register_blueprint(bp_games)
    app.register_blueprint(bp_offers)

    if os.getenv("SCHEMA_OWNER", "false").lower() == "true":
        with app.app_context():
            db.create_all()

    return app

app = create_app()

@app.before_request
def before_request():
    if request.path != "/metrics":
        REQUEST_COUNT.labels(request.method, request.path).inc()

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


# NOTE:
#   The way to view Redis Caching more effecticvely is to open the redis container
#       and run the command `redis-cli monitor` to see the cache hits and misses in real time as you interact with the API.
#   Another way is to type `redis-cli` to open the Redis CLI and then you can run commands like 
#   `   keys *` to see all the keys in the cache or `get <key>` to see the value of a specific key.