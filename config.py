#!/usr/bin/env python3
"""
Configuration file for Vortex Mod Fixer
"""
import os
from pathlib import Path

# Vortex state database path
# This is where Vortex stores its LevelDB database when running under Proton/Wine
VORTEX_STATE_DB = os.path.expanduser(
    "~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/state.v2"
)

# Subnautica game directory
SUBNAUTICA_GAME_PATH = os.path.expanduser(
    "~/.steam/steam/steamapps/common/Subnautica"
)

# Default game name
DEFAULT_GAME = "subnautica"

def get_db_path():
    """Get the Vortex database path, with fallback to local state/ directory"""
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
    print(f"Subnautica Game: {SUBNAUTICA_GAME_PATH}")
    print(f"  Exists: {os.path.exists(SUBNAUTICA_GAME_PATH)}")
    print()
    
    try:
        db_path = get_db_path()
        print(f"✓ Will use database: {db_path}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
    
    try:
        game_path = get_game_path()
        print(f"✓ Will use game path: {game_path}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")

