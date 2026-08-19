"""
Slash commands for managing server cron channel settings.
"""

import discord
from discord import app_commands
from discord.ext import commands

from commands.settings.list_cron_channels import handle_list_cron_channels
from commands.settings.remove_cron_channel import handle_remove_cron_channel
from commands.settings.set_cron_channel import handle_set_cron_channel
from utils.constants import CRON_TYPE_CHOICES
from utils.permissions import has_required_roles


class SettingsCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="set-cron-channel",
        description="Register a channel and optional ping tags for a cron job.",
    )
    @app_commands.choices(cron_type=list(CRON_TYPE_CHOICES))
    @app_commands.describe(
        cron_type="The type of cron job to configure",
        channel="The target text channel for reports",
        tags="Optional role/user mentions or tags (e.g. @Role)",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def set_cron_channel(
        self,
        interaction: discord.Interaction,
        cron_type: app_commands.Choice[str],
        channel: discord.TextChannel,
        tags: str | None = None,
    ):
        await handle_set_cron_channel(interaction, cron_type.value, channel, tags=tags)

    @app_commands.command(
        name="remove-cron-channel",
        description="Remove cron report channel mappings.",
    )
    @app_commands.choices(cron_type=list(CRON_TYPE_CHOICES))
    @app_commands.describe(
        cron_type="The type of cron job configuration to remove",
        channel="Specific channel to remove (leave blank to remove all for this cron)",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def remove_cron_channel(
        self,
        interaction: discord.Interaction,
        cron_type: app_commands.Choice[str],
        channel: discord.TextChannel | None = None,
    ):
        await handle_remove_cron_channel(interaction, cron_type.value, channel=channel)

    @app_commands.command(
        name="list-cron-channels",
        description="List all active cron channel configurations for this server.",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def list_cron_channels(self, interaction: discord.Interaction):
        await handle_list_cron_channels(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(SettingsCommandsCog(bot))
