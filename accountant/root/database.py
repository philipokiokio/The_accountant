from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from accountant.root.settings import Settings


settings = Settings()

engine = create_async_engine(url=str(settings.postgres_url))


async_session = async_sessionmaker(engine, expire_on_commit=False)
