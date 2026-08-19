"""
Discord UI views and button components for Quiz commands.
"""

import discord

from utils.quiz_db import get_all_questions, remove_question


class QuizDeleteButton(discord.ui.Button):
    """Interactive button attached to each question for dynamic deletion."""

    def __init__(self, question_id: str, short_id: str):
        super().__init__(
            label=f"Delete ({short_id})",
            style=discord.ButtonStyle.danger,
            custom_id=f"delete_quiz:{question_id}",
        )
        self.question_id = question_id

    async def callback(self, interaction: discord.Interaction):
        deleted = remove_question(self.question_id)
        if deleted:
            await interaction.response.send_message(
                f"🗑️ Question `{self.question_id[:8]}` deleted successfully.",
                ephemeral=True,
            )
            questions = get_all_questions()
            if not questions:
                await interaction.message.edit(
                    content="📝 **Quiz Questions List:**\n*No questions found.*",
                    view=None,
                )
            else:
                new_view = QuizListView(questions)
                content = "📝 **Quiz Questions List:**\n\n" + "\n".join(
                    f"• `{q_id[:8]}`: {text}" for q_id, text in questions
                )
                await interaction.message.edit(content=content, view=new_view)
        else:
            await interaction.response.send_message(
                "❌ Question was not found or already deleted.",
                ephemeral=True,
            )


class QuizListView(discord.ui.View):
    """Interactive Discord View holding delete buttons for questions."""

    def __init__(self, questions: list[tuple[str, str]]):
        super().__init__(timeout=180)
        # Limit buttons to first 25 items to fit within Discord view constraints
        for question_id, _ in questions[:25]:
            self.add_item(QuizDeleteButton(question_id, question_id[:8]))
