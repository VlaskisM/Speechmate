# External Integrations

**Analysis Date:** 2026-02-26

## APIs & External Services

**No external API integrations detected** - The application exposes REST API endpoints but does not consume external APIs.

## Data Storage

**Databases:**
- PostgreSQL 17 (primary relational database)
  - Connection: Environment variables `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
  - Client: SQLAlchemy 2.0.35 with asyncpg driver
  - Configuration: `data_ingress/src/configs/db.py` - `DatabaseSettings` class
  - Engine: Async engine created in `data_ingress/src/db/relational/db.py`
  - Migrations: Alembic 1.18.4 - migration files in `data_ingress/migrations/`
  - ORM Entities: `data_ingress/src/db/relational/entities/recording.py` - Recording model

**File Storage:**
- Local filesystem only - No external file storage service detected
- File URLs stored as strings in Recording entity (`file_url` field)
- Application stores file paths/URLs but does not integrate with S3, GCS, or similar

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Custom/None - No authentication/authorization system detected
- API endpoints in `data_ingress/src/web/routes/recording.py` and `data_ingress/src/web/routes/health_check.py` have no auth middleware
- All endpoints are publicly accessible

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- No explicit logging framework integrated (no Sentry, DataDog, etc.)
- Standard Python logging available but not configured

## CI/CD & Deployment

**Hosting:**
- Not specified - Infrastructure is containerized and deployment-agnostic
- Docker Compose configuration suggests local/development or container orchestration deployment

**CI Pipeline:**
- Not detected - No GitHub Actions, GitLab CI, or other CI/CD configuration files found

## Environment Configuration

**Required env vars:**
- `DB_HOST` - PostgreSQL hostname
- `DB_PORT` - PostgreSQL port (integer)
- `DB_USER` - PostgreSQL username
- `DB_PASSWORD` - PostgreSQL password
- `DB_NAME` - PostgreSQL database name

**Secrets location:**
- `.env` file at repository root (environment variables)
- Loaded via Pydantic-settings in `data_ingress/src/configs/db.py`
- File should contain: `DB_HOST=`, `DB_PORT=`, `DB_USER=`, `DB_PASSWORD=`, `DB_NAME=`

## REST API Endpoints

**Recording Service:**
- `GET /recordings/` - Retrieve all recordings
  - Response: List of RecordingResponse objects
  - Schema: `data_ingress/src/web/schemas/recording.py`

- `POST /recordings/` - Create new recording
  - Request body: RecordingCreate (badge_id, ts, file_url, user_id)
  - Response: RecordingResponse with auto-generated id

**Health Check Service:**
- `GET /health` - Service health status
  - Response: BaseResponse with status "ok"
  - Schema: `data_ingress/src/web/schemas/common.py`

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Data Model

**Recording Entity:**
- Location: `data_ingress/src/db/relational/entities/recording.py`
- Fields:
  - `id` (Integer, primary key, auto-increment)
  - `badge_id` (String, required)
  - `ts` (Integer, timestamp, required)
  - `file_url` (String, file reference, required)
  - `user_id` (Integer, required)
- Repository: `data_ingress/src/db/relational/repositories/recording.py`
- Service layer: `data_ingress/src/services/recording.py` with CRUD and query methods

---

*Integration audit: 2026-02-26*
