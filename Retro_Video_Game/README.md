# Retro Video Game Exchange REST API

## Overview

The Retro Video Game Exchange API is a RESTful web service that allows users to register accounts and manage a collection of retro video games they wish to trade with other users. The API supports creating, updating, retrieving, deleting, and searching for video games, as well as managing user information. Ownership of games is enforced so that only the user who owns a game may modify or delete it.

This project was developed as part of the **CSC380** course to demonstrate REST API design, persistent storage, Richardson Maturity Model Level 3 (HATEOAS) compliance, and service-oriented architecture concepts.

---

## Features

* User registration and profile management
* CRUD operations for retro video games
* Ownership enforcement for game and user updates
* Search functionality for games (by name, system, or owner)
* Persistent data storage using SQLite
* JSON-based request and response bodies
* OpenAPI (Swagger) documentation
* Richardson Maturity Model Level 3 (HATEOAS) compliant responses

---

## Technologies Used

* **Python 3**
* **Flask**
* **Flask-SQLAlchemy**
* **Flask-RESTX** (for REST structure and OpenAPI documentation)
* **SQLite** (persistent storage)

---

## Project Structure

```
L1_Retro_Video_Game/
│
├── app.py               # Application entry point
├── database.py          # Database initialization
├── db_models.py         # SQLAlchemy models
├── auth.py              # Simple ownership/authentication helper
├── routes/
│   ├── users.py         # User API endpoints
│   ├── offers.py        # Offers API endpoints
|   └── games.py         # Game API endpoints
├── requirements.txt     # Python dependencies used for this project
├── docker-compose.yml   # Contains the both APIs, NGINX, and Database containers
├── Dockerfile           # Dockerfile containing the instructions to pip install what's inside requirements.txt
├── nginx.conf           # Configurations for the NGINX container
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd retro-video-game-exchange
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The APIs will be available at thanks to NGINX:

```
http://localhost/
```

Removed Swagger Contents
---

## API Overview

### Users

* `POST /users` – Create a new user
* `GET /users/{id}` – Retrieve user details
* `PUT /users/{id}` – Update user name and address (email immutable)
* `GET /users` - Retrieves all users 

### Games

* `POST /users/{id}/games` – Create a game owned by a user
* `GET /games/{id}` – Retrieve a specific game
* `PUT /games/{id}` – Update a game (owner only)
* `DELETE /games/{id}` – Delete a game (owner only)
* `GET /games/all` – Retrieves all games

---

## Ownership Enforcement

Ownership is enforced using a simulated authentication mechanism via basic auth in email and password.

## HATEOAS (RMM Level 3 Compliance)

All resource responses include navigational links under a `_links` object, allowing clients to discover related actions dynamically.

Example:

```json
"_links": {
  "self": { "href": "/games/1" },
  "owner": { "href": "/users/1" },
  "update": { "href": "/games/1", "method": "PUT" },
  "delete": { "href": "/games/1", "method": "DELETE" }
}
```

---

## Error Handling

The API returns appropriate HTTP status codes and JSON error messages:

* `400 Bad Request`
* `403 Forbidden`
* `404 Not Found`
* `409 Conflict`
* `5xx Server Errors` (avoided by design)

---

## Academic Integrity & AI Assistance Disclosure

This project was developed by the repository owner.

The following components were created or refactored with assistance from ChatGPT (OpenAI) and then reviewed, tested, and integrated by the student:

AI-assisted components:

* Authentication refactor from X-User-Id headers to HTTP Basic Auth (auth.py)
* Ownership enforcement logic in:
* * routes/users.py
* * routes/games.py
* * routes/offers.py
* Offer status validation logic (accepted/rejected only)
* NGINX reverse proxy and load balancing configuration directions
* Docker Compose architecture (API + DB + NGINX)
* PostgreSQL + SQLAlchemy configuration fixes
* Partial Round-robin testing strategy
* README structure and documentation improvements

All final code and configuration choices were implemented and validated by the student.

## License

This project is intended for educational purposes only.
