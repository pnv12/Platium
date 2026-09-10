import sqlite3
import json

from platium.core.paths import DB_PATH, ensure_dirs


def _get_connection():
    ensure_dirs()
    return sqlite3.connect(DB_PATH)


def _serialize_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)


def _deserialize_value(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def init_db():
    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                value TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                scanner TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                data TEXT,
                confidence REAL,
                evidence TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entity_id INTEGER NOT NULL,
                target_entity_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL,
                evidence TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_entity_id) REFERENCES entities (id),
                FOREIGN KEY (target_entity_id) REFERENCES entities (id)
            )
        ''')

        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_entities_value '
            'ON entities (value)'
        )

        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_observations_entity_id '
            'ON observations (entity_id)'
        )

        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_relationships_source '
            'ON relationships (source_entity_id)'
        )

        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_relationships_target '
            'ON relationships (target_entity_id)'
        )

        conn.commit()


def _get_or_create_entity(entity_type, value):
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM entities WHERE value = ?",
            (value,)
        )

        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute(
            "INSERT INTO entities (entity_type, value) VALUES (?, ?)",
            (entity_type, value)
        )

        conn.commit()

        return cursor.lastrowid


def save_observation(
    entity_id,
    scanner,
    source,
    status,
    data=None,
    confidence=0.0,
    evidence=None
):
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO observations (
                entity_id,
                scanner,
                source,
                status,
                data,
                confidence,
                evidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            entity_id,
            scanner,
            source,
            status,
            _serialize_value(data),
            confidence,
            _serialize_value(evidence)
        ))

        conn.commit()

        return cursor.lastrowid


def save_relationship(
    source_entity_id,
    target_entity_id,
    relation_type,
    confidence=0.0,
    evidence=None
):
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO relationships (
                source_entity_id,
                target_entity_id,
                relation_type,
                confidence,
                evidence
            )
            VALUES (?, ?, ?, ?, ?)
        ''', (
            source_entity_id,
            target_entity_id,
            relation_type,
            confidence,
            _serialize_value(evidence)
        ))

        conn.commit()

        return cursor.lastrowid


def get_entity_by_id(entity_id):
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id,
                entity_type,
                value,
                created_at
            FROM entities
            WHERE id = ?
        ''', (entity_id,))

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "entity_type": row[1],
            "value": row[2],
            "created_at": row[3]
        }


def get_entity_by_value(value):
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id,
                entity_type,
                value,
                created_at
            FROM entities
            WHERE value = ?
        ''', (value,))

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "entity_type": row[1],
            "value": row[2],
            "created_at": row[3]
        }


def get_observations(entity_id):
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id,
                entity_id,
                scanner,
                source,
                status,
                data,
                confidence,
                evidence,
                timestamp
            FROM observations
            WHERE entity_id = ?
            ORDER BY timestamp DESC
        ''', (entity_id,))

        rows = cursor.fetchall()

        observations = []

        for row in rows:
            observations.append({
                "id": row[0],
                "entity_id": row[1],
                "scanner": row[2],
                "source": row[3],
                "status": row[4],
                "data": _deserialize_value(row[5]),
                "confidence": row[6],
                "evidence": _deserialize_value(row[7]),
                "timestamp": row[8]
            })

        return observations


def get_relationships(entity_id, direction="both"):
    init_db()

    if direction not in ("outgoing", "incoming", "both"):
        raise ValueError(
            "direction must be 'outgoing', 'incoming', or 'both'"
        )

    with _get_connection() as conn:
        cursor = conn.cursor()

        if direction == "outgoing":
            cursor.execute('''
                SELECT
                    r.id,
                    r.source_entity_id,
                    r.target_entity_id,
                    r.relation_type,
                    r.confidence,
                    r.evidence,
                    r.timestamp,
                    e.entity_type,
                    e.value
                FROM relationships r
                JOIN entities e
                    ON r.target_entity_id = e.id
                WHERE r.source_entity_id = ?
                ORDER BY r.timestamp DESC
            ''', (entity_id,))

        elif direction == "incoming":
            cursor.execute('''
                SELECT
                    r.id,
                    r.source_entity_id,
                    r.target_entity_id,
                    r.relation_type,
                    r.confidence,
                    r.evidence,
                    r.timestamp,
                    e.entity_type,
                    e.value
                FROM relationships r
                JOIN entities e
                    ON r.source_entity_id = e.id
                WHERE r.target_entity_id = ?
                ORDER BY r.timestamp DESC
            ''', (entity_id,))

        else:
            cursor.execute('''
                SELECT
                    r.id,
                    r.source_entity_id,
                    r.target_entity_id,
                    r.relation_type,
                    r.confidence,
                    r.evidence,
                    r.timestamp,
                    source.entity_type,
                    source.value,
                    target.entity_type,
                    target.value
                FROM relationships r
                JOIN entities source
                    ON r.source_entity_id = source.id
                JOIN entities target
                    ON r.target_entity_id = target.id
                WHERE
                    r.source_entity_id = ?
                    OR r.target_entity_id = ?
                ORDER BY r.timestamp DESC
            ''', (entity_id, entity_id))

        rows = cursor.fetchall()

        relationships = []

        for row in rows:
            if direction == "both":
                relationships.append({
                    "id": row[0],
                    "source_entity_id": row[1],
                    "target_entity_id": row[2],
                    "relation_type": row[3],
                    "confidence": row[4],
                    "evidence": _deserialize_value(row[5]),
                    "timestamp": row[6],
                    "source": {
                        "id": row[1],
                        "entity_type": row[7],
                        "value": row[8]
                    },
                    "target": {
                        "id": row[2],
                        "entity_type": row[9],
                        "value": row[10]
                    }
                })
            else:
                relationships.append({
                    "id": row[0],
                    "source_entity_id": row[1],
                    "target_entity_id": row[2],
                    "relation_type": row[3],
                    "confidence": row[4],
                    "evidence": _deserialize_value(row[5]),
                    "timestamp": row[6],
                    "entity": {
                        "id": row[2] if direction == "outgoing" else row[1],
                        "entity_type": row[7],
                        "value": row[8]
                    }
                })

        return relationships


def get_entity_context(entity_id):
    entity = get_entity_by_id(entity_id)

    if not entity:
        return None

    return {
        "entity": entity,
        "observations": get_observations(entity_id),
        "relationships": get_relationships(entity_id)
    }


def get_entity_context_by_value(value):
    entity = get_entity_by_value(value)

    if not entity:
        return None

    return get_entity_context(entity["id"])


def list_entities(entity_type=None, limit=100):
    init_db()

    if limit <= 0:
        return []

    with _get_connection() as conn:
        cursor = conn.cursor()

        if entity_type:
            cursor.execute('''
                SELECT
                    id,
                    entity_type,
                    value,
                    created_at
                FROM entities
                WHERE entity_type = ?
                ORDER BY id DESC
                LIMIT ?
            ''', (entity_type, limit))
        else:
            cursor.execute('''
                SELECT
                    id,
                    entity_type,
                    value,
                    created_at
                FROM entities
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "entity_type": row[1],
                "value": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]


def get_database_stats():
    init_db()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM entities")
        entities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM observations")
        observations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM relationships")
        relationships = cursor.fetchone()[0]

        cursor.execute('''
            SELECT entity_type, COUNT(*)
            FROM entities
            GROUP BY entity_type
            ORDER BY entity_type
        ''')

        type_distribution = {
            row[0]: row[1]
            for row in cursor.fetchall()
        }

    return {
        "entities": entities,
        "observations": observations,
        "relationships": relationships,
        "type_distribution": type_distribution
    }
