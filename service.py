from typing import Callable

from sqlalchemy import select

from db.engine import get_async_session
from db.models import UserDB
from schemas import UserDTO


class UserCrudHandler:
    """ We pass sessionmaker func to methods as an argument. It looks a bit strange
    but prevent us from using the same Session in multiple async tasks at once """

    async def get_user(self, user_id: int, func: Callable) -> UserDB:
        session = func()
        async with session:
            statement = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(statement)
            return result.scalar()

    async def add_user(self, user: UserDTO) -> UserDB:
        async with get_async_session() as session:
            async with session.begin():
                db_user = UserDB(
                    **user.model_dump()
                )
                session.add(db_user)
            await session.refresh(db_user)
            return db_user
