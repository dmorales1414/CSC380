from flask import request

# X-User-Id and User ID must match to authenticate (such as the owner ID must match the X-User-Id header)
# Returns None if no valid user ID is found
def get_authenticated_user_id():
    user_id = request.headers.get("X-User-Id")
    if user_id is None:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None