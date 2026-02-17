def game_links(game):
    return {
        "self": {"href": f"/games/{game.id}"},
        "owner": {"href": f"/users/{game.owner_id}"},
        "update": {"href": f"/games/{game.id}", "method": "PUT"},
        "delete": {"href": f"/games/{game.id}", "method": "DELETE"}
    }

def offer_links(offer):
    return {
        "self": {"href": f"/offers/{offer.id}"},
        "from_user": {"href": f"/users/{offer.from_user_id}"},
        "to_user": {"href": f"/users/{offer.to_user_id}"},
        "update": {"href": f"/offers/users/{offer.to_user_id}/{offer.id}", "method": "PUT"}
    }

def user_links(user):
    return {
        "self": {"href": f"/users/{user.id}"},
        "update": {"href": f"/users/{user.id}", "method": "PUT"},
        "password": {"href": f"/users/{user.id}", "method": "PATCH"},
        "offers": {"href": f"/offers/users/{user.id}"},
        "games": {"href": f"/games/users/{user.id}"}
    }
