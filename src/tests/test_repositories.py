import pytest

from sqlalchemy import inspect

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.models import User
from src.quests import ExperienceTransaction


class TestUserRepository:
    def test_query_base_case(self, mock_user_repository):
        # Arrange
        query_args = QueryArgs()
        # Act & Assert
        try:
            mock_user_repository._query(query_args)
        except Exception:
            pytest.fail("Empty query failed to build")

    @pytest.mark.parametrize(
        "query_arg",
        [
            {"filter_list": []},
            {"filter_dict": {}},
            {"eager_options": []},
            {"order_by": []},
            {"join_on": []},
            {"group_by": []},
            {"having": []},
        ],
    )
    def test_query_builder_with_empty_values(self, mock_user_repository, query_arg):
        # Arrange
        query_args = QueryArgs(**query_arg)
        # Act & Assert
        try:
            mock_user_repository._query(query_args)
        except Exception:
            pytest.fail(f"Query with empty args failed to build: {query_args}")

    @pytest.mark.parametrize(
        "query_args",
        [
            {"filter_list": [User.id == 1]},
            {"filter_dict": {"id": 1}},
            {"order_by": [User.id]},
            {"distinct_on": []},
            {"distinct_on": [User.id]},
            {"group_by": [User.id]},
            {"group_by": [User.id], "having": [User.id == 1]},
            {"join_on": [ExperienceTransaction]},
        ],
    )
    def test_query_builder_with_non_empty_values(self, mock_user_repository, query_args):
        # Arrange
        query_args = QueryArgs(**query_args)
        # Act & Assert
        try:
            mock_user_repository._query(query_args)
        except Exception:
            pytest.fail(f"Query failed to build with non empty values {query_args}")

    @pytest.mark.usefixtures("mock_user_repository")
    def test_query_with_having_and_no_grouping_fails(self):
        # Arrange & Act & Assert
        with pytest.raises(Warning, match="Defining query with having clause but no group by clause"):
            QueryArgs(having=[User.id == 1])


def get_user_data_for_query(usr):
    return QueryArgs(filter_dict={"discord_id": usr.discord_id})


@pytest.mark.integration()
@pytest.mark.asyncio()
class TestBaseRepositoryIntegration:
    async def test_create_user(self, mock_user_with_db_repository, faker):
        # Arrange
        user = User(discord_id=faker.unique.random_number(digits=18, fix_len=True))
        # Act
        await mock_user_with_db_repository.add(user)
        # Assert
        assert user == await mock_user_with_db_repository.get_first()

    async def test_delete_user(self, db_user, mock_user_with_db_repository):
        # Act
        await mock_user_with_db_repository.delete(db_user)
        # Assert
        assert inspect(db_user).was_deleted

    @pytest.mark.parametrize(
        ("method", "get_data"),
        [
            ("get_first", get_user_data_for_query),
            ("get_one", get_user_data_for_query),
            ("get_by_id", lambda usr: usr.id),
        ],
    )
    async def test_get_single_item(self, db_user, mock_user_with_db_repository, method, get_data):
        # Act
        user_res = await getattr(mock_user_with_db_repository, method)(get_data(db_user))
        # Assert
        assert user_res == db_user

    async def test_get_all(self, db_user, mock_user_with_db_repository):
        # Act
        user_res = await mock_user_with_db_repository.get_all(get_user_data_for_query(db_user))
        # Assert
        assert user_res == [db_user]

    async def test_get_all_with_entities(self, db_user, mock_user_with_db_repository):
        # Act
        user_data = await mock_user_with_db_repository.get_all_with_entities(
            [User.id], get_user_data_for_query(db_user)
        )
        # Assert
        assert user_data == [db_user.id]

    async def test_get_first_with_entities(self, db_user, mock_user_with_db_repository):
        # Act
        user_data = await mock_user_with_db_repository.get_first_with_entities(
            [User.id], get_user_data_for_query(db_user)
        )
        # Assert
        assert user_data == db_user.id

    async def test_get_count(self, db_user, mock_user_with_db_repository):
        # Act
        count = await mock_user_with_db_repository.get_count(get_user_data_for_query(db_user))
        # Assert
        assert count == 1

    async def test_update(self, db_user, mock_user_with_db_repository, faker):
        # Arrange
        new_id = faker.random_number(digits=18, fix_len=True)
        db_user.discord_id = new_id
        # Act
        await mock_user_with_db_repository.update()
        mock_user_with_db_repository.session.expunge_all()
        # Assert
        user = await mock_user_with_db_repository.get_first()
        assert user.discord_id == new_id
