"""
Custom permission checks and decorators for Discord slash commands.
"""

import discord
from discord import app_commands

from utils.constants import ALLOWED_ROLE_IDS


def has_required_roles():
    """Custom check decorator ensuring the user has at least one authorized role."""

    def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        return any(role.id in ALLOWED_ROLE_IDS for role in interaction.user.roles)

    return app_commands.check(predicate)
