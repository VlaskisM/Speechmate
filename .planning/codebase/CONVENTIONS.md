# Coding Conventions

**Analysis Date:** 2026-02-26

## Naming Patterns

**Files:**
- Lowercase with underscores: `recording.py`, `health_check.py`, `db.py`
- Module files follow resource/domain names: `recording.py` for Recording entity/service/repository
- Test files follow pattern: Not detected in current codebase

**Functions:**
- Snake_case: `get_all()`, `get_by_id()`, `create_recording()`, `async def`
- Async functions are prefixed with async keyword, no special naming convention
- Static methods use `@staticmethod` decorator: `RecordingService._to_response()`, `RecordingService._to_response_list()`
- Private/internal methods prefixed with underscore: `_to_response()`, `_to_response_list()`

**Variables:**
- Snake_case: `badge_id`, `user_id`, `recording_id`, `file_url`, `session`
- Database column names use underscores: `badge_id`, `file_url`, `user_id`
- Abbreviated names used in some contexts: `ts` for timestamp, `repo` for repository instance

**Types:**
- PascalCase for classes: `Recording`, `RecordingResponse`, `RecordingCreate`, `RecordingService`, `RecordingRepository`, `AbstractRecordingRepository`
- PascalCase for Pydantic models: `BaseResponse`, `BaseModel`
- Type hints use Python 3.10+ union syntax: `Recording | None`, `list[Recording]`, `list[RecordingResponse]`

## Code Style

**Formatting:**
- No explicit formatter detected (no .prettierrc, black config, or similar)
- Manual formatting observed:
  - 4-space indentation (standard Python)
  - Imports at top of file
  - Blank lines between class definitions and methods
  - Single blank line between method definitions within a class

**Linting:**
- No linting configuration detected (.pylintrc, .flake8, pyproject.toml not present)
- Code follows standard PEP 8 conventions implicitly

## Import Organization

**Order:**
1. Standard library imports (`collections.abc`, `pathlib.Path`, `sqlalchemy`)
2. Third-party imports (`fastapi`, `pydantic`, `sqlalchemy.ext.asyncio`)
3. Local relative imports from `src` package

**Path Aliases:**
- No path aliases detected
- All imports use absolute paths from project root: `from src.db.relational.db import async_session`
- Consistent pattern: `from src.[domain].[layer] import [class/function]`

**Pattern Examples:**
```python
# Standard library
from collections.abc import AsyncGenerator
from pathlib import Path

# Third-party
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Local imports
from src.configs.db import postgres_settings
from src.db.relational.repositories.recording import RecordingRepository
from src.web.schemas.recording import RecordingCreate, RecordingResponse
```

## Error Handling

**Patterns:**
- Early return pattern for None checks: `if recording is None: return None`
- Boolean return for operations: `delete()` returns `True` or `False` to indicate success
- HTTPException from FastAPI for API errors: `from fastapi import HTTPException` (imported but not yet used in routes)
- No try-catch blocks observed in current code
- No custom exception classes defined
- Repository layer handles None cases before service layer

**Examples:**
```python
# Repository layer - None handling
async def get_by_id(self, recording_id: int) -> Recording | None:
    return await self.session.get(Recording, recording_id)

# Service layer - None propagation
async def get_by_id(self, recording_id: int) -> RecordingResponse | None:
    async with async_session() as session:
        repo = RecordingRepository(session)
        recording = await repo.get_by_id(recording_id)
        if recording is None:
            return None
        return self._to_response(recording)

# Delete operation - boolean return
async def delete(self, recording_id: int) -> bool:
    recording = await self.get_by_id(recording_id)
    if recording is None:
        return False
    await self.session.delete(recording)
    return True
```

## Logging

**Framework:** Not detected - no logging imports found

**Patterns:**
- No logging infrastructure currently implemented
- No use of Python logging module
- No structured logging

## Comments

**When to Comment:**
- Minimal commenting observed
- No docstrings on functions or classes
- No JSDoc/docstring conventions established

**Code Examples:**
```python
# From requirements.txt - Russian comments used
asyncpg==0.31.0 # Асинхронный PostgreSQL дравер
sqlalchemy[asyncio]==2.0.35 # Асинхронный SQLAlchemy
```

## Function Design

**Size:** Small to medium functions (5-15 lines typical)

**Parameters:**
- Typed parameters in all functions
- Repository methods accept domain data directly: `create(badge_id: str, ts: int, file_url: str, user_id: int)`
- Service methods accept Pydantic models: `create(data: RecordingCreate)`
- No default parameter values observed in current code

**Return Values:**
- Type hints on all returns
- Explicit return type annotations: `-> RecordingResponse`, `-> list[Recording]`, `-> bool`, `-> None`
- Union types for optional returns: `-> Recording | None`

**Example:**
```python
async def create(self, data: RecordingCreate) -> RecordingResponse:
    async with async_session() as session:
        repo = RecordingRepository(session)
        recording = await repo.create(
            badge_id=data.badge_id,
            ts=data.ts,
            file_url=data.file_url,
            user_id=data.user_id,
        )
        await session.commit()
        await session.refresh(recording)
        return self._to_response(recording)
```

## Module Design

**Exports:**
- No explicit `__all__` declarations
- Imports are selective (only importing needed classes)
- Barrel files (`__init__.py`) exist but are empty

**Barrel Files:**
- Location: `src/configs/__init__.py`, `src/services/__init__.py`, `src/db/__init__.py`, `src/web/__init__.py`, etc.
- Pattern: All `__init__.py` files are empty (no re-exports)
- Import directly from modules, not from packages

## Async/Await Conventions

**Async Pattern:**
- All data access methods are async: `async def create()`, `async def get_all()`, `async def delete()`
- Session context manager used: `async with async_session() as session:`
- Commit/refresh explicitly called after mutations: `await session.commit()`, `await session.refresh(recording)`
- No blocking I/O in service layer

**Example:**
```python
async def create(self, data: RecordingCreate) -> RecordingResponse:
    async with async_session() as session:
        repo = RecordingRepository(session)
        recording = await repo.create(...)
        await session.commit()
        await session.refresh(recording)
        return self._to_response(recording)
```

## Dependency Injection

**Pattern:**
- Service instantiation in route handlers: `service = RecordingService()`
- Repository instantiation within service methods: `repo = RecordingRepository(session)`
- Database session passed to repository constructor: `RecordingRepository(session)`
- No dependency injection framework used (FastAPI's Depends not utilized)

**Example:**
```python
# In recording.py route
service = RecordingService()

@router.post("/", response_model=RecordingResponse, status_code=201)
async def create_recording(data: RecordingCreate):
    return await service.create(data)
```

---

*Convention analysis: 2026-02-26*
