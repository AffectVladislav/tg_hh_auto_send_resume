from sqlalchemy import BigInteger, String, Text, select, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    resume_id: Mapped[str] = mapped_column(String(38))
    authorization_code: Mapped[str] = mapped_column(String(64))
    cover_letter: Mapped[str] = mapped_column(Text(1000))

    __table_args__ = (UniqueConstraint('user_id', name='uq_user_id'),)


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.async_sessionmaker = async_sessionmaker(engine)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def add_user(self, user_data):
        async with self.async_sessionmaker() as session:
            new_user = User(**user_data)
            session.add(new_user)
            await session.commit()

    async def get_users(self):
        async with self.async_sessionmaker() as session:
            result = await session.execute(select(User))
            return result.scalars().all()


async def async_main():
    db_manager = DatabaseManager(engine)
    await db_manager.create_tables()
