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
│   └── games.py         # Game API endpoints
├── requirements.txt     # Python dependencies used for this project
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

The API will be available at:

```
http://localhost:5000/
```

Swagger (OpenAPI) documentation is accessible via the root URL.

---

## API Overview

### Users

* `POST /users` – Create a new user
* `GET /users/{id}` – Retrieve user details
* `PUT /users/{id}` – Update user name and address (email immutable)
* `GET /users/all` - Retrieves all users 

### Games

* `POST /users/{id}/games` – Create a game owned by a user
* `GET /games/{id}` – Retrieve a specific game
* `PUT /games/{id}` – Update a game (owner only)
* `DELETE /games/{id}` – Delete a game (owner only)
* `GET /games` – Search games by name, system, or owner

---

## Ownership Enforcement

Ownership is enforced using a simulated authentication mechanism via request headers.

### Header Format

```
X-User-Id: <user_id>
```

Rules enforced:

* Only the owner of a game may update or delete it
* Users may only update their own profile information

Unauthorized actions return:

```
403 Forbidden / Game Not Owned
```

---

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

This project was developed by the repository owner. Guidance, architectural advice, and example code patterns were provided with the assistance of **ChatGPT (OpenAI)**. All code was reviewed, adapted, and integrated by the student to ensure understanding and correctness.

AI assistance was used primarily for:

* REST API architectural planning
* Flask and SQLAlchemy setup guidance
* Example CRUD endpoint patterns
* HATEOAS design examples
* README documentation structure

No code was submitted without review and modification by the student.

---

## License

This project is intended for educational purposes only.
