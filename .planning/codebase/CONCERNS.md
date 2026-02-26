# Codebase Concerns

**Analysis Date:** 2026-02-26

## Tech Debt

**Incomplete Error Handling:**
- Issue: HTTPException is imported in `src/web/routes/recording.py` but never used. Routes lack proper exception handling for database operations and validation failures.
- Files: `data_ingress/src/web/routes/recording.py`
- Impact: API requests that fail will return generic 500 errors instead of meaningful HTTP status codes. Clients cannot distinguish between validation errors, not found, and server failures.
- Fix approach: Add try-except blocks in route handlers that catch repository exceptions and convert them to appropriate HTTPException responses (400 for validation, 404 for not found, 500 for database failures).

**Naive Service Instantiation in Routes:**
- Issue: `RecordingService()` is instantiated as a module-level variable in routes, creating a single shared instance across all requests.
- Files: `data_ingress/src/web/routes/recording.py` (line 7)
- Impact: If the service maintains state or has request-specific dependencies in future iterations, shared state could cause issues. Currently not critical but violates dependency injection best practices.
- Fix approach: Move service instantiation into route handlers or use FastAPI dependency injection (FastAPI Depends).

**Hardcoded Configuration in Run Script:**
- Issue: Host and port are hardcoded in the run script with reload=True enabled, which causes auto-restart on file changes.
- Files: `data_ingress/run.py` (lines 4-8)
- Impact: Running the application in production with auto-reload could cause instability. Different deployment environments (dev, staging, prod) cannot use the same script.
- Fix approach: Move configuration (host, port, reload flag) to environment variables or config files based on environment.

**Database Connection Not Pooled:**
- Issue: `create_async_engine` in `src/db/relational/db.py` has no explicit pool configuration.
- Files: `data_ingress/src/db/relational/db.py` (line 7)
- Impact: Under high concurrent load, connection pool exhaustion could occur. Default pool size may be inadequate for production.
- Fix approach: Add explicit pool configuration with `pool_size` and `max_overflow` parameters based on expected load.

**Weak Database Authentication:**
- Issue: Docker Compose uses `POSTGRES_HOST_AUTH_METHOD: trust` which disables password authentication.
- Files: `docker-compose.yml` (line 10)
- Impact: Security risk in any environment where PostgreSQL is accessible from untrusted networks. Any client can connect without credentials.
- Fix approach: Remove the `trust` authentication method - use default password authentication. Only use `trust` for local-only development with explicit documentation.

## Known Issues

**Potential Session Management Issue:**
- Issue: `async_session` has `expire_on_commit=False`, which defers lazy loading after session closes.
- Files: `data_ingress/src/db/relational/db.py` (line 9)
- Symptoms: If response models try to access lazy-loaded relationships after session closes, they will fail silently or raise `DetachedInstanceError`.
- Trigger: Access any ORM relationship that wasn't eagerly loaded in a route response context.
- Workaround: Use SQLAlchemy's `selectinload` in repository queries to eagerly load relationships, or ensure all accessed attributes are loaded before session closes.

**Missing Transaction Rollback on Failure:**
- Issue: Service layer creates sessions but only commits on success. No explicit rollback on failure, relying on context manager cleanup.
- Files: `data_ingress/src/services/recording.py` (lines 16-27, 55-61)
- Symptoms: If an exception occurs after operations but before commit, changes may not be properly rolled back depending on exception type.
- Trigger: Raise an exception within a service method's async with block.
- Workaround: Wrap operations in explicit try-except with rollback statements.

## Security Considerations

**Credentials in Database Config:**
- Risk: Database credentials are loaded from `.env` file and constructed into URLs with plaintext passwords.
- Files: `data_ingress/src/configs/db.py` (line 14)
- Current mitigation: `.env` file is not committed (listed in `.gitignore`), credentials not exposed in code.
- Recommendations:
  - Use connection string environment variable instead of constructing from parts
  - Implement secrets rotation for production
  - Consider using IAM/managed credentials for cloud PostgreSQL instead of user/password

**No Input Validation Constraints:**
- Risk: `RecordingCreate` schema lacks validation constraints (string length, integer ranges, URL format).
- Files: `data_ingress/src/web/schemas/recording.py` (lines 4-8)
- Current mitigation: Pydantic provides basic type validation.
- Recommendations:
  - Add field validators: `badge_id` length limits, `ts` positive integer check, `file_url` URL validation
  - Add `Field(description=...)` for OpenAPI documentation
  - Consider max_length constraints to prevent large payload attacks

**No API Authentication:**
- Risk: All endpoints are publicly accessible with no authentication or authorization.
- Files: `data_ingress/src/web/routes/recording.py`
- Current mitigation: None.
- Recommendations:
  - Add bearer token or API key authentication using FastAPI security
  - Implement user_id validation to ensure users can only access their own recordings
  - Add rate limiting to prevent abuse

## Performance Bottlenecks

**N+1 Query Vulnerability:**
- Problem: Service methods call repository methods that return ORM objects, which may lazy-load relationships when accessed in response models.
- Files: `data_ingress/src/services/recording.py` (lines 12, 32-33), `data_ingress/src/db/relational/repositories/recording.py` (lines 53-55)
- Cause: Repository methods execute SELECT queries, but if response models access foreign keys or relationships, additional queries execute per row.
- Improvement path: Add eager loading (selectinload) to repository queries. Use Pydantic models that don't reference ORM relationships.

**Full Table Scan on List Endpoints:**
- Problem: `get_all()` endpoint loads all recordings without pagination or filtering.
- Files: `data_ingress/src/web/routes/recording.py` (line 10-12), `data_ingress/src/db/relational/repositories/recording.py` (line 53-55)
- Cause: No LIMIT/OFFSET in query, no pagination parameters in API.
- Improvement path: Add pagination (limit, offset) parameters to route, implement offset-based or cursor-based pagination in repository.

**Missing Database Indexes:**
- Problem: Recording entity has queries on `user_id` and `badge_id` but no indexes defined.
- Files: `data_ingress/src/db/relational/entities/recording.py`
- Cause: ORM entity lacks index definitions, migrations may not have created indexes.
- Improvement path: Add `Index` to frequently queried columns in entity definition, run migrations to create indexes.

## Fragile Areas

**Repository-Service Tight Coupling:**
- Files: `data_ingress/src/services/recording.py`, `data_ingress/src/db/relational/repositories/recording.py`
- Why fragile: Service directly instantiates `RecordingRepository` within async context. If repository interface changes, service breaks. Abstract base class exists but is not used as a type hint or injected.
- Safe modification: Inject repository as a parameter to service methods, use abstract class as type hint, or use FastAPI's dependency system to provide repositories.
- Test coverage: Service layer has no obvious unit tests to catch interface mismatches.

**Manual Session Management:**
- Files: `data_ingress/src/services/recording.py` (all methods)
- Why fragile: Every service method manually opens/closes database sessions. Code duplication and easy to forget commit() or refresh(). If session handling rules change, must update all methods.
- Safe modification: Create a decorator or context manager for session handling to centralize session lifecycle management.
- Test coverage: No mock session handling visible, integration tests would be needed.

**Bare Exception Imports:**
- Files: `data_ingress/src/web/routes/recording.py` (imports HTTPException but doesn't use it)
- Why fragile: Dead imports indicate incomplete refactoring. Route handlers don't catch exceptions, so unhandled exceptions propagate to FastAPI's default handler.
- Safe modification: Complete the error handling implementation with try-except blocks and HTTPException raises. Remove unused imports.
- Test coverage: Error scenarios are not tested.

## Scaling Limits

**Single Service Instance per Route:**
- Current capacity: Handles concurrent requests up to async event loop capacity.
- Limit: Service is instantiated once; if service becomes stateful or holds resources, bottleneck occurs.
- Scaling path: Use dependency injection to create service instances per request or scope.

**Database Connection Pool (Unconfigured):**
- Current capacity: Default SQLAlchemy async pool (5 concurrent connections with 10 overflow).
- Limit: With dozens of concurrent requests, pool exhaustion could occur, causing "QueuePool timeout" errors.
- Scaling path: Set `pool_size=20, max_overflow=40` or higher based on load testing. Consider connection pooling middleware (pgBouncer).

**Unbounded List Endpoint:**
- Current capacity: Can serve small datasets (< 1000 records) without performance degradation.
- Limit: Loading all recordings into memory without pagination will fail with large datasets.
- Scaling path: Implement pagination with configurable page size, use streaming responses for large exports.

## Dependencies at Risk

**No Dependency Version Pinning:**
- Risk: `requirements.txt` pins minor versions (e.g., `fastapi==0.115.8`) but `sqlalchemy[asyncio]==2.0.35` could have breaking changes in asyncio support.
- Impact: If SQLAlchemy 2.0.x introduces asyncio regression, application breaks on next pip install.
- Migration plan: Use `>=` with version ceilings (e.g., `sqlalchemy>=2.0.35,<3.0.0`) or lock with pip-tools / Poetry.

**Alembic Configuration Incomplete:**
- Risk: Database migrations are in place but no instructions for running migrations on deployment.
- Impact: Developers may forget to run migrations before testing, causing schema mismatches.
- Migration plan: Document migration process, add pre-startup checks that verify migration status.

## Missing Critical Features

**No Database Migration Verification:**
- Problem: Application starts without verifying if pending migrations exist. If migrations are skipped, app may run against mismatched schema.
- Blocks: Reliable deployment and testing across environments.

**No Health Check Database Connectivity:**
- Problem: Health endpoint returns "ok" without checking database connection.
- Blocks: Load balancers cannot verify database availability; failed database results in app serving stale cache indefinitely.

**No Logging System:**
- Problem: No structured logging, audit trail, or error tracking integrated.
- Blocks: Production debugging, audit compliance, error monitoring.

**No Request ID Tracing:**
- Problem: No correlation IDs on requests for distributed tracing.
- Blocks: Tracing errors across multiple services or retries.

## Test Coverage Gaps

**No Unit Tests:**
- What's not tested: Service layer logic, repository queries, schema validation, error handling.
- Files: `data_ingress/src/services/recording.py`, `data_ingress/src/db/relational/repositories/recording.py`
- Risk: Breaking changes to business logic go undetected. Refactoring is high-risk.
- Priority: High

**No Integration Tests:**
- What's not tested: End-to-end API flows, database integration, async session handling, transaction behavior.
- Files: `data_ingress/src/web/routes/recording.py`
- Risk: API contract changes and database failures discovered only in production.
- Priority: High

**No Error Scenario Testing:**
- What's not tested: Invalid input handling, missing records, database connection failures, constraint violations.
- Files: All route and service files.
- Risk: Unhandled exceptions crash the application or return invalid responses.
- Priority: High

---

*Concerns audit: 2026-02-26*
