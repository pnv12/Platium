"""
Investigation Layer — управління розслідуваннями.

Investigation працює поверх Storage Layer:
- investigations — окремі кейси;
- investigation_entities — сутності, включені в кейс;
- investigation_notes — аналітичні нотатки;
- investigation_timeline — події розслідування.

Модуль не залежить від Aggregator і не використовує DB_PATH напряму.
"""

from datetime import datetime

from platium.core.paths import DB_PATH, ensure_dirs
from platium.storage.database import (
    _get_connection,
    init_db,
    get_entity_by_id,
    get_entity_context,
)


def init_investigation_db():
    """Створює таблиці для розслідувань."""
    ensure_dirs()
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS investigation_entities (
                investigation_id INTEGER NOT NULL,
                entity_id INTEGER NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (investigation_id, entity_id),
                FOREIGN KEY (investigation_id)
                    REFERENCES investigations (id),
                FOREIGN KEY (entity_id)
                    REFERENCES entities (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS investigation_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investigation_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                author TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (investigation_id)
                    REFERENCES investigations (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS investigation_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investigation_id INTEGER NOT NULL,
                entity_id INTEGER,
                event_type TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (investigation_id)
                    REFERENCES investigations (id),
                FOREIGN KEY (entity_id)
                    REFERENCES entities (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_investigation_entities_investigation
            ON investigation_entities (investigation_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_investigation_entities_entity
            ON investigation_entities (entity_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_investigation_notes_investigation
            ON investigation_notes (investigation_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_investigation_timeline_investigation
            ON investigation_timeline (investigation_id)
            """
        )

        conn.commit()


def create_investigation(
    name,
    description=None,
    status="active"
):
    """Створює нове розслідування."""
    if not name or not str(name).strip():
        raise ValueError("Investigation name cannot be empty")

    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO investigations (
                name,
                description,
                status
            )
            VALUES (?, ?, ?)
            """,
            (
                str(name).strip(),
                description,
                status
            )
        )

        conn.commit()

        return cursor.lastrowid


def get_investigation(investigation_id):
    """Отримує розслідування за ID."""
    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                description,
                status,
                created_at,
                updated_at
            FROM investigations
            WHERE id = ?
            """,
            (investigation_id,)
        )

        row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "status": row[3],
        "created_at": row[4],
        "updated_at": row[5]
    }


def list_investigations(status=None):
    """Повертає список розслідувань."""
    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        if status is None:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    status,
                    created_at,
                    updated_at
                FROM investigations
                ORDER BY created_at DESC
                """
            )
        else:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    status,
                    created_at,
                    updated_at
                FROM investigations
                WHERE status = ?
                ORDER BY created_at DESC
                """,
                (status,)
            )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }
        for row in rows
    ]


def update_investigation(
    investigation_id,
    name=None,
    description=None,
    status=None
):
    """Оновлює дані розслідування."""
    investigation = get_investigation(investigation_id)

    if not investigation:
        return False

    new_name = (
        investigation["name"]
        if name is None
        else str(name).strip()
    )

    new_description = (
        investigation["description"]
        if description is None
        else description
    )

    new_status = (
        investigation["status"]
        if status is None
        else status
    )

    if not new_name:
        raise ValueError("Investigation name cannot be empty")

    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE investigations
            SET
                name = ?,
                description = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                new_name,
                new_description,
                new_status,
                investigation_id
            )
        )

        conn.commit()

    return True


def add_entity_to_investigation(
    investigation_id,
    entity_id
):
    """Додає сутність до розслідування."""
    init_investigation_db()

    if not get_investigation(investigation_id):
        raise ValueError(
            f"Investigation not found: {investigation_id}"
        )

    if not get_entity_by_id(entity_id):
        raise ValueError(
            f"Entity not found: {entity_id}"
        )

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO investigation_entities (
                investigation_id,
                entity_id
            )
            VALUES (?, ?)
            """,
            (
                investigation_id,
                entity_id
            )
        )

        added = cursor.rowcount > 0

        cursor.execute(
            """
            UPDATE investigations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (investigation_id,)
        )

        conn.commit()

    return added


def remove_entity_from_investigation(
    investigation_id,
    entity_id
):
    """Видаляє сутність із розслідування."""
    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM investigation_entities
            WHERE investigation_id = ?
              AND entity_id = ?
            """,
            (
                investigation_id,
                entity_id
            )
        )

        removed = cursor.rowcount > 0

        if removed:
            cursor.execute(
                """
                UPDATE investigations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (investigation_id,)
            )

        conn.commit()

    return removed


def add_note_to_investigation(
    investigation_id,
    content,
    author=None
):
    """Додає нотатку до розслідування."""
    if not content or not str(content).strip():
        raise ValueError("Note content cannot be empty")

    init_investigation_db()

    if not get_investigation(investigation_id):
        raise ValueError(
            f"Investigation not found: {investigation_id}"
        )

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO investigation_notes (
                investigation_id,
                content,
                author
            )
            VALUES (?, ?, ?)
            """,
            (
                investigation_id,
                str(content).strip(),
                author
            )
        )

        note_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE investigations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (investigation_id,)
        )

        conn.commit()

    return note_id


def add_timeline_event(
    investigation_id,
    entity_id,
    event_type,
    description
):
    """Додає подію до таймлайну розслідування."""
    if not event_type or not str(event_type).strip():
        raise ValueError("Event type cannot be empty")

    init_investigation_db()

    if not get_investigation(investigation_id):
        raise ValueError(
            f"Investigation not found: {investigation_id}"
        )

    if entity_id is not None and not get_entity_by_id(entity_id):
        raise ValueError(
            f"Entity not found: {entity_id}"
        )

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO investigation_timeline (
                investigation_id,
                entity_id,
                event_type,
                description
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                investigation_id,
                entity_id,
                str(event_type).strip(),
                description
            )
        )

        event_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE investigations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (investigation_id,)
        )

        conn.commit()

    return event_id


def get_investigation_entities(investigation_id):
    """Отримує сутності, пов'язані з розслідуванням."""
    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                e.id,
                e.entity_type,
                e.value,
                ie.added_at
            FROM investigation_entities ie
            JOIN entities e
                ON ie.entity_id = e.id
            WHERE ie.investigation_id = ?
            ORDER BY ie.added_at ASC
            """,
            (investigation_id,)
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "type": row[1],
            "value": row[2],
            "added_at": row[3]
        }
        for row in rows
    ]


def get_investigation_notes(investigation_id):
    """Отримує всі нотатки розслідування."""
    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                content,
                author,
                created_at
            FROM investigation_notes
            WHERE investigation_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (investigation_id,)
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "content": row[1],
            "author": row[2],
            "created_at": row[3]
        }
        for row in rows
    ]


def get_investigation_timeline(investigation_id):
    """Отримує таймлайн розслідування."""
    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                it.id,
                it.entity_id,
                it.event_type,
                it.description,
                it.created_at,
                e.entity_type,
                e.value
            FROM investigation_timeline it
            LEFT JOIN entities e
                ON it.entity_id = e.id
            WHERE it.investigation_id = ?
            ORDER BY it.created_at ASC, it.id ASC
            """,
            (investigation_id,)
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "entity_id": row[1],
            "type": row[2],
            "description": row[3],
            "timestamp": row[4],
            "entity": (
                {
                    "id": row[1],
                    "entity_type": row[5],
                    "value": row[6]
                }
                if row[1] is not None
                else None
            )
        }
        for row in rows
    ]


def get_investigation_context(investigation_id):
    """
    Повертає повну картину розслідування:
    кейс + сутності + їх контекст + нотатки + timeline.
    """
    investigation = get_investigation(investigation_id)

    if not investigation:
        return None

    entities = get_investigation_entities(investigation_id)

    enriched_entities = []

    for entity in entities:
        context = get_entity_context(entity["id"])

        enriched_entities.append(
            {
                **entity,
                "context": context
            }
        )

    return {
        "investigation": investigation,
        "entities": enriched_entities,
        "notes": get_investigation_notes(investigation_id),
        "timeline": get_investigation_timeline(
            investigation_id
        )
    }


def get_investigation_stats(investigation_id):
    """Повертає статистику розслідування."""
    investigation = get_investigation(investigation_id)

    if not investigation:
        return None

    init_investigation_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM investigation_entities
            WHERE investigation_id = ?
            """,
            (investigation_id,)
        )
        entities_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM investigation_notes
            WHERE investigation_id = ?
            """,
            (investigation_id,)
        )
        notes_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM investigation_timeline
            WHERE investigation_id = ?
            """,
            (investigation_id,)
        )
        timeline_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT
                e.entity_type,
                COUNT(*)
            FROM investigation_entities ie
            JOIN entities e
                ON ie.entity_id = e.id
            WHERE ie.investigation_id = ?
            GROUP BY e.entity_type
            ORDER BY e.entity_type
            """,
            (investigation_id,)
        )

        type_distribution = {
            row[0]: row[1]
            for row in cursor.fetchall()
        }

    return {
        "investigation_id": investigation_id,
        "entities": entities_count,
        "notes": notes_count,
        "timeline_events": timeline_count,
        "type_distribution": type_distribution,
        "status": investigation["status"],
        "updated_at": investigation["updated_at"]
    } 
