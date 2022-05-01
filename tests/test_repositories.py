import pytest
from pytest import mark
from sqlalchemy import inspect

from helpers.sqlalchemy_helpers import QueryArgs
from models import User


class TestUserRepository:
    def test_query_base_case(self, mock_user_repository):
        # Arrange
        query_args = QueryArgs()
        # Act & Assert
        try:
            mock_user_repository._query(query_args)
        except:  # noqa
            assert False, "Empty query failed to build"

    @mark.parametrize(
        "query_arg",
        [
            {"filter_list": []},
            {"filter_dict": {}},
            {"eager_options": []},
            {"order_by_list": []},
            {"join_list": []},
            {"group_by_list": []},
            {"having_list": []},
        ],
    )
    def test_query_builder_with_empty_values(self, mock_user_repository, query_arg):
        # Arrange
        query_args = QueryArgs(**query_arg)
        # Act & Assert
        try:
            mock_user_repository._query(query_args)
        except:  # noqa
            assert False, f"Query with empty args failed to build: {query_args}"

    # TECH DEBT Join and eager options are untested because currently there are no tables to join onto
    @mark.parametrize(
        "query_args",
        [
            {"filter_list": [User.id == 1]},
            {"filter_dict": dict(id=1)},
            {"order_by_list": [User.id]},
            {"distinct_on_list": []},
            {"distinct_on_list": [User.id]},
            {"group_by_list": [User.id]},
            {"group_by_list": [User.id], "having_list": [User.id == 1]},
        ],
    )
    def test_query_builder_with_non_empty_values(self, mock_user_repository, query_args):
        # Arrange
        query_args = QueryArgs(**query_args)
        # Act & Assert
        try:
            mock_user_repository._query(query_args)
        except:  # noqa
            assert False, f"Query failed to build with non emtpy values {query_args}"

    def test_query_with_having_and_no_grouping_fails(self, mock_user_repository):
        # Arrange & Act & Assert
        with pytest.raises(Warning, match="Defining query with having clause but no group by clause"):
            QueryArgs(having_list=[User.id == 1])


def get_user_data_for_query(usr):
    return QueryArgs(filter_dict={"discord_id": usr.discord_id})


@mark.integration
@mark.asyncio
class TestBaseRepositoryIntegration:
    async def test_create_user(self, mock_user_with_db_repository, faker):
        # Arrange
        discord_id = faker.unique.random_number(digits=18, fix_len=True)
        # Act
        user = await mock_user_with_db_repository.create(discord_id=discord_id)
        # Assert
        assert user.discord_id == discord_id

    async def test_delete_user(self, db_user, mock_user_with_db_repository):
        # Act
        await mock_user_with_db_repository.delete(db_user)
        # Assert
        assert inspect(db_user).was_deleted

    @mark.parametrize(
        "method, get_data",
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
