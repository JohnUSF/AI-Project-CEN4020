"""Verified SQLite online backups; restore is an explicit OFFLINE operation.

A WAL-mode .sqlite3 file cannot be backed up safely by just copying the one file.
SQLite's backup API takes a consistent snapshot including committed WAL changes.
"""

import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _assert_database(path):
    with sqlite3.connect(path) as c:
        if c.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed")


def create_backup(source, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if not source.is_file() or source == target:
        raise ValueError(
            "Source must be an existing SQLite database distinct from target"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=".eventhub_backup_", suffix=".sqlite3", dir=target.parent
    )
    os.close(fd)
    try:
        with (
            sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src,
            sqlite3.connect(tmp) as dst,
        ):
            src.backup(dst)
        _assert_database(tmp)
        os.chmod(tmp, 0o600)
        os.replace(tmp, target)
        metadata = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": _digest(target),
            "bytes": target.stat().st_size,
            "source_name": source.name,
            "note": "SQLite online backup; no automatic retention or offsite storage configured",
        }
        target.with_suffix(target.suffix + ".manifest.json").write_text(
            json.dumps(metadata, indent=2) + "\n"
        )
        return metadata
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def verify_backup(backup):
    backup = Path(backup)
    data = json.loads(backup.with_suffix(backup.suffix + ".manifest.json").read_text())
    if data.get("sha256") != _digest(backup):
        raise ValueError("Backup checksum does not match manifest")
    _assert_database(backup)
    return data


def restore_backup(backup, destination, *, confirmed=False):
    """Only for stopped app; caller must explicitly confirm before overwriting."""
    if not confirmed:
        raise PermissionError("Stop the application and pass --confirm-restore")
    backup, destination = Path(backup).resolve(), Path(destination).resolve()
    if backup == destination:
        raise ValueError("Backup and destination cannot be the same path")
    verify_backup(backup)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=".eventhub_restore_", suffix=".sqlite3", dir=destination.parent
    )
    os.close(fd)
    try:
        with (
            sqlite3.connect(f"file:{backup}?mode=ro", uri=True) as src,
            sqlite3.connect(tmp) as dst,
        ):
            src.backup(dst)
        _assert_database(tmp)
        os.chmod(tmp, 0o600)
        os.replace(tmp, destination)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
