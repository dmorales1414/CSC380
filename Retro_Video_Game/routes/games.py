from flask import Blueprint, request, jsonify
from db_models import Game, User, Offer
from database import db
from werkzeug.security import generate_password_hash
from auth import get_authenticated_user

# Blueprint for game routes
bp_games = Blueprint("games", __name__, url_prefix="/games")

# Get all games
@bp_games.get("/all")
def search_games():
    return jsonify([{
        "id": g.id,
        "name": g.name,
        "system": g.system,
        "owner_id": g.owner_id
    } for g in Game.query.all()])

# Create a new game for a specific user
@bp_games.post("/users/<int:user_id>")
def create_game(user_id):
    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    data = request.json
    game = Game(**data, owner_id=user_id)
    db.session.add(game)
    db.session.commit()
    return jsonify(id=game.id), 201

# Update a specific game
@bp_games.put("/<int:game_id>")
def update_game(game_id):
    user = get_authenticated_user()
    game = Game.query.get_or_404(game_id)

    if not user or user.id != game.owner_id:
        return {"error": "Forbidden: Must be the owner of the game to update it"}, 403

    for key, value in request.json.items():
        setattr(game, key, value)

    db.session.commit()
    return "", 204

# Delete a specific game
@bp_games.delete("/<int:game_id>")
def delete_game(game_id):
    user = get_authenticated_user()
    game = Game.query.get_or_404(game_id)

    if not user or user.id != game.owner_id:
        return {"error": "Forbidden: Must be the owner of the game to delete it"}, 403

    db.session.delete(game)
    db.session.commit()
    return "", 204
