import asyncio
from typing import AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager, contextmanager
import logging

from bot.config import config
from bot.models import Base

logger = logging.getLogger(__name__)

# Database engines
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def get_database_url(is_async: bool = False) -> str:
    """Get database URL with proper driver"""
    url = config.DATABASE_URL
    
    if url.startswith("sqlite:///"):
        if is_async:
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")
        else:
            return url
    elif url.startswith("postgresql://"):
        if is_async:
            return url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            return url.replace("postgresql://", "postgresql+psycopg2://")
    elif url.startswith("mysql://"):
        if is_async:
            return url.replace("mysql://", "mysql+aiomysql://")
        else:
            return url.replace("mysql://", "mysql+pymysql://")
    
    return url


def init_database():
    """Initialize database connections"""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    # Synchronous engine
    sync_url = get_database_url(is_async=False)
    
    if sync_url.startswith("sqlite"):
        engine = create_engine(
            sync_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=config.LOG_LEVEL.lower() == "debug"
        )
    else:
        engine = create_engine(
            sync_url,
            pool_size=10,
            max_overflow=20,
            echo=config.LOG_LEVEL.lower() == "debug"
        )
    
    # Asynchronous engine
    async_url = get_database_url(is_async=True)
    
    if async_url.startswith("sqlite"):
        async_engine = create_async_engine(
            async_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=config.LOG_LEVEL.lower() == "debug"
        )
    else:
        async_engine = create_async_engine(
            async_url,
            pool_size=10,
            max_overflow=20,
            echo=config.LOG_LEVEL.lower() == "debug"
        )
    
    # Session makers
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )
    
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )
    
    logger.info("Database connections initialized")


async def create_tables():
    """Create all tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


def create_tables_sync():
    """Create all tables synchronously"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (sync)")


@contextmanager
def get_db() -> Session:
    """Get synchronous database session"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchronous database session"""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Async database session error: {e}")
            raise
        finally:
            await session.close()


class DatabaseManager:
    """Database manager for handling connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_local = None
        self.async_session_local = None
    
    async def initialize(self):
        """Initialize database manager"""
        init_database()
        await create_tables()
        logger.info("Database manager initialized")
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")
    
    @contextmanager
    def get_session(self) -> Session:
        """Get synchronous database session"""
        with get_db() as session:
            yield session
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get asynchronous database session"""
        async with get_async_db() as session:
            yield session


# Global database manager instance
db_manager = DatabaseManager()


# Database event handlers
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable SQLite foreign key support"""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Health check functions
async def check_database_health() -> dict:
    """Check database health"""
    try:
        async with get_async_db() as session:
            result = await session.execute("SELECT 1")
            result.scalar()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


def check_database_health_sync() -> dict:
    """Check database health synchronously"""
    try:
        with get_db() as session:
            session.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


# Migration utilities
async def run_migrations():
    """Run database migrations"""
    try:
        # For now, just create tables
        await create_tables()
        logger.info("Database migrations completed")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def backup_database(backup_path: str):
    """Backup SQLite database"""
    if not config.DATABASE_URL.startswith("sqlite"):
        raise ValueError("Backup only supported for SQLite databases")
    
    import shutil
    import os
    
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
    else:
        raise FileNotFoundError(f"Database file not found: {db_path}")


# Database initialization function for startup
async def init_db_on_startup():
    """Initialize database on application startup"""
    try:
        await db_manager.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Database cleanup function for shutdown
async def cleanup_db_on_shutdown():
    """Cleanup database on application shutdown"""
    try:
        await db_manager.close()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        raise