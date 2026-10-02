import sqlite3
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "documents.db"
)


def create_database():
    """
    Create the database and documents table.
    """

    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            extracted_data TEXT,
            validation_status TEXT,
            validation_message TEXT,
            processed_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_document(
    file_name,
    document_type,
    extracted_data,
    validation_result
):
    """
    Save processed document information
    into the database.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO documents (
            file_name,
            document_type,
            extracted_data,
            validation_status,
            validation_message,
            processed_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        file_name,
        document_type,
        str(extracted_data),
        "Valid" if validation_result.get("valid") else "Invalid",
        validation_result.get("message"),
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()
    connection.close()
def get_all_documents():
    """
    Retrieve all processed documents from the database.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            file_name,
            document_type,
            extracted_data,
            validation_status,
            validation_message,
            processed_at
        FROM documents
        ORDER BY id DESC
    """)

    documents = cursor.fetchall()

    connection.close()

    return documents