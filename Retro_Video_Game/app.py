from flask import Flask
from database import db
from db_models import User, Game, Offer
from routes.users import bp_users
from routes.games import bp_games
from routes.offers import bp_offers

import os

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL", "postgresql://user:password@db/retro_games")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(bp_users)
    app.register_blueprint(bp_games)
    app.register_blueprint(bp_offers)

    if os.getenv("SCHEMA_OWNER", "false").lower() == "true":
        with app.app_context():
            db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
