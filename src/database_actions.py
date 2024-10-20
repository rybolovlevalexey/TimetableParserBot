from pydantic_models import UserInDB
from services import AuthActions
from database_models import async_session_maker, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DataBaseActions:
    def __init__(self):
        self.auth_actions = AuthActions()

    # Получение пользователя из базы данных
    async def get_user(self, username: str) -> UserInDB | None:
        session: AsyncSession
        async with async_session_maker() as session:
            query = select(User).where(username == User.login)
            query_result = await session.execute(query)
            result = query_result.scalars().all()
            if len(result) == 1:
                cur_user = result[0]
                return UserInDB.model_validate(cur_user)
            return None

    # Аутентификация пользователя
    async def authenticate_user(self, username: str, password: str) -> None | UserInDB:
        user = await self.get_user(username)
        if not user:
            return None
        if not self.auth_actions.verify_password(password, user.hashed_password):
            return None
        return user
