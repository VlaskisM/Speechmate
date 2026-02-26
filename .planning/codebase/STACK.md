# Technology Stack

**Analysis Date:** 2026-02-26

## Languages

**Primary:**
- Python 3.x - Backend API and data ingress services

## Runtime

**Environment:**
- Python runtime (version not explicitly pinned in project files)

**Package Manager:**
- pip - Manages Python dependencies
- Lockfile: `requirements.txt` present

## Frameworks

**Core:**
- FastAPI 0.115.8 - Web framework for building REST APIs with async support
- Uvicorn 0.38.0 - ASGI server for running FastAPI applications

**Database ORM:**
- SQLAlchemy[asyncio] 2.0.35 - Async-capable SQL toolkit and object-relational mapper
- Alembic 1.18.4 - Database migration management tool

**Configuration Management:**
- Pydantic 2.10.6 - Data validation and settings management
- Pydantic-settings 2.8.0 - Settings management with environment variable support

## Key Dependencies

**Critical:**
- asyncpg 0.31.0 - High-performance asynchronous PostgreSQL driver for SQLAlchemy async operations
- psycopg[binary] 3.3.3 - Synchronous PostgreSQL driver, required for Alembic migrations (cannot use async driver with migrations)

**Infrastructure:**
- All dependencies are Python packages; no external SDK integrations detected

## Configuration

**Environment:**
- Configuration via `.env` file
- Pydantic-settings loads environment variables from `.env` file at root level
- Database connection settings: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Settings class: `DatabaseSettings` in `data_ingress/src/configs/db.py`

**Build:**
- Entry point: `/e/VisualStudioCodeProjects/Speechmate/run.py` - Root launcher that invokes data_ingress subprocess
- Application entry point: `data_ingress/run.py` - Starts Uvicorn server on host 0.0.0.0, port 8000 with reload enabled
- FastAPI app initialization: `data_ingress/src/web/web.py`

## Platform Requirements

**Development:**
- Python 3.x runtime
- pip package manager
- PostgreSQL 17 (via Docker Compose)

**Production:**
- Python 3.x runtime
- PostgreSQL 17 or compatible
- Containerized deployment (Docker support evident from docker-compose.yml)

## Database

**Type:** PostgreSQL 17
- Async connection pool via SQLAlchemy async engine
- Synchronous connection fallback for migrations
- Connection URL format: `postgresql+asyncpg://user:pass@host:port/dbname` (async)
- Connection URL format: `postgresql+psycopg://user:pass@host:port/dbname` (sync/migrations)

## Deployment

**Containerization:**
- Docker Compose configuration: `docker-compose.yml`
- PostgreSQL service: `postgres:17` image
- Volume: `postgres_data` for persistent database storage
- Environment-based configuration for database credentials

---

*Stack analysis: 2026-02-26*
