"""
Discord UI views, pagination, and dropdown components for Cron Channel list commands.
"""

import math

import discord

from utils.settings_db import get_guild_cron_configs, remove_cron_channel_config


class CronDeleteConfirmView(discord.ui.View):
    """Confirmation view with 'Confirm' and 'Cancel' buttons for deleting a cron channel config."""

    def __init__(
        self,
        guild_id: int,
        cron_type: str,
        channel_id: int,
        parent_view: "CronChannelsListView",
    ):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.cron_type = cron_type
        self.channel_id = channel_id
        self.parent_view = parent_view

    @discord.ui.button(
        label="Confirm Remove", style=discord.ButtonStyle.danger, emoji="🗑️"
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        removed_count = remove_cron_channel_config(
            self.guild_id, self.cron_type, self.channel_id
        )

        if removed_count > 0:
            configs = get_guild_cron_configs(self.guild_id)
            if self.parent_view.filter_cron_type:
                configs = [
                    c for c in configs if c[0] == self.parent_view.filter_cron_type
                ]

            if not configs:
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="⚙️ Configured Cron Channels",
                        description="*No configured cron channels found for this server.*",
                        color=discord.Color.blue(),
                    ),
                    view=None,
                )
            else:
                max_pages = max(
                    1,
                    math.ceil(len(configs) / CronChannelsListView.ITEMS_PER_PAGE),
                )
                new_page = min(self.parent_view.current_page, max_pages - 1)

                new_view = CronChannelsListView(
                    guild_id=self.guild_id,
                    configs=configs,
                    current_page=new_page,
                    filter_cron_type=self.parent_view.filter_cron_type,
                )
                await interaction.response.edit_message(
                    embed=new_view.build_embed(), view=new_view
                )
        else:
            await interaction.response.send_message(
                "❌ Configuration was not found or already removed.",
                ephemeral=True,
            )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.parent_view.build_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class CronDeleteSelect(discord.ui.Select):
    """Dropdown select menu allowing removal of specific cron configurations."""

    def __init__(
        self,
        guild_id: int,
        page_configs: list[tuple[str, int, str]],
        page_offset: int,
        parent_view: "CronChannelsListView",
    ):
        self.guild_id = guild_id
        self.parent_view = parent_view

        options = []
        for idx, (cron_type, channel_id, tags) in enumerate(
            page_configs, start=page_offset
        ):
            # Format value as 'cron_type|channel_id' to uniquely identify row
            val = f"{cron_type}|{channel_id}"
            tags_desc = f"Tags: {tags}" if tags else "No tags"
            options.append(
                discord.SelectOption(
                    label=f"{idx + 1}. {cron_type} (#channel_id: {channel_id})",
                    value=val,
                    description=tags_desc,
                    emoji="⚙️",
                )
            )

        super().__init__(
            placeholder="Select a cron configuration to remove...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_val = self.values[0]
        cron_type, channel_id_str = selected_val.split("|")
        channel_id = int(channel_id_str)

        confirm_view = CronDeleteConfirmView(
            guild_id=self.guild_id,
            cron_type=cron_type,
            channel_id=channel_id,
            parent_view=self.parent_view,
        )

        confirm_embed = discord.Embed(
            title="⚠️ Confirm Cron Mapping Removal",
            description=(
                f"Are you sure you want to remove this cron mapping?\n\n"
                f"**Cron Type:** `{cron_type}`\n"
                f"**Target Channel:** <#{channel_id}>\n"
                f"**Channel ID:** `{channel_id}`"
            ),
            color=discord.Color.red(),
        )

        await interaction.response.edit_message(embed=confirm_embed, view=confirm_view)


class CronChannelsListView(discord.ui.View):
    """Paginated Discord View for listing and deleting cron channel configurations."""

    ITEMS_PER_PAGE = 10

    def __init__(
        self,
        guild_id: int,
        configs: list[tuple[str, int, str]],
        current_page: int = 0,
        filter_cron_type: str | None = None,
    ):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.configs = configs
        self.current_page = current_page
        self.filter_cron_type = filter_cron_type
        self.max_pages = max(1, math.ceil(len(configs) / self.ITEMS_PER_PAGE))

        self.update_components()

    def update_components(self) -> None:
        """Rebuilds components for the active page."""
        self.clear_items()

        start_idx = self.current_page * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        page_items = self.configs[start_idx:end_idx]

        if page_items:
            self.add_item(
                CronDeleteSelect(self.guild_id, page_items, start_idx, parent_view=self)
            )

        if self.max_pages > 1:
            prev_btn = discord.ui.Button(
                label="◀ Previous",
                style=discord.ButtonStyle.secondary,
                disabled=(self.current_page == 0),
            )
            prev_btn.callback = self.prev_page
            self.add_item(prev_btn)

            next_btn = discord.ui.Button(
                label="Next ▶",
                style=discord.ButtonStyle.secondary,
                disabled=(self.current_page >= self.max_pages - 1),
            )
            next_btn.callback = self.next_page
            self.add_item(next_btn)

    def build_embed(self) -> discord.Embed:
        """Builds embed showing configured channels."""
        filter_title = f" ({self.filter_cron_type})" if self.filter_cron_type else ""
        embed = discord.Embed(
            title=f"⚙️ Configured Cron Channels{filter_title}",
            color=discord.Color.blue(),
        )
        embed.set_footer(
            text=f"Page {self.current_page + 1} of {self.max_pages} • Total: {len(self.configs)} mappings"
        )

        start_idx = self.current_page * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        page_items = self.configs[start_idx:end_idx]

        description_lines = []
        for idx, (cron_type, channel_id, tags) in enumerate(
            page_items, start=start_idx + 1
        ):
            tags_str = f" | Tags: `{tags}`" if tags else ""
            description_lines.append(
                f"**{idx}.** 📌 `{cron_type}` ➔ <#{channel_id}> `{channel_id}`{tags_str}"
            )

        embed.description = "\n".join(description_lines)
        return embed

    async def prev_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        self.update_components()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        self.update_components()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)
