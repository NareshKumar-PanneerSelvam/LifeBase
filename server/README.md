# LifeBase Server (FastAPI Backend)

A production-grade, high-performance async-first backend for **LifeBase** written in Python 3.12 utilizing the FastAPI framework. This server is designed to replace the legacy Java backend.

---

## 🚀 Tech Stack
*   **Python**: 3.12
*   **Web Framework**: FastAPI (Async-first)
*   **Database**: PostgreSQL
*   **SQL ORM**: SQLAlchemy 2.0 (Async mapping, type annotations)
*   **Database Migrations**: Alembic
*   **Serialization & Validation**: Pydantic v2
*   **Security & Encryption**: `python-jose` (JWT), `passlib` with `bcrypt` (password hashing), SHA-256 (token hashing)
*   **Environment & Config**: `pydantic-settings`
*   **Logging**: `structlog` (Structured JSON outputs)
*   **Package Manager**: `uv` (fastest python dependency manager)
*   **Containerization**: Docker & Docker Compose

---

## 🏛️ Architecture & Project Structure
The backend implements a **Modular Monolith** matching a highly scalable **Repository-Service Pattern**:

```
server/
│
├── alembic/                # Database migration schemas
│   ├── versions/           # Migration revisions
│   └── env.py              # Async migration runner
│
├── app/
│   ├── api/
│   │   └── v1/             # Versioned controllers
│   │       ├── auth/       # Authentication endpoints
│   │       ├── users/      # User profile endpoints
│   │       └── health/     # Health checking status
│   │
│   ├── core/               # Shared system infrastructure
│   │   ├── config.py       # Pydantic environment loader
│   │   ├── database.py     # SQLAlchemy Async Engine and session builder
│   │   ├── security.py     # Password hashing, JWT token issuers
│   │   ├── dependencies.py # API dependency injections (Auth check, admin check)
│   │   ├── exceptions.py   # Zentralized exception handling
│   │   └── logging.py      # Structlog logging configuration
│   │
│   ├── models/             # SQLAlchemy ORM schemas
│   ├── schemas/            # Pydantic data serialization schemas
│   ├── repositories/       # Generic and model-specific data access layers (DAL)
│   ├── services/           # Coordinated business logic layer
│   ├── middleware/         # Custom log and metrics interceptors
│   │
│   └── main.py             # FastAPI entrypoint and lifespan coordinator
│
├── tests/                  # Integration tests
│   ├── conftest.py         # Pytest shared async resources and sqlite fixture
│   └── test_auth.py        # Token operations and access tests
│
├── .env.example            # Environment properties template
├── pyproject.toml          # UV project dependency manifests
├── Dockerfile              # Multi-stage container build
├── docker-compose.yml      # DB and application multi-service mapping
└── README.md               # Setup and development guide
```

---

## 🔐 High-Security JWT Flow & Breach Mitigation
We employ a production-grade session security framework focusing on:
1.  **Hashed Session Data**: We *never* store refresh tokens as plain text in the database. Every token is stored as a deterministic **SHA-256 hash**. If the database is compromised, sessions remain completely secure since a SHA-256 representation cannot be utilized as a JWT credential.
2.  **Refresh Token Rotation (RTR)**: When the client requests an access token refresh using a refresh token:
    *   The service verifies and decodes the token.
    *   It checks the database to verify the token hash exists, is active, and is not expired.
    *   Upon successful validation, **the used refresh token is immediately marked as revoked**, and a brand new Access and Refresh Token pair is returned to the client.
3.  **Active Breach Mitigation**: If an attacker steals a refresh token and attempts a replay attack using an **already revoked** token:
    *   The database detects that this specific token is already marked as `revoked=True`.
    *   This indicates a potential session theft (either the client or the attacker is attempting token reuse).
    *   **The server automatically revokes all active sessions for that user immediately**, terminating every active token and forcing a fresh login.

---

## ⚙️ Local Development Setup

### 📦 Prerequisites
Ensure you have `uv` installed. If not, install it using:
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 🛠️ Step-by-Step Installation

1.  **Clone / Open Project**
    Navigate to the project root:
    ```bash
    cd d:\LifeBase\server
    ```

2.  **Create Virtual Environment**
    Create a Python 3.12 virtual environment:
    ```bash
    uv venv --python 3.12
    ```

3.  **Activate Virtual Environment**
    ```bash
    # Windows (PowerShell)
    .venv\Scripts\Activate.ps1

    # macOS/Linux
    source .venv/bin/activate
    ```

4.  **Install Dependencies**
    Install all required standard and development libraries:
    ```bash
    uv pip install -e ".[dev]"
    ```

5.  **Configure Environment**
    Copy `.env.example` to `.env` (it is pre-configured with local defaults):
    ```bash
    cp .env.example .env
    ```

---

## 🐋 Running via Docker (Recommended)
You can run the entire infrastructure (including PostgreSQL and the API server) in a single command using Docker Compose:

```bash
docker-compose up --build -d
```

*   **API Server**: `http://localhost:8000`
*   **PostgreSQL**: Port `5432`
*   **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Alternative Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ⚙️ Running Migrations
When starting the Postgres server, apply database schema migrations:

```bash
# Apply migrations to latest
alembic upgrade head

# Generate an autodetected migration script after adding models
alembic revision --autogenerate -m "Add authentication models"
```

---

## 🧪 Running Integration Tests
We provide a comprehensive, async test suite utilizing an isolated, highly optimized in-memory SQLite database, requiring zero databases to be running.

Activate your environment and run:
```bash
pytest
```

---

## 📋 Endpoints Registry

### 🔍 Health Check
*   `GET /api/v1/health` - Check server status and dynamic Postgres connectivity

### 🔐 Authentication Module
*   `POST /api/v1/auth/register` - Create a new user profile
*   `POST /api/v1/auth/login` - Authenticate credentials, returns Access (15m) + Refresh (7d) tokens
*   `POST /api/v1/auth/refresh` - Request a new JWT pair using Refresh Token (Rotation active)
*   `POST /api/v1/auth/logout` - Invalidate active Refresh Token session

### 👥 Users Module
*   `GET /api/v1/users/me` - [Protected] Fetches current active profile
*   `GET /api/v1/users/admin-only` - [Protected/Admin] Administrative endpoint
