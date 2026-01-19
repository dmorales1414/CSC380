from flask import request
from flask_restx import Namespace, Resource, fields
from db_models import Game, User
from database import db
from auth import get_authenticated_user_id

game_ns = Namespace("games", description="Game operations")
auth_header = game_ns.parser()
auth_header.add_argument(
    "X-User-Id",
    location="headers",
    type=int,
    required=True,
    help="Authenticated user ID"
)


# -----------------
# Swagger Models
# -----------------
game_model = game_ns.model("Game", {
    "id": fields.Integer(readOnly=True),
    "name": fields.String(required=True),
    "publisher": fields.String(required=True),
    "year_published": fields.Integer(required=True),
    "system": fields.String(required=True),
    "condition": fields.String(required=True),
    "previous_owners": fields.Integer(required=False),
    "owner_id": fields.Integer(required=True)
})

# -------------------------
# CREATE GAME
# -------------------------
@game_ns.route("/users/<int:user_id>/games")
class UserGameList(Resource):

    @game_ns.expect(game_model)
    @game_ns.response(201, "Game created")
    @game_ns.response(404, "User not found")
    def post(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        data = request.json

        game = Game(
            name=data["name"],
            publisher=data["publisher"],
            year_published=data["year_published"],
            system=data["system"],
            condition=data["condition"],
            previous_owners=data.get("previous_owners"),
            owner_id=user.id
        )

        db.session.add(game)
        db.session.commit()

        return {
            "id": game.id,
            "name": game.name,
            "system": game.system,
            "condition": game.condition,
            "_links": {
                "self": {"href": f"/games/{game.id}"},
                "owner": {"href": f"/users/{user.id}"},
                "update": {"href": f"/games/{game.id}", "method": "PUT"},
                "delete": {"href": f"/games/{game.id}", "method": "DELETE"}
            }
        }, 201

# Endpoint to for GET
@game_ns.route("")
class GameList(Resource):
    def get(self):
        query = Game.query

        name = request.args.get("name")
        system = request.args.get("system")
        owner_id = request.args.get("owner_id")

        if name:
            query = query.filter(Game.name.ilike(f"%{name}%"))
        if system:
            query = query.filter_by(system=system)
        if owner_id:
            query = query.filter_by(owner_id=owner_id)

        games = query.all()

        return [
            {
                "id": g.id,
                "name": g.name,
                "system": g.system,
                "condition": g.condition,
                "_links": {
                    "self": {"href": f"/games/{g.id}"},
                    "owner": {"href": f"/users/{g.owner_id}"}
                }
            }
            for g in games
        ], 200


# -------------------------
# GET / UPDATE / DELETE GAME
# -------------------------
@game_ns.route("/<int:game_id>")
class GameResource(Resource):
    # -----------------
    # GET GAME
    # -----------------
    @game_ns.response(200, "Success")
    @game_ns.response(404, "Game not found")
    def get(self, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {"error": "Game not found"}, 404

        return {
            "id": game.id,
            "name": game.name,
            "publisher": game.publisher,
            "year_published": game.year_published,
            "system": game.system,
            "condition": game.condition,
            "previous_owners": game.previous_owners,
            "owner_id": game.owner_id,
            "_links": {
                "self": {"href": f"/games/{game.id}"},
                "owner": {"href": f"/users/{game.owner_id}"},
                "update": {"href": f"/games/{game.id}", "method": "PUT"},
                "delete": {"href": f"/games/{game.id}", "method": "DELETE"}
            }
        }, 200

    # -----------------
    # UPDATE GAME
    # -----------------
    @game_ns.expect(auth_header, game_model)
    @game_ns.response(204, "Game updated")
    @game_ns.response(403, "Game not owned")
    @game_ns.response(404, "Game not found")

    def put(self, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {"error": "Game not found"}, 404
        
        # Checks ownership
        current_user_id = get_authenticated_user_id()
        if current_user_id != game.owner_id:
            return {"error": "You do not own this game"}, 403

        data = request.json

        game.name = data["name"]
        game.publisher = data["publisher"]
        game.year_published = data["year_published"]
        game.system = data["system"]
        game.condition = data["condition"]
        game.previous_owners = data.get("previous_owners")

        db.session.commit()
        return "", 204

    # -----------------
    # DELETE GAME
    # -----------------
    @game_ns.expect(auth_header)
    @game_ns.response(200, "Game deleted")
    @game_ns.response(403, "Game not owned")
    @game_ns.response(404, "Game not found")
    def delete(self, game_id):
        game = Game.query.get(game_id)
        if not game:
            return {"error": "Game not found"}, 404
        
        # Checks ownership
        current_user_id = get_authenticated_user_id()
        if current_user_id != game.owner_id:
            return {"error": "You do not own this game"}, 403


        db.session.delete(game)
        db.session.commit()
        return {"message": "Game deleted"}, 200
