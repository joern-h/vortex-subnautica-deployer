# Vortex Mod Fixer for Linux

This tool fixes Vortex Mod Manager's broken mod deployment on Linux by correctly symlinking mods from the staging directory to the game folder.

## Problem

When running Vortex Mod Manager on Linux (especially for Subnautica), the mod installer doesn't properly deploy mods to the game directory. All enabled mods remain in the staging directory and are never symlinked to the game folder, causing them not to load.

## Solution

The `deploy_mods.py` script reads Vortex's LevelDB database to find enabled mods and correctly symlinks them to the game directory, respecting the proper deployment order and structure.

**⚠️ IMPORTANT: All scripts are READ-ONLY** - They never write to the Vortex database. Your Vortex configuration is completely safe.

## Features

✅ **Automatic profile detection** - Finds and uses your currently active profile  
✅ **Correct deployment order** - BepInEx framework first, then plugins  
✅ **Smart filtering** - Only deploys enabled mods, skips collections  
✅ **Path conversion** - Handles Windows to Linux path conversion  
✅ **Safe preview mode** - Dry-run option to preview changes before applying  
✅ **Proper structure** - BepInEx framework → game root, plugins → BepInEx/plugins/  

## Quick Start

### 1. Preview what will be deployed
```bash
python3 deploy_mods.py --dry-run
```

### 2. Deploy the mods
```bash
python3 deploy_mods.py
```

That's it! Your mods should now be properly deployed and will load when you start the game.

## Requirements

- Python 3
- `plyvel` library for LevelDB access

Install dependencies:
```bash
pip install plyvel
```

## Configuration

The scripts automatically detect your Vortex database and game paths using `config.py`:

- **Vortex Database**: `~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/state.v2`
- **Subnautica Game**: `~/.steam/steam/steamapps/common/Subnautica`

To verify your configuration:
```bash
python3 config.py
```

If your paths are different, edit `config.py` to match your setup.

## Usage

```bash
# Preview deployment (recommended first step)
python3 deploy_mods.py --dry-run

# Actually deploy mods
python3 deploy_mods.py

# Use custom database path
python3 deploy_mods.py --db /path/to/vortex/state/

# Specify different game
python3 deploy_mods.py --game subnautica
```

## How It Works

1. **Reads Vortex database** - Extracts mod information from LevelDB
2. **Finds active profile** - Determines which profile is currently active
3. **Filters enabled mods** - Only processes mods that are enabled in the current profile
4. **Sorts by type** - BepInEx framework (bepinex-5) first, then plugins (bepinex-plugin)
5. **Creates symlinks**:
   - BepInEx framework → Game root directory
   - BepInEx plugins → Game/BepInEx/plugins/ directory
6. **Skips collections** - Collections are metadata only, not actual mods

## Example Output

```
================================================================================
VORTEX MOD DEPLOYMENT SCRIPT FOR LINUX
================================================================================

Game Path: /home/user/.steam/steam/steamapps/common/Subnautica
Staging Path: /home/user/.vortex/staging
Active Profile: Nightmare (bCAlVVOy-)

Found 13 enabled mods to deploy:

  - BepInEx Framework: 1
  - BepInEx Plugins: 12

Deploying: Tobey's BepInEx Pack for Subnautica
  Type: bepinex-5
  From: /home/user/.vortex/staging/Tobey's BepInEx Pack for Subnautica-1108-5-4-23-pack-3-0-0-1766242325
  To: /home/user/.steam/steam/steamapps/common/Subnautica (game root)
  Created 32 symlinks

Deploying: Nautilus
  Type: bepinex-plugin
  From: /home/user/.vortex/staging/Nautilus-1262-1-0-0-pre-48-1768198293
  To: /home/user/.steam/steam/steamapps/common/Subnautica/BepInEx/plugins
  Created 2 symlinks

...

================================================================================
DEPLOYMENT COMPLETE
================================================================================
Total mods processed: 13
Total symlinks created: 93
```

## Other Useful Scripts

### `find_enabled_mods.py`
Shows currently enabled mods for the active profile.
```bash
python3 find_enabled_mods.py
```

### `find_mod_paths.py`
Shows installation paths and details for mods.
```bash
# Show only enabled mods
python3 find_mod_paths.py

# Show all mods
python3 find_mod_paths.py --all
```

### `explore_db.py`
General database exploration and statistics.
```bash
python3 explore_db.py
```

## Removing Symlinks

If you want to undeploy all mods and remove the symlinks, use the cleanup script:

### `cleanup_mods.py`

```bash
# Preview what symlinks would be removed
python3 cleanup_mods.py --dry-run

# Actually remove all symlinks
python3 cleanup_mods.py

# Remove with verbose output (shows each symlink)
python3 cleanup_mods.py --verbose
```

**What it does:**
- Scans the game directory for symlinks
- Only removes symlinks (never removes real files)
- Shows you exactly what will be removed
- Supports dry-run mode for safety

**Example output:**
```
================================================================================
VORTEX MOD CLEANUP SCRIPT
================================================================================

Game Path: /home/user/.steam/steam/steamapps/common/Subnautica

Scanning for symlinks in game root...
Found 6 symlinks in game root
Scanning for symlinks in BepInEx directory...
Found 98 symlinks in BepInEx directory

Total symlinks to remove: 104

Removing symlinks...
  ✓ Removed: .doorstop_version
  ✓ Removed: doorstop_config.ini
  ...

================================================================================
CLEANUP COMPLETE
================================================================================
Symlinks removed: 104
```

## Troubleshooting

**Q: Script says "ERROR: Could not open database"**
A: Make sure you're running the script from the directory containing the `state/` folder, or use `--db` to specify the path.

**Q: Mods still don't load in game**
A: Make sure you ran the script without `--dry-run`. Check that symlinks were created in the game directory.

**Q: I want to undeploy mods**
A: Use `python3 cleanup_mods.py` to remove all symlinks. You can also disable specific mods in Vortex and re-run `deploy_mods.py`.

**Q: How do I know if mods are deployed?**
A: Run `python3 cleanup_mods.py --dry-run` to see how many symlinks exist in your game directory.

**Q: Will cleanup_mods.py delete my mod files?**
A: No! It only removes symlinks, never real files. Your mods remain safe in the staging directory.

## License

This is a utility script created to fix a specific issue with Vortex Mod Manager on Linux. Use at your own risk.

