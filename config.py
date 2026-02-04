#!/usr/bin/env python3
"""
Configuration file for Vortex Mod Fixer
"""
import os
import shutil
from pathlib import Path

# Vortex state database path
# This is where Vortex stores its LevelDB database when running under Proton/Wine
VORTEX_STATE_DB = os.path.expanduser(
    "~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/state.v2"
)

# Vortex lockfile path
VORTEX_LOCKFILE = os.path.expanduser(
    "~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/lockfile"
)

# Local copy of state.v2 database (used when Vortex is not running)
LOCAL_STATE_COPY = "state.v2.local"

# Subnautica game directory
SUBNAUTICA_GAME_PATH = os.path.expanduser(
    "~/.steam/steam/steamapps/common/Subnautica"
)

# Default game name
DEFAULT_GAME = "subnautica"

def is_vortex_running():
    """Check if Vortex is currently running by checking for lockfile"""
    return os.path.exists(VORTEX_LOCKFILE)

def copy_database_to_local():
    """Copy the Vortex state.v2 database to a local directory"""
    if not os.path.exists(VORTEX_STATE_DB):
        raise FileNotFoundError(f"Vortex database not found at: {VORTEX_STATE_DB}")

    print(f"Copying database from {VORTEX_STATE_DB} to {LOCAL_STATE_COPY}...")

    # Remove old local copy if it exists
    if os.path.exists(LOCAL_STATE_COPY):
        shutil.rmtree(LOCAL_STATE_COPY)

    # Copy the entire state.v2 directory
    shutil.copytree(VORTEX_STATE_DB, LOCAL_STATE_COPY)
    print(f"✓ Database copied to {LOCAL_STATE_COPY}")

    return LOCAL_STATE_COPY

def get_safe_db_path():
    """
    Get a safe database path to use.

    If Vortex is running (lockfile exists), abort to prevent corruption.
    If Vortex is not running, create a fresh local copy and use that.
    """
    if is_vortex_running():
        raise RuntimeError(
            "ERROR: Vortex is currently running (lockfile detected)!\n"
            f"Lockfile: {VORTEX_LOCKFILE}\n\n"
            "Please close Vortex before running this script to prevent database corruption."
        )

    # Vortex is not running, safe to proceed
    print("✓ Vortex is not running (no lockfile detected)")

    # Always create a fresh local copy
    return copy_database_to_local()

def get_db_path():
    """
    Get the Vortex database path, with fallback to local state/ directory.

    DEPRECATED: Use get_safe_db_path() instead for safety against corruption.
    This function is kept for backward compatibility but should not be used.
    """
    if os.path.exists(VORTEX_STATE_DB):
        return VORTEX_STATE_DB
    elif os.path.exists("state/"):
        print(f"Warning: Using local state/ directory instead of {VORTEX_STATE_DB}")
        return "state/"
    else:
        raise FileNotFoundError(
            f"Could not find Vortex database at:\n"
            f"  {VORTEX_STATE_DB}\n"
            f"  or local state/ directory"
        )

def get_game_path():
    """Get the Subnautica game path"""
    if os.path.exists(SUBNAUTICA_GAME_PATH):
        return SUBNAUTICA_GAME_PATH
    else:
        raise FileNotFoundError(
            f"Could not find Subnautica at: {SUBNAUTICA_GAME_PATH}"
        )

if __name__ == "__main__":
    print("Vortex Mod Fixer Configuration")
    print("=" * 80)
    print(f"Vortex Database: {VORTEX_STATE_DB}")
    print(f"  Exists: {os.path.exists(VORTEX_STATE_DB)}")
    print()
    print(f"Vortex Lockfile: {VORTEX_LOCKFILE}")
    print(f"  Exists: {os.path.exists(VORTEX_LOCKFILE)}")
    print(f"  Vortex Running: {is_vortex_running()}")
    print()
    print(f"Subnautica Game: {SUBNAUTICA_GAME_PATH}")
    print(f"  Exists: {os.path.exists(SUBNAUTICA_GAME_PATH)}")
    print()

    try:
        db_path = get_safe_db_path()
        print(f"✓ Safe database path: {db_path}")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"✗ Error: {e}")

    try:
        game_path = get_game_path()
        print(f"✓ Will use game path: {game_path}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")

