from sqlalchemy.future import select
from database.models import DatabaseManager, User
from sqlalchemy.exc import IntegrityError


class UserRequests:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def add_user(self, user_data):
        async with self.db_manager.async_sessionmaker() as session:
            new_user = User(**user_data)
            session.add(new_user)
            try:
                await session.commit()
                return True  # Пользователь успешно добавлен
            except IntegrityError:
                await session.rollback()  # Откат транзакции в случае ошибки
                return False  # Пользователь уже существует

    async def user_exists(self, user_id):
        async with self.db_manager.async_sessionmaker() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()
            return user is not None  # Возвращаем True, если пользователь существует

    async def update_user(self, user_id, update_data):
        async with self.db_manager.async_sessionmaker() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                await session.commit()
                return True
            return False

    async def delete_user(self, user_id):
        async with self.db_manager.async_sessionmaker() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False

    async def get_users(self):
        async with self.db_manager.async_sessionmaker() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def get_user_data(self, user_id):
        async with self.db_manager.async_sessionmaker() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()

            if user:
                return {
                    'user_id': user.user_id,
                    'resume_id': user.resume_id,
                    'authorization_code': user.authorization_code,
                    'cover_letter': user.cover_letter
                }
            return None
