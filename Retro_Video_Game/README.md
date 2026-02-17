# Retro Video Game Exchange REST API

## Overview

The **Retro Video Game Exchange API** is a RESTful, microservice-based web platform that allows users to register accounts, manage a collection of retro video games, and trade with other users. Users can create offers, accept or reject trades, and receive real-time email notifications through a Kafka-powered email service.

This project was developed as part of the **CSC380** course to demonstrate:

- REST API design  
- Persistent data storage  
- Richardson Maturity Model Level 3 (HATEOAS) compliance  
- Service-Oriented Architecture (SOA)  
- Event-driven messaging using Kafka  

---

## Features

- User registration and profile management  
- CRUD operations for retro video games  
- Ownership enforcement for user and game updates  
- Offer system with accept/reject workflow  
- Kafka-based email notification microservice  
- Search functionality (by name, system, or owner)  
- Persistent storage using PostgreSQL  
- JSON-based request and response bodies  
- NGINX reverse proxy & load balancing  
- Richardson Maturity Model Level 3 (HATEOAS) compliant responses  

---

## Technologies Used

- Python 3  
- Flask  
- Flask-SQLAlchemy  
- PostgreSQL  
- Apache Kafka  
- Docker & Docker Compose  
- NGINX  
- Ethereal SMTP (test email service)  

---

## Project Structure

```text
Retro_Video_Game/
│
├── app.py                  # Main API entry point
├── database.py             # Database initialization
├── db_models.py            # SQLAlchemy models
├── kafka_producer.py       # Kafka notification publisher
│
├── routes/
│   ├── users.py            # User API endpoints
│   ├── offers.py           # Offer API endpoints
│   └── games.py            # Game API endpoints
│
├── utils/
│   ├── hateoas_helper      # A hateoas helper
│   └── auth.py             # Basic Auth ownership enforcement
│
├── email_service/
│   ├── consumer.py         # Kafka email consumer
│   ├── Dockerfile          # email_service container
│   ├── entrypoint.sh       # entrypoint helper to start files in the correct order 
│   ├── requirements.txt    # Kafka dependencies
│   └── wait_for_kafka.py   # Startup dependency check
│
├── docker-compose.yml      # API, Kafka, DB, Email Service, NGINX
├── Dockerfile              # Flask API container
├── nginx.conf              # Reverse proxy config
├── requirements.txt       # Python dependencies
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd retro-video-game-exchange
```

### 2. Build & Start Containers

```bash
docker-compose up --build
```

The API will be available via NGINX at:

```text
http://localhost/
```

---

## API Overview

### Users

- POST /users – Create a new user  
- GET /users/{id} – Retrieve user details  
- PUT /users/{id} – Update name and address  
- PATCH /users/{id} – Update password  
- GET /users – Retrieve all users  

### Games

- POST /users/{id}/games – Create a game  
- GET /games/{id} – Retrieve a game  
- PUT /games/{id} – Update a game  
- DELETE /games/{id} – Delete a game  
- GET /games/all – Retrieve all games  

### Offers

- POST /offers/users/{id} – Create a new offer  
- PUT /offers/users/{id}/{offer_id} – Accept/Reject offer  
- GET /offers/users/{id} – View all related offers  

---

## Event-Driven Email Notifications

This system uses **Apache Kafka** to decouple email delivery from the API:

1. API sends notification events to Kafka.  
2. The email-service container consumes messages.  
3. The service logs into the sender’s SMTP inbox.  
4. The message is delivered to the intended recipient.  

Each user stores their own SMTP credentials (`smtp_email`, `smtp_password`) in the database.

This ensures:

- No static environment emails  
- True multi-user messaging  
- Fully asynchronous notifications  

---

## Ownership Enforcement

Ownership is enforced using **HTTP Basic Authentication**.  
Only the authenticated owner of a resource may modify or delete it.

---

## HATEOAS (RMM Level 3 Compliance)

All responses include navigational links:

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

The API returns appropriate status codes:

- 400 Bad Request  
- 403 Forbidden  
- 404 Not Found  
- 409 Conflict  
- 5xx Server Errors  

---

## Academic Integrity & AI Assistance Disclosure

This project was developed by the repository owner.

Portions of this project were created or refactored with the assistance of **ChatGPT (OpenAI)** and then reviewed, tested, and integrated by the student.

### AI-assisted components include:

- Kafka-based email microservice architecture  
- SMTP authentication handling and consumer logic  
- Offer notification logic and message contracts  
- Authentication refactor to HTTP Basic Auth  
- Ownership enforcement logic in:  
  - routes/users.py  
  - routes/games.py  
  - routes/offers.py  
- PostgreSQL & SQLAlchemy configuration fixes  
- Docker Compose architecture  
- NGINX reverse proxy configuration  
- Event-driven messaging design  
- README documentation formatting  

All final design decisions, debugging, testing, and validation were performed by the student.

---

## License

This project is intended for **educational purposes only**.
