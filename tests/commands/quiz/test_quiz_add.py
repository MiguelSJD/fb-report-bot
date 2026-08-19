"""
Unit tests for /quiz-add slash command handler.
"""
import sqlite3
from unittest.mock import AsyncMock, patch

import pytest

from commands.quiz.quiz_add import handle_quiz_add


@pytest.mark.asyncio
async def test_handle_quiz_add_success():
    """Test successfully adding a quiz question."""
    mock_interaction = AsyncMock()
    mock_interaction.guild_id = 123
    mock_interaction.user = "TestUser"

    with patch("commands.quiz.quiz_add.add_question", return_value="uuid-1234"):
        await handle_quiz_add(mock_interaction, "What is Python?")

        mock_interaction.response.send_message.assert_called_once()
        sent_text = mock_interaction.response.send_message.call_args[0][0]
        assert "✅ Question added successfully!" in sent_text
        assert "uuid-1234" in sent_text
        assert "What is Python?" in sent_text


@pytest.mark.asyncio
async def test_handle_quiz_add_failure():
    """Test error handling when database insertion fails."""
    mock_interaction = AsyncMock()
    mock_interaction.guild_id = 123

    with patch("commands.quiz.quiz_add.add_question", side_effect=sqlite3.Error("DB Error")):
        await handle_quiz_add(mock_interaction, "What is Python?")

        mock_interaction.response.send_message.assert_called_once_with(
            "❌ Failed to add question: `DB Error`", ephemeral=True
        )