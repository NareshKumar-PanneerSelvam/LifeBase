# LifeBase Backend Developer Setup & Operations Guide

This document details the configuration paths for database connection strings and provides a comprehensive guide for developers setting up, running, migrating, and testing the `lifebase-server` FastAPI backend.

---

## 🔌 1. PostgreSQL Connection String Configuration

The PostgreSQL connection string is configured dynamically using an environment-based configuration system. Here is exactly where and how it is defined:

### 1. The Environment Files
*   **Location**: `lifebase-server/.env` (and `lifebase-server/.env.example`)
*   **Key**: `DATABASE_URL`
*   **Standard Local Format**: 
    ```ini
    DATABASE_URL="postgresql://postgres:postgres@localhost:5432/lifebase"
    ```
    *(Note: Using standard `postgresql://` is compatible with other tools, and our code handles driver conversion automatically).*

### 2. Configuration Loader
*   **File**: [`app/core/config.py`](file:///d:/LifeBase/lifebase-server/app/core/config.py)
*   **Role**: Uses `pydantic-settings` to load settings from the `.env` file into a type-safe Python settings model:
    ```python
    class Settings(BaseSettings):
        DATABASE_URL: str
    ```

### 3. Async Engine Initialization (Auto-Swapping Driver)
*   **File**: [`app/core/database.py`](file:///d:/LifeBase/lifebase-server/app/core/database.py)
*   **Role**: Automatically intercepts the database URL and swaps the protocol prefix to `postgresql+asyncpg://` if it was loaded as a standard synchronous connection. This lets us use standard postgres connection formats while strictly executing async-first operations in SQLAlchemy:
    ```python
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    engine = create_async_engine(db_url, echo=settings.DEBUG, future=True)
    ```

### 4. Containerized Environment (Docker Compose)
*   **File**: [`docker-compose.yml`](file:///d:/LifeBase/lifebase-server/docker-compose.yml)
*   **Role**: Overrides the connection string for the `web` container. It routes database queries to the `db` container service within the Docker internal network:
    ```yaml
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/lifebase
    ```

### 5. Database Migrations Loader
*   **File**: [`alembic/env.py`](file:///d:/LifeBase/lifebase-server/alembic/env.py)
*   **Role**: Loads `settings.DATABASE_URL`, converts it to the async driver format, and passes it directly to the Alembic connection pool so that database migrations run on the same environment targets:
    ```python
    config.set_main_option("sqlalchemy.url", db_url)
    ```

---

## 🛠️ 2. Local Virtual Environment Setup

We recommend utilizing the **`uv`** package manager for fast virtual environment builds.

### Step 1: Initialize the Environment
Navigate to the server directory and create a Python 3.12 virtual environment:
```bash
cd d:\LifeBase\lifebase-server
uv venv --python 3.12
```

### Step 2: Activate the Virtual Environment
*   **Windows (PowerShell)**:
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
*   **macOS / Linux**:
    ```bash
    source .venv/bin/activate
    ```

### Step 3: Install Dependencies
Install all runtime, development, and test requirements:
```bash
uv pip install -r pyproject.toml
uv pip install pytest pytest-asyncio httpx aiosqlite
```
*(This automatically installs `bcrypt<5.0.0` to preserve compatibility with `passlib` on Python 3.12, along with `aiosqlite` for isolated database testing).*

### Step 4: Configure Local Variables
Create a local `.env` file from the example template:
```bash
cp .env.example .env
```
Ensure the `DATABASE_URL` matches your local PostgreSQL credentials.

---

## 🐋 3. Running via Docker Compose (Recommended)

Docker Compose orchestrates both the PostgreSQL database service and the FastAPI web server, ensuring a complete runtime connection out of the box.

### Run in Background
```bash
docker-compose up --build -d
```

### Stream Application Logs
```bash
docker-compose logs -f web
```

### Shutdown Services and Retain Volumes
```bash
docker-compose down
```

---

## ⚙️ 4. Running Database Migrations

Database schema migrations are managed via **Alembic**.

### Apply Existing Migrations to Database
Apply all upgrade scripts to catch up with the latest schema state:
```bash
# Activate your venv and run
alembic upgrade head
```

### Autodetect and Generate New Migration Revisions
When you modify or create SQLAlchemy models in `app/models/`, Alembic can compare them against your live database to generate migration scripts:
```bash
alembic revision --autogenerate -m "Describe your schema change"
```
The new script is placed under `alembic/versions/` and can be inspected before applying.

---

## 🧪 5. Running the Test Suite

We provide a robust integration test suite utilizing an isolated **in-memory SQLite database** using `aiosqlite`. Tests are self-contained and run without needing a real PostgreSQL database server active.

### Running Pytest
To run all tests and view clean tracebacks, set your Python Path and run `pytest`:
```bash
# Windows PowerShell
$env:PYTHONPATH="."
.venv\Scripts\pytest -p no:logging -v

# macOS / Linux
PYTHONPATH=. .venv/bin/pytest -p no:logging -v
```

---

## 📋 6. Interactive OpenAPI (Swagger) Documentation

FastAPI automatically parses Pydantic validation schemas to construct self-documenting endpoints.

1.  Start the server locally (or via Docker Compose).
2.  Open your browser and navigate to:
    *   **Interactive Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **Alternative Docs (Redoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
3.  You can use the **"Try it out"** buttons in Swagger UI to execute register, login, refresh, logout, and profile queries directly from the browser.
