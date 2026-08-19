"""
Database CRUD helper functions for Quiz Questions and History.
"""

import sqlite3
import uuid

from utils.database import get_db_connection


def init_quiz_table(cursor: sqlite3.Cursor) -> None:
    """Create quiz_questions and previous_quiz_history tables if they don't exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id TEXT PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS previous_quiz_history (
            question_id TEXT PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def add_question(guild_id: int, question_text: str) -> str:
    """Inserts a new question scoped to a specific guild ID."""
    question_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_questions (id, guild_id, question)
            VALUES (?, ?, ?)
            """,
            (question_id, guild_id, question_text),
        )
        conn.commit()
    return question_id


def get_all_questions(guild_id: int) -> list[tuple[str, str]]:
    """Retrieves all quiz questions for a specific guild."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, question 
            FROM quiz_questions 
            WHERE guild_id = ? 
            ORDER BY LOWER(question) ASC
            """,
            (guild_id,),
        )
        return cursor.fetchall()


def remove_question(guild_id: int, question_id: str) -> bool:
    """Deletes a question by ID for a specific guild."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM quiz_questions WHERE id = ? AND guild_id = ?",
            (question_id, guild_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def fetch_and_rotate_quiz_questions(guild_id: int) -> list[str]:
    """
    Selects 5 unique random questions scoped strictly to the given guild_id.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM quiz_questions WHERE guild_id = ?", (guild_id,)
        )
        total_questions = cursor.fetchone()[0]

        if total_questions < 5:
            return []

        cursor.execute(
            """
            SELECT id, question FROM quiz_questions 
            WHERE guild_id = ? 
              AND id NOT IN (SELECT question_id FROM previous_quiz_history WHERE guild_id = ?)
            ORDER BY RANDOM() LIMIT 5
            """,
            (guild_id, guild_id),
        )
        selected_rows = cursor.fetchall()

        if len(selected_rows) < 5:
            cursor.execute(
                """
                SELECT id, question FROM quiz_questions 
                WHERE guild_id = ? 
                ORDER BY RANDOM() LIMIT 5
                """,
                (guild_id,),
            )
            selected_rows = cursor.fetchall()

        selected_ids = [row[0] for row in selected_rows]
        questions_text = [row[1] for row in selected_rows]

        cursor.execute(
            "DELETE FROM previous_quiz_history WHERE guild_id = ?", (guild_id,)
        )
        cursor.executemany(
            "INSERT INTO previous_quiz_history (question_id, guild_id) VALUES (?, ?)",
            [(q_id, guild_id) for q_id in selected_ids],
        )
        conn.commit()

        return questions_text
