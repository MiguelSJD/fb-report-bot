"""
Slash commands for managing server cron channel settings.
"""

import discord
from discord import app_commands
from discord.ext import commands

from commands.remove_cron_channel import handle_remove_cron_channel
from commands.set_cron_channel import handle_set_cron_channel


class SettingsCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="set-cron-channel", description="Set the channel for cron reports"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def set_cron_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        """Set the channel where cron reports will be posted for this server."""
        await handle_set_cron_channel(interaction, channel)

    @app_commands.command(
        name="remove-cron-channel", description="Remove the cron report channel setting"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def remove_cron_channel(self, interaction: discord.Interaction):
        """Remove the cron report channel setting for this server."""
        await handle_remove_cron_channel(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(SettingsCommandsCog(bot))
