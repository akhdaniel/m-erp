from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Create async engine for database operations
async_engine = create_async_engine(
  settings.database_url,
  echo=settings.debug,
  future=True,
  pool_pre_ping=True,
  pool_recycle=300,
)

# Create async session factory
async_session_factory = sessionmaker(
  bind=async_engine,
  class_=AsyncSession,
  expire_on_commit=False,
  autoflush=True,
  autocommit=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncSession:
  """
  Dependency function to get database session.
  Yields an async database session and ensures it's closed after use.
  """
  async with async_session_factory() as session:
    try:
      yield session
      await session.commit()
    except Exception:
      await session.rollback()
      raise
    finally:
      await session.close()


async def init_db():
  """
  Initialize database by creating all tables.
  This should be called during application startup.
  """
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


async def close_db():
  """
  Close database connections.
  This should be called during application shutdown.
  """
  await async_engine.dispose()