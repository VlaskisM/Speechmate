# Architecture

**Analysis Date:** 2026-02-26

## Pattern Overview

**Overall:** Layered architecture with clear separation of concerns following Domain-Driven Design principles.

**Key Characteristics:**
- Three-tier layer separation: Web (API/Routes) → Services → Repositories
- Abstract repository pattern for database abstraction
- Dependency injection via direct class instantiation in services
- Async-first design using FastAPI and SQLAlchemy async engine
- Schema validation via Pydantic models

## Layers

**Web Layer (API Routes):**
- Purpose: Handle HTTP requests, validate input schemas, return responses
- Location: `data_ingress/src/web/routes/`
- Contains: FastAPI APIRouter instances, HTTP endpoint handlers
- Depends on: Services layer for business logic
- Used by: HTTP clients

**Service Layer (Business Logic):**
- Purpose: Orchestrate business operations, coordinate repositories, transform data between schemas and entities
- Location: `data_ingress/src/services/`
- Contains: Service classes with async methods, data transformation logic
- Depends on: Repository layer for data access, schemas for input/output
- Used by: Web layer routes

**Repository Layer (Data Access):**
- Purpose: Abstract database operations, provide CRUD interface independent of ORM details
- Location: `data_ingress/src/db/relational/repositories/`
- Contains: Abstract repository interfaces and concrete implementations using SQLAlchemy
- Depends on: Entity layer (ORM models), AsyncSession from database configuration
- Used by: Service layer

**Entity Layer (Database Models):**
- Purpose: Define database table schemas using SQLAlchemy ORM
- Location: `data_ingress/src/db/relational/entities/`
- Contains: SQLAlchemy declarative model classes
- Depends on: SQLAlchemy DeclarativeBase
- Used by: Repository layer for queries and inserts

**Configuration Layer:**
- Purpose: Centralize external configuration and database initialization
- Location: `data_ingress/src/configs/`
- Contains: Pydantic Settings for environment-based configuration, database engine and session factory
- Depends on: Environment variables
- Used by: All other layers

## Data Flow

**Create Recording Request:**

1. HTTP POST request → `data_ingress/src/web/routes/recording.py` endpoint
2. FastAPI validates input against `RecordingCreate` schema
3. Route handler instantiates `RecordingService()` and calls `create(data)`
4. Service opens async session: `async with async_session() as session`
5. Service instantiates `RecordingRepository(session)` with active session
6. Repository creates `Recording` entity and adds to session
7. Service commits transaction: `await session.commit()`
8. Service refreshes entity to get database-generated ID: `await session.refresh(recording)`
9. Service transforms entity to response schema via `_to_response()`
10. Response returned to client as `RecordingResponse` JSON

**Retrieve Recordings Request:**

1. HTTP GET request → `data_ingress/src/web/routes/recording.py` endpoint
2. Route handler calls `service.get_all()`
3. Service opens session and creates repository instance
4. Repository executes SQLAlchemy query: `select(Recording)` with optional WHERE clause
5. Results returned as list of entities
6. Service transforms entities to list of `RecordingResponse` objects
7. Response returned to client as JSON array

**State Management:**
- Session lifecycle: Opened per request in service layer, committed/rolled back at end of service method
- Transaction management: Explicit commits required after write operations
- Entity lifecycle: Entities managed by SQLAlchemy session, auto-expired on commit
- Session `expire_on_commit=False` configuration prevents reload on commit

## Key Abstractions

**AbstractRecordingRepository:**
- Purpose: Define contract for recording data operations independent of implementation
- Examples: `data_ingress/src/db/relational/repositories/recording.py` (lines 9-33)
- Pattern: Abstract Base Class with @abstractmethod decorators defining get_all(), get_by_id(), create(), delete() operations

**Recording Entity:**
- Purpose: Represent database table structure in Python code
- Examples: `data_ingress/src/db/relational/entities/recording.py`
- Pattern: SQLAlchemy declarative model with Mapped type hints for type safety

**Pydantic Schemas:**
- Purpose: Validate request/response data and provide serialization contracts
- Examples: `RecordingCreate`, `RecordingResponse` in `data_ingress/src/web/schemas/recording.py`
- Pattern: Pydantic BaseModel with `from_attributes=True` config for ORM conversion

**RecordingService:**
- Purpose: Coordinate repository operations and handle data transformations
- Examples: `data_ingress/src/services/recording.py`
- Pattern: Static methods for transformation (`_to_response`), async instance methods for operations

## Entry Points

**Application Start:**
- Location: `data_ingress/run.py`
- Triggers: Direct Python execution or uvicorn command
- Responsibilities: Bootstrap FastAPI application with uvicorn server on port 8000

**Web Application Instance:**
- Location: `data_ingress/src/web/web.py`
- Triggers: Imported by uvicorn during startup
- Responsibilities: Create FastAPI app instance, register all routers (service_router, recording_router)

**HTTP Endpoints:**
- GET `/health` → Health check endpoint in `data_ingress/src/web/routes/health_check.py`
- GET `/recordings` → List all recordings in `data_ingress/src/web/routes/recording.py`
- POST `/recordings` → Create new recording in `data_ingress/src/web/routes/recording.py`

## Error Handling

**Strategy:** Implicit HTTP exception propagation with FastAPI error handling.

**Patterns:**
- Database errors: No explicit catch blocks; SQLAlchemy exceptions propagate as 500 Internal Server Error
- Validation errors: Pydantic validation failures automatically return 422 Unprocessable Entity
- Not found: Service methods return None for non-existent items; routes don't currently handle None responses
- Transaction failures: SQLAlchemy rollback on exception; no retry logic implemented

## Cross-Cutting Concerns

**Logging:** Not implemented. No logger configured in any layer.

**Validation:** Performed by Pydantic schemas at route entry point. Repository and service layers assume valid input.

**Authentication:** Not implemented. No auth middleware or user context tracking.

**Database Transactions:** Managed per-service-call in try-finally-like pattern using context managers. Commit must be explicit.

---

*Architecture analysis: 2026-02-26*
