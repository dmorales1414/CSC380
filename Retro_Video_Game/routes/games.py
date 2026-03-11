from flask import Blueprint, current_app, request, jsonify
from db_models import Game, User, Offer
from database import db
from werkzeug.security import generate_password_hash
from utils.auth import get_authenticated_user
from utils.hateoas_helper import game_links

# Blueprint for game routes
bp_games = Blueprint("games", __name__, url_prefix="/games")

# Get all games
@bp_games.get("/all")
def search_games():
    game_redis_client = current_app.redis_client
    cache_key = f"all_games"

    cached_games = game_redis_client.get(cache_key)

    if cached_games:
        print("CACHE HIT: all_games")
        return jsonify(cached_games)

    print("CACHE MISS: all_games")

    games =[{
        "id": g.id,
        "name": g.name,
        "system": g.system,
        "owner_id": g.owner_id,
        "links": game_links(g)
        } for g in Game.query.all()]
    
    # Cache the games for 1 minute (60 seconds) afterwards it will be removed and the process will repeat on the next request
    game_redis_client.setex(cache_key, 60, jsonify(games).get_data(as_text=True))
    
    return jsonify(games)

# Create a new game for a specific user
@bp_games.post("/users/<int:user_id>")
def create_game(user_id):
    game_redis_client = current_app.redis_client

    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    data = request.json
    game = Game(**data, owner_id=user_id)

    db.session.add(game)
    db.session.commit()
    
    game_redis_client.delete("all_games")
    
    return jsonify({
        "id": game.id,
        "links": game_links(game)
    }), 201

# Update a specific game
@bp_games.put("/<int:game_id>")
def update_game(game_id):
    game_redis_client = current_app.redis_client

    user = get_authenticated_user()
    game = Game.query.get_or_404(game_id)

    if not user or user.id != game.owner_id:
        return {"error": "Forbidden: Must be the owner of the game to update it"}, 403

    for key, value in request.json.items():
        setattr(game, key, value)

    db.session.commit()

    game_redis_client.delete("all_games")

    return "", 204

# Delete a specific game
@bp_games.delete("/<int:game_id>")
def delete_game(game_id):
    game_redis_client = current_app.redis_client

    user = get_authenticated_user()
    game = Game.query.get_or_404(game_id)

    if not user or user.id != game.owner_id:
        return {"error": "Forbidden: Must be the owner of the game to delete it"}, 403

    db.session.delete(game)
    db.session.commit()

    game_redis_client.delete("all_games")
    
    return "", 204
