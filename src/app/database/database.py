from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import configs

# Create an asynchronous engine using the provided database URL
engine = create_async_engine(configs.database_url, future=True, echo=True)

# Create a sessionmaker factory for creating asynchronous sessions
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,  # Prevent automatic flushing of the session
)

Base = declarative_base()