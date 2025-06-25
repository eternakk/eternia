"""
Initial database schema for Eternia.

This migration creates all the tables needed for the Eternia database.
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE schema_version
        (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL,
            updated_at REAL NOT NULL
        )
        """,
        "DROP TABLE schema_version"
    ),
    step(
        """
        CREATE TABLE state
        (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL,
            timestamp REAL NOT NULL,
            last_emotion TEXT,
            last_intensity REAL,
            last_dominance REAL,
            last_zone TEXT,
            evolution_stats TEXT NOT NULL,
            max_memories INTEGER NOT NULL,
            max_discoveries INTEGER NOT NULL,
            max_explored_zones INTEGER NOT NULL,
            max_modifiers INTEGER NOT NULL,
            max_checkpoints INTEGER NOT NULL
        )
        """,
        "DROP TABLE state"
    ),
    step(
        """
        CREATE TABLE memories
        (
            id INTEGER PRIMARY KEY,
            state_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            emotional_quality TEXT,
            clarity REAL,
            timestamp REAL NOT NULL,
            data TEXT,
            FOREIGN KEY (state_id) REFERENCES state (id)
        )
        """,
        "DROP TABLE memories"
    ),
    step(
        """
        CREATE TABLE discoveries
        (
            id INTEGER PRIMARY KEY,
            state_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            timestamp REAL NOT NULL,
            data TEXT,
            FOREIGN KEY (state_id) REFERENCES state (id)
        )
        """,
        "DROP TABLE discoveries"
    ),
    step(
        """
        CREATE TABLE explored_zones
        (
            id INTEGER PRIMARY KEY,
            state_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            timestamp REAL NOT NULL,
            FOREIGN KEY (state_id) REFERENCES state (id)
        )
        """,
        "DROP TABLE explored_zones"
    ),
    step(
        """
        CREATE TABLE modifiers
        (
            id INTEGER PRIMARY KEY,
            state_id INTEGER NOT NULL,
            zone TEXT NOT NULL,
            type TEXT,
            effect TEXT,
            timestamp REAL NOT NULL,
            data TEXT,
            FOREIGN KEY (state_id) REFERENCES state (id)
        )
        """,
        "DROP TABLE modifiers"
    ),
    step(
        """
        CREATE TABLE checkpoints
        (
            id INTEGER PRIMARY KEY,
            state_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            timestamp REAL NOT NULL,
            FOREIGN KEY (state_id) REFERENCES state (id)
        )
        """,
        "DROP TABLE checkpoints"
    ),
    # Insert initial schema version
    step(
        """
        INSERT INTO schema_version (version, updated_at)
        VALUES (1, strftime('%s', 'now'))
        """,
        """
        DELETE FROM schema_version
        WHERE version = 1
        """
    )
]