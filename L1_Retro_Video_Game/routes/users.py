from flask import request
from flask_restx import Namespace, Resource, fields
from db_models import User
from database import db
from auth import get_authenticated_user_id

user_ns = Namespace("users", description="User operations")
auth_header = user_ns.parser()
auth_header.add_argument(
    "X-User-Id",
    location="headers",
    type=int,
    required=True,
    help="Authenticated user ID"
)

# Swagger Model
user_model = user_ns.model("User", {
    "id": fields.Integer(readOnly=True),
    "name": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True),
    "address": fields.String(required=True)
})

# CREATE USER
@user_ns.route("")
class UserList(Resource):

    @user_ns.expect(user_model)
    @user_ns.response(201, "User created")
    def post(self):
        data = request.json

        # Check email uniqueness
        if User.query.filter_by(email=data["email"]).first():
            return {
                "error": "Email already exists"
            }, 409

        user = User(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            address=data["address"]
        )

        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "_links": {
                "self": {"href": f"/users/{user.id}"},
                "update": {"href": f"/users/{user.id}", "method": "PUT"},
                "games": {"href": f"/users/{user.id}/games"}
            
            }
        }, 201


# GET / UPDATE USER
@user_ns.route("/<int:user_id>")
class UserResource(Resource):

    # GET USER
    @user_ns.response(200, "Success")
    @user_ns.response(404, "User not found")
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "_links": {
                "self": {"href": f"/users/{user.id}"},
                "update": {"href": f"/users/{user.id}", "method": "PUT"},
                "games": {"href": f"/users/{user.id}/games"}
            }
        }, 200

    # UPDATE USER
    @user_ns.expect(auth_header, user_model)
    @user_ns.response(204, "User updated")
    @user_ns.response(403, "User not owned")
    @user_ns.response(404, "User not found")
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        
        # Checks ownership
        current_user_id = get_authenticated_user_id()
        if current_user_id != user.id:
            return {"error": "You can only update your own user data"}, 403

        data = request.json

        # Note: Email cannot be changed
        user.name = data["name"]
        user.address = data["address"]

        db.session.commit()
        return "", 204
    

# GET all users
@user_ns.route("/all")
class UserAllResource(Resource):
    @user_ns.response(200, "Success")
    def get(self):
        users = User.query.all()
        users_list = []
        for user in users:
            users_list.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "_links": {
                    "self": {"href": f"/users/{user.id}"},
                    "update": {"href": f"/users/{user.id}", "method": "PUT"},
                    "games": {"href": f"/users/{user.id}/games"}
                }
            })
        return users_list
