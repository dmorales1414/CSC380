from flask import request
from db_models import User
from werkzeug.security import check_password_hash

# Switch towards an email and password based authentication
def get_authenticated_user():
    auth = request.authorization
    if not auth:
        return None

    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return None

    if not check_password_hash(user.password, auth.password):
        return None

    return user
