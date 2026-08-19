"""
Discord UI views, pagination, and dropdown components for Quiz list commands.
"""

import math

import discord

from utils.quiz_db import get_all_questions, remove_question


class QuizDeleteConfirmView(discord.ui.View):
    """Confirmation view with 'Confirm' and 'Cancel' buttons for deletion."""

    def __init__(
        self, question_id: str, question_text: str, parent_view: "QuizListView"
    ):
        super().__init__(timeout=60)
        self.question_id = question_id
        self.question_text = question_text
        self.parent_view = parent_view

    @discord.ui.button(
        label="Confirm Delete", style=discord.ButtonStyle.danger, emoji="🗑️"
    )
    async def confirm(self, interaction: discord.Interaction):
        deleted = remove_question(self.question_id)

        if deleted:
            questions = get_all_questions()
            if not questions:
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="📝 Quiz Questions List",
                        description="*No questions found in the database.*",
                        color=discord.Color.blue(),
                    ),
                    view=None,
                )
            else:
                max_pages = max(
                    1, math.ceil(len(questions) / QuizListView.ITEMS_PER_PAGE)
                )
                new_page = min(self.parent_view.current_page, max_pages - 1)

                new_view = QuizListView(questions, current_page=new_page)
                embed = new_view.build_embed()
                await interaction.response.edit_message(embed=embed, view=new_view)
        else:
            await interaction.response.send_message(
                "❌ Question was not found or already deleted.", ephemeral=True
            )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction):
        embed = self.parent_view.build_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class QuizDeleteSelect(discord.ui.Select):
    """Dropdown select menu allowing question selection for deletion."""

    def __init__(
        self,
        page_questions: list[tuple[str, str]],
        page_offset: int,
        parent_view: "QuizListView",
    ):
        self.parent_view = parent_view
        self.questions_map = {q_id: text for q_id, text in page_questions}

        options = [
            discord.SelectOption(
                label=f"{idx + 1}. {text[:90]}",
                value=q_id,
                description=f"ID: {q_id[:8]}",
                emoji="🗑️",
            )
            for idx, (q_id, text) in enumerate(page_questions, start=page_offset)
        ]
        super().__init__(
            placeholder="Select a question to delete...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        q_id = self.values[0]  # Full UUID
        q_text = self.questions_map.get(q_id, "Unknown Question")

        confirm_view = QuizDeleteConfirmView(
            question_id=q_id,
            question_text=q_text,
            parent_view=self.parent_view,
        )

        confirm_embed = discord.Embed(
            title="⚠️ Confirm Question Deletion",
            description=(
                f"Are you sure you want to delete this question?\n\n"
                f"**Question:** {q_text}\n\n"
                f"**Full ID (for manual fallback command):**\n`{q_id}`"
            ),
            color=discord.Color.red(),
        )

        await interaction.response.edit_message(embed=confirm_embed, view=confirm_view)


class QuizListView(discord.ui.View):
    """Paginated Discord View containing a delete select menu and page navigation."""

    ITEMS_PER_PAGE = 10

    def __init__(self, questions: list[tuple[str, str]], current_page: int = 0):
        super().__init__(timeout=180)
        self.questions = questions
        self.current_page = current_page
        self.max_pages = max(1, math.ceil(len(questions) / self.ITEMS_PER_PAGE))

        self.update_components()

    def update_components(self) -> None:
        """Rebuilds components for the current active page."""
        self.clear_items()

        # Slice current page items
        start_idx = self.current_page * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        page_items = self.questions[start_idx:end_idx]

        if page_items:
            self.add_item(QuizDeleteSelect(page_items, start_idx, parent_view=self))

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
        """Constructs an embed displaying questions for the active page."""
        embed = discord.Embed(
            title="📝 Quiz Questions List",
            color=discord.Color.blue(),
        )
        embed.set_footer(
            text=f"Page {self.current_page + 1} of {self.max_pages} • Total: {len(self.questions)} questions"
        )

        start_idx = self.current_page * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        page_items = self.questions[start_idx:end_idx]

        description_lines = []
        for idx, (q_id, text) in enumerate(page_items, start=start_idx + 1):
            description_lines.append(f"**{idx}.** `{q_id}` — {text}")

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
