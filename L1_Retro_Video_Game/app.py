from flask import Flask
from flask_restx import Api
from database import db
from db_models import User, Game   # noqa: F401  (import so tables get created)
from routes.users import user_ns
from routes.games import game_ns

# Will use swagger for UI documentation and easy testing in `http://127.0.0.1:5000`
def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///retro_games.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    api = Api(
        app,
        title="Retro Video Game Exchange API",
        version="1.0",
        description="REST API for trading retro video games"
    )

    api.add_namespace(user_ns, path="/users")
    api.add_namespace(game_ns, path="/games")

    with app.app_context():
        db.create_all()

    return app, api

app, api = create_app()

if __name__ == "__main__":
    app.run(debug=True)
