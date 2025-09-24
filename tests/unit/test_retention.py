import os
import time
from pathlib import Path

from modules.retention import purge_old_files


def test_purge_old_files(tmp_path: Path):
    # Create files with different ages
    recent = tmp_path / "recent.log"
    old = tmp_path / "old.log"
    recent.write_text("recent")
    old.write_text("old")

    # Set mtime: recent = now, old = now - 10 days
    now = time.time()
    os.utime(recent, (now, now))
    os.utime(old, (now - 10 * 86400, now - 10 * 86400))

    deleted = purge_old_files(tmp_path, older_than_days=7, patterns=("*.log",))
    assert deleted == 1
    assert recent.exists()
    assert not old.exists()
