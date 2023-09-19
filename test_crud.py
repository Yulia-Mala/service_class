import unittest
from unittest import mock

from sqlalchemy import select

from db.models import UserDB
from schemas import UserDTO
from service import UserCrudHandler


class TestCrud(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUp(self) -> None:
        self.handler = UserCrudHandler()
        self.mocked_session = mock.AsyncMock()

    async def test_get_user(self):
        await self.handler.get_user(user_id=1, sessionmaker=lambda: self.mocked_session)

        expected_statement = str(select(UserDB).where(UserDB.id == 1))
        real_statement = str(self.mocked_session.execute.await_args[0][0])

        self.mocked_session.execute.assert_awaited_once()
        assert real_statement == expected_statement

    async def test_add_user(self):
        user = UserDTO(info="test info")

        await self.handler.add_user(user, sessionmaker=lambda: self.mocked_session)

        self.mocked_session.begin.assert_called_once()
        self.mocked_session.add.assert_called_once()

        passed_user_info = self.mocked_session.add.call_args[0][0].info

        assert passed_user_info == "test info"
