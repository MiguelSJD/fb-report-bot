"""
Unit tests for Quiz generator module and /quiz slash command handler.
"""

from unittest.mock import AsyncMock, patch

import pytest

from commands.quiz.quiz import generate_quiz_message, handle_quiz


def test_generate_quiz_message_success():
    """Test generating quiz message with sufficient questions."""
    mock_questions = [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5",
    ]
    test_guild_id = 123
    target_link = "https://discord.com/channels/123/456"

    with patch(
        "commands.quiz.quiz.fetch_and_rotate_quiz_questions",
        return_value=mock_questions,
    ) as mock_fetch:
        message = generate_quiz_message(
            guild_id=test_guild_id,
            target_channel_link=target_link,
        )

        mock_fetch.assert_called_once_with(test_guild_id)
        assert "# 🧩 Welcome to our weekly Quiz" in message
        assert (
            f"submitting your answers to [weekly-quiz]({target_link}) channel"
            in message
        )
        assert "1. Question 1" in message
        assert "5. Question 5" in message


def test_generate_quiz_message_insufficient_questions():
    """Test that generate_quiz_message returns None when fewer than 5 questions exist."""
    test_guild_id = 123

    with patch(
        "commands.quiz.quiz.fetch_and_rotate_quiz_questions",
        return_value=[],
    ) as mock_fetch:
        message = generate_quiz_message(guild_id=test_guild_id)

        mock_fetch.assert_called_once_with(test_guild_id)
        assert message is None


@pytest.mark.asyncio
async def test_handle_quiz_success():
    """Test successful execution of /quiz slash command with tags."""
    mock_interaction = AsyncMock()
    mock_interaction.guild_id = 123
    mock_interaction.channel_id = 456
    mock_interaction.user = "TestUser"

    mock_questions = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    with patch(
        "commands.quiz.quiz.fetch_and_rotate_quiz_questions",
        return_value=mock_questions,
    ) as mock_fetch:
        await handle_quiz(mock_interaction, tags="<@&789>")

        mock_fetch.assert_called_once_with(mock_interaction.guild_id)
        mock_interaction.response.defer.assert_called_once_with(ephemeral=False)
        mock_interaction.followup.send.assert_called_once()
        sent_content = mock_interaction.followup.send.call_args[1]["content"]

        assert "[weekly-quiz]" in sent_content
        assert "<@&789>" in sent_content


@pytest.mark.asyncio
async def test_handle_quiz_not_enough_questions():
    """Test /quiz handler sends an ephemeral error when not enough questions exist."""
    mock_interaction = AsyncMock()
    mock_interaction.guild_id = 123
    mock_interaction.user = "TestUser"

    with patch(
        "commands.quiz.quiz.fetch_and_rotate_quiz_questions",
        return_value=[],
    ) as mock_fetch:
        await handle_quiz(mock_interaction)

        mock_fetch.assert_called_once_with(mock_interaction.guild_id)
        mock_interaction.followup.send.assert_called_once_with(
            content="❌ **Not enough questions found.** At least 5 questions are required in the database.",
            ephemeral=True,
        )
