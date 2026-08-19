"""
Unit tests for /quiz-list slash command handler.
"""

from unittest.mock import AsyncMock, patch

import discord
import pytest

from commands.quiz.quiz_list import handle_quiz_list


@pytest.mark.asyncio
async def test_handle_quiz_list_empty():
    """Test listing quiz questions when the database is empty."""
    mock_interaction = AsyncMock()

    with patch("commands.quiz.quiz_list.get_all_questions", return_value=[]):
        await handle_quiz_list(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        kwargs = mock_interaction.response.send_message.call_args[1]

        # Verify ephemeral flag and embed title/description
        assert kwargs["ephemeral"] is True
        assert "embed" in kwargs

        embed = kwargs["embed"]
        assert isinstance(embed, discord.Embed)
        assert embed.title == "📝 Quiz Questions List"
        assert "*No questions found.*" in embed.description


@pytest.mark.asyncio
async def test_handle_quiz_list_with_data():
    """Test listing quiz questions with data present."""
    mock_interaction = AsyncMock()
    mock_data = [("12345678-q_id", "Sample Question 1")]

    with patch("commands.quiz.quiz_list.get_all_questions", return_value=mock_data):
        await handle_quiz_list(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        kwargs = mock_interaction.response.send_message.call_args[1]

        assert kwargs["ephemeral"] is True
        assert "embed" in kwargs
        assert "view" in kwargs

        embed = kwargs["embed"]
        assert isinstance(embed, discord.Embed)
        assert "Sample Question 1" in embed.description
        assert "12345678-q_id" in embed.description
