# Project Summary

## What This Is

A collection of Python scripts to fix Vortex Mod Manager's broken mod deployment on Linux for Subnautica.

## The Problem

Vortex Mod Manager running under Proton/Wine on Linux doesn't properly deploy mods. All enabled mods stay in the staging directory and are never symlinked to the game folder, so they don't load.

## The Solution

Two main scripts that work together:

1. **`deploy_mods.py`** - Deploys mods by creating symlinks
2. **`cleanup_mods.py`** - Removes mod symlinks

## Key Features

✅ **Automatic configuration** - Detects Vortex database and game paths  
✅ **Read-only database access** - Never modifies Vortex configuration  
✅ **Safe symlink management** - Only creates/removes symlinks, never real files  
✅ **Dry-run mode** - Preview changes before applying  
✅ **Profile-aware** - Only deploys mods enabled in current profile  
✅ **Correct deployment order** - BepInEx framework first, then plugins  

## Quick Start

```bash
# 1. Verify configuration
python3 config.py

# 2. Preview deployment
python3 deploy_mods.py --dry-run

# 3. Deploy mods
python3 deploy_mods.py

# 4. (Optional) Remove all symlinks
python3 cleanup_mods.py
```

## Files

### Main Scripts
- **`config.py`** - Configuration (database and game paths)
- **`deploy_mods.py`** - Deploy mods to game directory
- **`cleanup_mods.py`** - Remove mod symlinks

### Information Scripts
- **`find_enabled_mods.py`** - List enabled mods
- **`find_mod_paths.py`** - Show mod installation paths
- **`explore_db.py`** - Database statistics
- **`analyze_keys.py`** - Key pattern analysis
- **`dump_all.py`** - Export database to JSON

### Documentation
- **`README.md`** - Complete usage guide
- **`USAGE.md`** - Quick reference
- **`SAFETY.md`** - Safety guarantees and verification
- **`DATA_STRUCTURE.md`** - Database structure documentation
- **`SUMMARY.md`** - This file

## Configuration

Default paths (edit `config.py` if different):

```python
# Vortex database (Proton/Wine path)
VORTEX_STATE_DB = "~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/state.v2"

# Subnautica game directory
SUBNAUTICA_GAME_PATH = "~/.steam/steam/steamapps/common/Subnautica"
```

## Safety

**All scripts are READ-ONLY for the database:**
- ✅ All use `create_if_missing=False`
- ✅ No `.put()`, `.delete()`, or `.write_batch()` calls
- ✅ Database is never modified
- ✅ Vortex configuration stays intact

**File system operations:**
- `deploy_mods.py` creates symlinks in game directory
- `cleanup_mods.py` removes symlinks (not real files)
- Mod files in staging directory are never touched

## How It Works

### Deployment Process

1. Read Vortex database to find:
   - Active profile
   - Enabled mods
   - Mod types (bepinex-5, bepinex-plugin)
   - Installation paths

2. Convert Windows paths to Linux paths:
   - `Z:\home\...` → `/home/...`

3. Create symlinks in correct order:
   - BepInEx framework → game root
   - BepInEx plugins → game/BepInEx/plugins/

4. Skip collections (metadata only)

### Cleanup Process

1. Scan game directory for symlinks
2. Recursively search BepInEx directory
3. Remove only symlinks (verify with `os.path.islink()`)
4. Never touch real files

## Requirements

- Python 3
- `plyvel` library: `pip install plyvel`
- Vortex Mod Manager (running under Proton/Wine)
- Subnautica (Steam)

## Typical Workflow

### First Time Setup
```bash
python3 config.py                    # Verify paths
python3 find_enabled_mods.py         # See what's enabled
python3 deploy_mods.py --dry-run     # Preview
python3 deploy_mods.py               # Deploy
```

### Switching Profiles
```bash
# 1. Switch profile in Vortex
# 2. Clean up old profile's mods
python3 cleanup_mods.py

# 3. Deploy new profile's mods
python3 deploy_mods.py
```

### Troubleshooting
```bash
python3 cleanup_mods.py --dry-run    # Check current symlinks
python3 find_enabled_mods.py         # Verify enabled mods
python3 find_mod_paths.py            # Check installation paths
```

## Current Status

Based on your system:
- ✅ Vortex database found and accessible
- ✅ Subnautica game directory found
- ✅ Active profile: "Nightmare" (15 enabled mods)
- ✅ Mods already deployed (104 symlinks found)

## Support

All scripts support `--help`:
```bash
python3 deploy_mods.py --help
python3 cleanup_mods.py --help
python3 find_enabled_mods.py --help
```

## License

Utility scripts to fix Vortex on Linux. Use at your own risk.

