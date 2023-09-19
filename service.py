from typing import Callable

from sqlalchemy import select

from db.models import UserDB
from schemas import UserDTO


class UserCrudHandler:
    """
    We pass sessionmaker func to methods as an argument. It looks a bit strange
    but prevent us from using the same Session in multiple async tasks at once
    """

    async def get_user(self, user_id: int, sessionmaker: Callable) -> UserDB:
        session = sessionmaker()
        async with session:
            statement = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(statement)
            return result.scalar()

    async def add_user(self, user: UserDTO, sessionmaker: Callable) -> UserDB:
        """
        I should definitely use context manager to handle the transaction like:
        async with get_async_session() as session:
            async with session.begin():
                db_user = UserDB(
                    **user.model_dump()
                )
                session.add(db_user)
            await session.refresh(db_user)
        The problem appeared in tests with __aenter__ attribute in the second context manager
        """
        session = sessionmaker()

        db_user = UserDB(
            **user.model_dump()
        )

        async with session:
            session.begin()
            try:
                session.add(db_user)
            except Exception:
                session.rollback()
            else:
                await session.commit()
                await session.refresh(db_user)

        return db_user
