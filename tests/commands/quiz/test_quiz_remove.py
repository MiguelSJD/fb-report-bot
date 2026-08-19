"""
Unit tests for /quiz-remove slash command handler.
"""

from unittest.mock import AsyncMock, patch

import pytest

from commands.quiz.quiz_remove import handle_quiz_remove


@pytest.mark.asyncio
async def test_handle_quiz_remove_success():
    """Test successfully removing an existing question."""
    mock_interaction = AsyncMock()
    mock_interaction.guild_id = 123
    mock_interaction.user = "TestUser"

    with patch("commands.quiz.quiz_remove.remove_question", return_value=True):
        await handle_quiz_remove(mock_interaction, "uuid-123")

        mock_interaction.response.send_message.assert_called_once_with(
            "✅ Successfully deleted question `uuid-123`.", ephemeral=True
        )


@pytest.mark.asyncio
async def test_handle_quiz_remove_not_found():
    """Test attempting to remove a non-existent question."""
    mock_interaction = AsyncMock()

    # Removed trailing colon at the end of the await line below
    with patch("commands.quiz.quiz_remove.remove_question", return_value=False):
        await handle_quiz_remove(mock_interaction, "invalid-uuid")

        mock_interaction.response.send_message.assert_called_once_with(
            "⚠️ No question found with ID `invalid-uuid`.", ephemeral=True
        )
