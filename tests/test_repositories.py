import pytest
from asynctest import MagicMock
from pytest import mark

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


@mark.integration
@mark.asyncio
class TestBaseRepositoryIntegration:
    async def test_create_user(self, db_session, mock_user_repository, faker):
        # Arrange
        mock_user_repository.session_factory = MagicMock(return_value=db_session)
        discord_id = faker.unique.random_number(digits=18, fix_len=True)
        # Act
        user = await mock_user_repository.create(discord_id=discord_id)
        # Assert
        assert user.discord_id == discord_id
