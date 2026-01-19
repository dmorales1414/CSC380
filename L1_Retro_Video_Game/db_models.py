from database import db

# Models for the User and Game tables
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    games = db.relationship("Game", backref="owner", lazy=True)


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    system = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    previous_owners = db.Column(db.Integer, nullable=True) # Can be null

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)