import pytest

from src.helpers.message_helpers import format_quest_board
from src.models import Quest


class TestFormatQuestBoard:
    def test_base_case(self):
        # Act
        board = format_quest_board([])
        # Assert
        assert board == "No available quests"

    def test_single_case(self):
        # Arrange
        quest = Quest(name="Test Quest", experience=50)
        # Act
        board = format_quest_board([quest])
        # Assert
        assert (
            board == "```\n"
            "======================\n"
            "||  Quests      XP  ||\n"
            "||  Test Quest  50  ||\n"
            "======================\n"
            "```"
        )

    @pytest.mark.parametrize(
        ("name", "experience", "line_length"),
        [("", 0, 18), ("abcde", 50000, 21), ("abcdefg", 1, 19), ("abcdefg", 123, 20)],
    )
    def test_multi_case(self, name, experience, line_length):
        quests = [Quest(name=name, experience=experience)]
        board = format_quest_board(quests)
        lines = board.split("\n")
        test_lines = [line for line in lines if line != "```"]
        assert all(len(line) == line_length for line in test_lines), test_lines
