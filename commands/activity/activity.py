"""
Activity report generator module for F&B Bot.
"""

import asyncio

import discord

from models.log_level import LogLevel
from utils.google_sheets import get_activity_worksheet
from utils.logger import log_event


async def handle_activity_report(
    interaction: discord.Interaction, user: discord.Member
) -> None:
    """Handle the activity slash command execution flow."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        log_event(
            guild_id,
            LogLevel.INFO,
            f"User {interaction.user} triggered /activity for {user}",
        )

        def fetch_row():
            rows = get_activity_worksheet("Activity_Pull").get_all_values()
            return next((r for r in rows if r and r[0] == str(user.id)), None)

        user_row = await asyncio.to_thread(fetch_row)

        if not user_row:
            await interaction.followup.send(
                f"❌ No activity record found for {user.mention}.", ephemeral=True
            )
            return

        user_row += [""] * (16 - len(user_row))
        (
            _,
            mod_name,
            week1_days,
            week1_points,
            week2_days,
            week2_points,
            week3_days,
            week3_points,
            week4_days,
            week4_points,
            week5_days,
            week5_points,
            monthly_days,
            monthly_points,
            basic,
            performance,
        ) = user_row[:16]

        embed = discord.Embed(title="State Of Survival", color=discord.Color.random())
        embed.set_author(name="Hunters Monthly Activity Report")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="GMN", value=mod_name, inline=False)
        embed.add_field(name="Monthly Days", value=monthly_days, inline=True)
        embed.add_field(name="Monthly Points", value=monthly_points, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name="Week 1",
            value=f"Days: {week1_days} / Points: {week1_points}",
            inline=True,
        )
        embed.add_field(
            name="Week 2",
            value=f"Days: {week2_days} / Points: {week2_points}",
            inline=True,
        )
        embed.add_field(
            name="Week 3",
            value=f"Days: {week3_days} / Points: {week3_points}",
            inline=True,
        )
        embed.add_field(
            name="Week 4",
            value=f"Days: {week4_days} / Points: {week4_points}",
            inline=True,
        )
        embed.add_field(
            name="Week 5",
            value=f"Days: {week5_days} / Points: {week5_points}",
            inline=True,
        )
        embed.add_field(name="Basic Comp", value=basic or "N/A", inline=True)
        embed.add_field(
            name="Performance Comp", value=performance or "N/A", inline=True
        )
        embed.add_field(
            name="Note (4-week months)",
            value="Base: 16d/80pts\nPerf: 16d+/100pts",
            inline=False,
        )
        embed.add_field(
            name="Note (5-week months)",
            value="Base: 20d/100pts\nPerf: 20d+/125pts",
            inline=False,
        )
        embed.add_field(
            name="Disclaimer",
            value="If you notice issues, please contact **F/BLMOD**.",
            inline=False,
        )
        embed.set_footer(text="Sos Feedback/Bugs")

        try:
            await user.send(embed=embed)
            await interaction.followup.send(
                f"✅ Sent DM to {user.mention}.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                f"⚠️ Could not send DM to {user.mention}. They may have DMs off.",
                ephemeral=True,
            )

    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
        RuntimeError,
    ) as exc:
        log_event(
            guild_id,
            LogLevel.ERROR,
            f"Activity report generation failed for {user}: {exc}",
            exc=exc,
        )
        await interaction.followup.send(f"❌ Error: {exc}", ephemeral=True)
