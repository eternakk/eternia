import os
import sys
import pytest
import tempfile
import json
import sqlite3
import time
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import EternaDatabase
from modules.state_tracker import EternaStateTracker


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        temp_db_path = temp_file.name

    yield temp_db_path

    # Clean up after the test
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def temp_json_path():
    """Create a temporary JSON file path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_json_path = temp_file.name

    yield temp_json_path

    # Clean up after the test
    if os.path.exists(temp_json_path):
        os.unlink(temp_json_path)


@pytest.fixture
def temp_backup_dir():
    """Create a temporary directory for backup testing."""
    temp_dir = tempfile.mkdtemp()

    yield temp_dir

    # Clean up after the test
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_state_data():
    """Return sample state data for testing."""
    return {
        "version": 1,
        "timestamp": 1625097600.0,
        "emotion": {
            "name": "joy",
            "intensity": 0.8,
            "direction": "outward"
        },
        "last_intensity": 0.8,
        "last_dominance": 0.6,
        "last_zone": "Quantum Forest",
        "evolution": {
            "intellect": 120,
            "senses": 110
        },
        "memories": [
            {
                "description": "First memory",
                "emotional_quality": "joy",
                "clarity": 0.9
            },
            {
                "description": "Second memory",
                "emotional_quality": "wonder",
                "clarity": 0.7
            }
        ],
        "discoveries": [
            {
                "name": "Crystal Formation",
                "category": "natural"
            },
            {
                "name": "Ancient Artifact",
                "category": "artifact"
            }
        ],
        "explored_zones": ["Quantum Forest", "Crystal Caves"],
        "modifiers": {
            "Quantum Forest": ["luminous", {"type": "temporal", "effect": "slow"}],
            "Crystal Caves": ["resonant"]
        },
        "checkpoints": ["checkpoint_1.bin", "checkpoint_2.bin"],
        "max_memories": 100,
        "max_discoveries": 50,
        "max_explored_zones": 20,
        "max_modifiers": 50,
        "max_checkpoints": 10
    }


@pytest.fixture
def db_instance(temp_db_path):
    """Return an initialized EternaDatabase instance."""
    db = EternaDatabase(db_path=temp_db_path)
    yield db
    db.close()


@pytest.fixture
def state_tracker_with_db(temp_db_path, temp_json_path):
    """Return an initialized EternaStateTracker instance with database enabled."""
    tracker = EternaStateTracker(
        save_path=temp_json_path,
        db_path=temp_db_path,
        use_database=True,
        use_lazy_loading=True
    )
    tracker.initialize()
    yield tracker
    tracker.shutdown()


@pytest.fixture
def state_tracker_with_json(temp_json_path):
    """Return an initialized EternaStateTracker instance with JSON persistence."""
    tracker = EternaStateTracker(
        save_path=temp_json_path,
        use_database=False
    )
    tracker.initialize()
    yield tracker
    tracker.shutdown()


class TestEternaDatabase:
    """Tests for the EternaDatabase class."""

    def test_initialization(self, temp_db_path):
        """Test that the database is properly initialized."""
        db = EternaDatabase(db_path=temp_db_path)

        # Check that the database file was created
        assert os.path.exists(temp_db_path)

        # Check that the connection is established
        assert db.conn is not None
        assert db.cursor is not None

        # Check that the schema version is set
        db.cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
        version = db.cursor.fetchone()[0]
        assert version == db.SCHEMA_VERSION

        db.close()

    def test_create_tables(self, temp_db_path):
        """Test that all required tables are created."""
        db = EternaDatabase(db_path=temp_db_path)

        # Check that all tables exist
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db.cursor.fetchall()]

        expected_tables = [
            "schema_version", "state", "memories", "discoveries", 
            "explored_zones", "modifiers", "checkpoints"
        ]

        for table in expected_tables:
            assert table in tables

        db.close()

    def test_save_and_load_state(self, db_instance, sample_state_data):
        """Test saving and loading state data."""
        # Save the state
        state_id = db_instance.save_state(sample_state_data)
        assert state_id is not None

        # Load the state
        loaded_state = db_instance.load_latest_state()
        assert loaded_state is not None

        # Check that the loaded state matches the original
        assert loaded_state["version"] == sample_state_data["version"]
        assert loaded_state["emotion"]["name"] == sample_state_data["emotion"]["name"]
        assert loaded_state["last_zone"] == sample_state_data["last_zone"]
        assert loaded_state["evolution"]["intellect"] == sample_state_data["evolution"]["intellect"]

        # Check that collections were loaded
        assert len(loaded_state["memories"]) == len(sample_state_data["memories"])
        assert len(loaded_state["discoveries"]) == len(sample_state_data["discoveries"])
        assert len(loaded_state["explored_zones"]) == len(sample_state_data["explored_zones"])
        assert len(loaded_state["modifiers"]) == len(sample_state_data["modifiers"])
        assert len(loaded_state["checkpoints"]) == len(sample_state_data["checkpoints"])

    def test_lazy_loading(self, db_instance, sample_state_data):
        """Test lazy loading of collections."""
        # Save the state
        state_id = db_instance.save_state(sample_state_data)

        # Load the state with lazy loading
        lazy_state = db_instance.load_latest_state(lazy_load=True)
        assert lazy_state is not None

        # Check that collections are empty initially
        assert len(lazy_state["memories"]) == 0
        assert len(lazy_state["discoveries"]) == 0
        assert len(lazy_state["explored_zones"]) == 0
        assert len(lazy_state["modifiers"]) == 0
        assert len(lazy_state["checkpoints"]) == 0

        # Load each collection and check that it's populated
        memories = db_instance.lazy_load_collection(lazy_state, "memories")
        assert len(memories) == len(sample_state_data["memories"])

        discoveries = db_instance.lazy_load_collection(lazy_state, "discoveries")
        assert len(discoveries) == len(sample_state_data["discoveries"])

        explored_zones = db_instance.lazy_load_collection(lazy_state, "explored_zones")
        assert len(explored_zones) == len(sample_state_data["explored_zones"])

        modifiers = db_instance.lazy_load_collection(lazy_state, "modifiers")
        assert len(modifiers) == len(sample_state_data["modifiers"])

        checkpoints = db_instance.lazy_load_collection(lazy_state, "checkpoints")
        assert len(checkpoints) == len(sample_state_data["checkpoints"])

    def test_backup_and_restore(self, db_instance, sample_state_data, temp_backup_dir):
        """Test backup and restore functionality."""
        # Save the state
        state_id = db_instance.save_state(sample_state_data)

        # Create a backup
        backup_path = os.path.join(temp_backup_dir, "test_backup.db")
        result_path = db_instance.backup_state(backup_path)
        assert result_path == backup_path
        assert os.path.exists(backup_path)

        # Modify the state
        modified_state = sample_state_data.copy()
        modified_state["last_zone"] = "Modified Zone"
        db_instance.save_state(modified_state)

        # Verify the modification
        current_state = db_instance.load_latest_state()
        assert current_state["last_zone"] == "Modified Zone"

        # Restore from backup
        success = db_instance.restore_from_backup(backup_path)
        assert success

        # Verify the restoration
        restored_state = db_instance.load_latest_state()
        assert restored_state["last_zone"] == sample_state_data["last_zone"]

    def test_export_and_import(self, db_instance, sample_state_data, temp_backup_dir):
        """Test export to JSON and import from JSON."""
        # Save the state
        state_id = db_instance.save_state(sample_state_data)

        # Export to JSON
        json_path = os.path.join(temp_backup_dir, "test_export.json")
        result_path = db_instance.export_to_json(json_path)
        assert result_path == json_path
        assert os.path.exists(json_path)

        # Verify the exported JSON
        with open(json_path, 'r') as f:
            export_data = json.load(f)
        assert "state" in export_data
        assert export_data["state"]["last_zone"] == sample_state_data["last_zone"]

        # Modify the state
        modified_state = sample_state_data.copy()
        modified_state["last_zone"] = "Modified Zone"
        db_instance.save_state(modified_state)

        # Import from JSON
        success = db_instance.import_from_json(json_path)
        assert success

        # Verify the import
        imported_state = db_instance.load_latest_state()
        assert imported_state["last_zone"] == sample_state_data["last_zone"]

    def test_schema_versioning(self, temp_db_path):
        """Test schema versioning and migration."""
        # Create a database with version 0 (simulating an old version)
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE schema_version (id INTEGER PRIMARY KEY, version INTEGER NOT NULL, updated_at REAL NOT NULL)")
        cursor.execute("INSERT INTO schema_version (version, updated_at) VALUES (0, ?)", (time.time(),))
        conn.commit()
        conn.close()

        # Open the database, which should trigger a migration
        with patch.object(EternaDatabase, '_migrate_schema') as mock_migrate:
            db = EternaDatabase(db_path=temp_db_path)
            mock_migrate.assert_called_once_with(0)

            # Check that the schema version was updated
            db.cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            version = db.cursor.fetchone()[0]
            assert version == db.SCHEMA_VERSION

            db.close()


class TestEternaStateTrackerWithDatabase:
    """Tests for the EternaStateTracker class with database integration."""

    def test_initialization_with_database(self, state_tracker_with_db):
        """Test that the state tracker is properly initialized with database."""
        tracker = state_tracker_with_db

        # Check that the database is initialized
        assert tracker.db is not None
        assert tracker.use_database is True

    def test_save_and_load_with_database(self, state_tracker_with_db, sample_state_data):
        """Test saving and loading state with database."""
        tracker = state_tracker_with_db

        # Set up the tracker with sample data
        tracker.last_emotion = sample_state_data["emotion"]
        tracker.last_intensity = sample_state_data["last_intensity"]
        tracker.last_dominance = sample_state_data["last_dominance"]
        tracker.last_zone = sample_state_data["last_zone"]
        tracker.evolution_stats = sample_state_data["evolution"]

        for memory in sample_state_data["memories"]:
            tracker.add_memory(memory)

        for discovery in sample_state_data["discoveries"]:
            tracker.record_discovery(discovery)

        for zone in sample_state_data["explored_zones"]:
            tracker.mark_zone_explored(zone)

        for zone, modifiers in sample_state_data["modifiers"].items():
            for modifier in modifiers:
                tracker.add_modifier(zone, modifier)

        for checkpoint in sample_state_data["checkpoints"]:
            tracker.register_checkpoint(checkpoint)

        # Save the state
        tracker.save()

        # Create a new tracker and load the state
        new_tracker = EternaStateTracker(
            db_path=tracker.db_path,
            use_database=True,
            use_lazy_loading=False
        )
        new_tracker.load()

        # Check that the loaded state matches the original
        assert new_tracker.last_emotion["name"] == sample_state_data["emotion"]["name"]
        assert new_tracker.last_intensity == sample_state_data["last_intensity"]
        assert new_tracker.last_zone == sample_state_data["last_zone"]
        assert new_tracker.evolution_stats["intellect"] == sample_state_data["evolution"]["intellect"]

        # Check that collections were loaded
        assert len(new_tracker.memories) == len(sample_state_data["memories"])
        assert len(new_tracker.discoveries) == len(sample_state_data["discoveries"])
        assert len(new_tracker.explored_zones) == len(sample_state_data["explored_zones"])
        assert len(new_tracker.checkpoints) == len(sample_state_data["checkpoints"])

    def test_lazy_loading_with_state_tracker(self, state_tracker_with_db, sample_state_data):
        """Test lazy loading with state tracker."""
        tracker = state_tracker_with_db

        # Set up the tracker with sample data
        tracker.last_emotion = sample_state_data["emotion"]
        tracker.last_zone = sample_state_data["last_zone"]
        tracker.evolution_stats = sample_state_data["evolution"]

        for memory in sample_state_data["memories"]:
            tracker.add_memory(memory)

        for discovery in sample_state_data["discoveries"]:
            tracker.record_discovery(discovery)

        # Save the state
        tracker.save()

        # Create a new tracker with lazy loading
        lazy_tracker = EternaStateTracker(
            db_path=tracker.db_path,
            use_database=True,
            use_lazy_loading=True
        )
        lazy_tracker.initialize()  # Initialize to set up cache and other attributes
        lazy_tracker.load()

        # Check that collections are empty initially
        assert len(lazy_tracker.memories) == 0
        assert len(lazy_tracker.discoveries) == 0

        # Access collections directly to trigger lazy loading
        lazy_tracker._ensure_collection_loaded("memories")
        lazy_tracker._ensure_collection_loaded("discoveries")

        # Verify that collections are now loaded
        assert len(lazy_tracker.memories) == len(sample_state_data["memories"])
        assert len(lazy_tracker.discoveries) == len(sample_state_data["discoveries"])

    def test_backup_and_restore_with_state_tracker(self, state_tracker_with_db, sample_state_data, temp_backup_dir):
        """Test backup and restore with state tracker."""
        tracker = state_tracker_with_db

        # Set up the tracker with sample data
        tracker.last_emotion = sample_state_data["emotion"]
        tracker.last_zone = sample_state_data["last_zone"]
        tracker.evolution_stats = sample_state_data["evolution"]

        # Save the state
        tracker.save()

        # Create a backup
        backup_path = os.path.join(temp_backup_dir, "test_backup.db")
        result_path = tracker.backup_state(backup_path)
        assert result_path == backup_path
        assert os.path.exists(backup_path)

        # Modify the state
        tracker.last_zone = "Modified Zone"
        tracker.save()

        # Verify the modification
        assert tracker.last_zone == "Modified Zone"

        # Restore from backup
        success = tracker.restore_from_backup(backup_path)
        assert success

        # Create a new tracker to load the restored state
        new_tracker = EternaStateTracker(
            db_path=tracker.db_path,
            use_database=True,
            use_lazy_loading=False
        )
        new_tracker.initialize()
        new_tracker.load()

        # Verify the restoration
        assert new_tracker.last_zone == sample_state_data["last_zone"]

    def test_switching_persistence_modes(self, state_tracker_with_db, state_tracker_with_json, sample_state_data):
        """Test switching between database and JSON persistence."""
        # Set up the database tracker with sample data
        db_tracker = state_tracker_with_db
        db_tracker.last_emotion = sample_state_data["emotion"]
        db_tracker.last_zone = sample_state_data["last_zone"]
        db_tracker.evolution_stats = sample_state_data["evolution"]
        db_tracker.save()

        # Export to JSON
        json_path = state_tracker_with_json.save_path
        db_tracker.export_to_json(json_path)

        # Create a new JSON tracker to ensure clean state
        json_tracker = EternaStateTracker(
            save_path=json_path,
            use_database=False
        )
        json_tracker.initialize()

        # Manually load the JSON file to verify its contents
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        # Verify the JSON data directly
        assert "state" in json_data
        assert "last_zone" in json_data["state"]
        assert json_data["state"]["last_zone"] == sample_state_data["last_zone"]

        # Modify the JSON data directly
        json_data["state"]["last_zone"] = "JSON Modified Zone"

        # Save the modified JSON data
        with open(json_path, 'w') as f:
            json.dump(json_data, f)

        # Import back to the database tracker
        db_tracker.import_from_json(json_path)

        # Create a new tracker to load the imported state
        new_db_tracker = EternaStateTracker(
            db_path=db_tracker.db_path,
            use_database=True,
            use_lazy_loading=False
        )
        new_db_tracker.initialize()
        new_db_tracker.load()

        # Check that the modification was imported
        assert new_db_tracker.last_zone == "JSON Modified Zone"


if __name__ == "__main__":
    pytest.main(["-v", "test_database.py"])
