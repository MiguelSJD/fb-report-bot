"""
Unit tests for /quiz-list slash command handler.
"""

from unittest.mock import AsyncMock, patch

import pytest

from commands.quiz.quiz_list import handle_quiz_list


@pytest.mark.asyncio
async def test_handle_quiz_list_empty():
    """Test listing quiz questions when the database is empty."""
    mock_interaction = AsyncMock()

    with patch("commands.quiz.quiz_list.get_all_questions", return_value=[]):
        await handle_quiz_list(mock_interaction)

        mock_interaction.response.send_message.assert_called_once_with(
            "📝 **Quiz Questions List:**\n*No questions found.*",
            ephemeral=True,
        )


@pytest.mark.asyncio
async def test_handle_quiz_list_with_data():
    """Test listing quiz questions with data present."""
    mock_interaction = AsyncMock()
    mock_data = [("12345678-q_id", "Sample Question 1")]

    with patch("commands.quiz.quiz_list.get_all_questions", return_value=mock_data):
        await handle_quiz_list(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        kwargs = mock_interaction.response.send_message.call_args[1]
        assert "Sample Question 1" in kwargs["content"]
        assert kwargs["view"] is not None
        assert kwargs["ephemeral"] is True
