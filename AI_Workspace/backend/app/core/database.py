"""
Shared Database Module

Provides async SQLAlchemy engine and session factory.
Each agent can also have its own isolated database via get_agent_engine().
"""

import logging
from pathlib import Path
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import get_settings, get_agent_data_dir

logger = logging.getLogger("botivate.core.database")


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


@lru_cache()
def get_engine():
    """Get the shared async database engine."""
    settings = get_settings()
    # Ensure the database directory exists
    db_url = settings.database_url
    if "sqlite" in db_url:
        db_path = db_url.split("///")[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_async_engine(db_url, echo=False)
    return engine


@lru_cache()
def get_session_factory():
    """Get the shared async session factory."""
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """FastAPI dependency — yields an async database session."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_agent_engine(agent_name: str):
    """Get an isolated async engine for a specific agent."""
    data_dir = get_agent_data_dir(agent_name)
    db_path = data_dir / f"{agent_name}.db"
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)


def get_agent_session_factory(agent_name: str):
    """Get an isolated async session factory for a specific agent."""
    engine = get_agent_engine(agent_name)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create all shared tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Shared database initialized")


async def init_agent_db(agent_name: str, base_class=None):
    """Create all tables for a specific agent's database."""
    engine = get_agent_engine(agent_name)
    target_base = base_class or Base
    async with engine.begin() as conn:
        await conn.run_sync(target_base.metadata.create_all)
    logger.info(f"Agent database initialized: {agent_name}")
