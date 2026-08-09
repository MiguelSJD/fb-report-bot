"""
Global event listeners and app command error handlers for FB Report Bot.
"""

import discord
from discord.ext import commands

from models.log_level import LogLevel
from utils.logger import log_event


class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.error(self.on_tree_error)

    @commands.Cog.listener()
    async def on_ready(self):
        """Triggered when the bot connects to Discord."""
        log_event(
            None,
            LogLevel.INFO,
            f"Logged in successfully as {self.bot.user} (ID: {self.bot.user.id})",
        )

        try:
            synced = await self.bot.tree.sync()
            log_event(
                None,
                LogLevel.INFO,
                f"Successfully synced {len(synced)} application slash commands.",
            )
        except (
            discord.HTTPException,
            discord.app_commands.AppCommandError,
            discord.DiscordException,
        ) as exc:
            log_event(
                None,
                LogLevel.ERROR,
                f"Failed to sync application commands: {exc}",
                exc=exc,
            )

    async def on_tree_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        """Global error handler for slash command tree errors."""
        guild_id = interaction.guild_id if interaction.guild else None

        if isinstance(error, discord.app_commands.CheckFailure):
            msg = "⚠️ You don't have permission to use this command."
            log_event(
                guild_id,
                LogLevel.WARNING,
                f"User {interaction.user} (ID: {interaction.user.id}) failed command checks.",
            )
        elif isinstance(error, discord.app_commands.CommandNotFound):
            msg = "⚠️ This command is not available in this channel."
            log_event(
                guild_id,
                LogLevel.WARNING,
                f"Command not found during interaction from {interaction.user}.",
            )
        else:
            msg = f"⚠️ An unexpected error occurred: `{type(error).__name__}`"
            log_event(
                guild_id,
                LogLevel.ERROR,
                f"Slash command execution error ({type(error).__name__}): {error}",
                exc=error,
            )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(content=msg, ephemeral=True)
            else:
                await interaction.response.send_message(content=msg, ephemeral=True)

        except (
            discord.HTTPException,
            discord.app_commands.AppCommandError,
            discord.DiscordException,
        ) as exc:
            log_event(
                guild_id,
                LogLevel.ERROR,
                f"Failed to send error message response to user: {exc}",
                exc=exc,
            )


async def setup(bot: commands.Bot):
    """Entry point for extension loading."""
    await bot.add_cog(EventsCog(bot))
