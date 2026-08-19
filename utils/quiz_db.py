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
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS previous_quiz_history (
            question_id TEXT PRIMARY KEY,
            selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def add_question(question_text: str) -> str:
    """Inserts a new question into the database with a UUID string."""
    question_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_questions (id, question)
            VALUES (?, ?)
            """,
            (question_id, question_text),
        )
        conn.commit()
    return question_id


def get_all_questions() -> list[tuple[str, str]]:
    """Retrieves all quiz questions from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question FROM quiz_questions ORDER BY created_at DESC"
        )
        return cursor.fetchall()


def remove_question(question_id: str) -> bool:
    """Deletes a question by ID. Returns True if a row was deleted."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz_questions WHERE id = ?", (question_id,))
        conn.commit()
        return cursor.rowcount > 0


def fetch_and_rotate_quiz_questions() -> list[str]:
    """
    Selects 5 unique random questions.
    1. Attempts to fetch questions excluding those used last week.
    2. Fallback: Includes last week's questions if total available questions < 5.
    3. Overrides previous_quiz_history with the new 5 question IDs.
    Returns a list of question text strings, or empty list if total questions < 5.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM quiz_questions")
        total_questions = cursor.fetchone()[0]

        if total_questions < 5:
            return []

        cursor.execute(
            """
            SELECT id, question FROM quiz_questions 
            WHERE id NOT IN (SELECT question_id FROM previous_quiz_history)
            ORDER BY RANDOM() LIMIT 5
            """
        )
        selected_rows = cursor.fetchall()

        if len(selected_rows) < 5:
            cursor.execute(
                "SELECT id, question FROM quiz_questions ORDER BY RANDOM() LIMIT 5"
            )
            selected_rows = cursor.fetchall()

        selected_ids = [row[0] for row in selected_rows]
        questions_text = [row[1] for row in selected_rows]

        cursor.execute("DELETE FROM previous_quiz_history")
        cursor.executemany(
            "INSERT INTO previous_quiz_history (question_id) VALUES (?)",
            [(q_id,) for q_id in selected_ids],
        )
        conn.commit()

        return questions_text