"""
Unit tests for activity report generation logic.
"""

from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from commands.activity.activity import handle_activity_report


@pytest.mark.asyncio
async def test_handle_activity_report_user_not_found(monkeypatch):
    """Test behavior when target user ID is not found in worksheet rows."""
    mock_interaction = MagicMock(spec=discord.Interaction)
    mock_interaction.guild_id = 123456789
    mock_interaction.followup = MagicMock()
    mock_interaction.followup.send = AsyncMock()

    mock_target_user = MagicMock(spec=discord.Member)
    mock_target_user.id = 12345
    mock_target_user.mention = "<@12345>"

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = [
        ["67890", "OtherMod", "5", "10"],
    ]

    monkeypatch.setattr(
        "commands.activity_report.get_activity_worksheet",
        lambda tab_name: mock_worksheet,
    )
    monkeypatch.setattr(
        "commands.activity_report.log_event", lambda *args, **kwargs: None
    )

    await handle_activity_report(mock_interaction, mock_target_user)

    mock_interaction.followup.send.assert_called_once_with(
        "❌ No activity record found for <@12345>.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_handle_activity_report_success(monkeypatch):
    """Test successful row fetching, embed construction, and DM delivery."""
    mock_interaction = MagicMock(spec=discord.Interaction)
    mock_interaction.guild_id = 123456789
    mock_interaction.user = MagicMock(spec=discord.Member)
    mock_interaction.user.display_avatar.url = (
        "https://cdn.discordapp.com/avatars/user.png"
    )
    mock_interaction.followup = MagicMock()
    mock_interaction.followup.send = AsyncMock()

    mock_target_user = MagicMock(spec=discord.Member)
    mock_target_user.id = 12345
    mock_target_user.mention = "<@12345>"
    mock_target_user.send = AsyncMock()

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = [
        [
            "12345",
            "HunterMod",
            "4",
            "20",
            "4",
            "20",
            "4",
            "20",
            "4",
            "20",
            "0",
            "0",
            "16",
            "80",
            "$100",
            "$50",
        ]
    ]

    monkeypatch.setattr(
        "commands.activity_report.get_activity_worksheet",
        lambda tab_name: mock_worksheet,
    )
    monkeypatch.setattr(
        "commands.activity_report.log_event", lambda *args, **kwargs: None
    )

    await handle_activity_report(mock_interaction, mock_target_user)

    # Verify DM sent to user
    mock_target_user.send.assert_called_once()
    _, kwargs = mock_target_user.send.call_args
    embed = kwargs.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.title == "State Of Survival"
    assert embed.author.name == "Hunters Monthly Activity Report"

    fields = {f.name: f.value for f in embed.fields}
    assert fields["GMN"] == "HunterMod"
    assert fields["Week 1"] == "Days: 4 / Points: 20"
    assert fields["Basic Comp"] == "$100"
    assert fields["Performance Comp"] == "$50"

    # Verify followup response sent back to interaction
    mock_interaction.followup.send.assert_called_once_with(
        "✅ Sent DM to <@12345>.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_handle_activity_report_dm_forbidden(monkeypatch):
    """Test handling when sending a DM fails due to closed DMs (discord.Forbidden)."""
    mock_interaction = MagicMock(spec=discord.Interaction)
    mock_interaction.guild_id = 123456789
    mock_interaction.user = MagicMock(spec=discord.Member)
    mock_interaction.user.display_avatar.url = (
        "https://cdn.discordapp.com/avatars/user.png"
    )
    mock_interaction.followup = MagicMock()
    mock_interaction.followup.send = AsyncMock()

    mock_target_user = MagicMock(spec=discord.Member)
    mock_target_user.id = 12345
    mock_target_user.mention = "<@12345>"
    mock_target_user.send = AsyncMock(
        side_effect=discord.Forbidden(MagicMock(), "Cannot send messages to this user")
    )

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = [["12345", "HunterMod", "4", "20"]]

    monkeypatch.setattr(
        "commands.activity_report.get_activity_worksheet",
        lambda tab_name: mock_worksheet,
    )
    monkeypatch.setattr(
        "commands.activity_report.log_event", lambda *args, **kwargs: None
    )

    await handle_activity_report(mock_interaction, mock_target_user)

    mock_interaction.followup.send.assert_called_once_with(
        "⚠️ Could not send DM to <@12345>. They may have DMs off.",
        ephemeral=True,
    )


@pytest.mark.asyncio
async def test_handle_activity_report_exception_handling(monkeypatch):
    """Test error handling when Google Sheets API throws an exception."""
    mock_interaction = MagicMock(spec=discord.Interaction)
    mock_interaction.guild_id = 123456789
    mock_interaction.followup = MagicMock()
    mock_interaction.followup.send = AsyncMock()

    mock_target_user = MagicMock(spec=discord.Member)

    def raise_error(tab_name):
        raise RuntimeError("Sheets API down")

    monkeypatch.setattr("commands.activity_report.get_activity_worksheet", raise_error)
    monkeypatch.setattr(
        "commands.activity_report.log_event", lambda *args, **kwargs: None
    )

    await handle_activity_report(mock_interaction, mock_target_user)

    mock_interaction.followup.send.assert_called_once_with(
        "❌ Error: Sheets API down", ephemeral=True
    )
