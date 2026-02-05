# Vortex Mod Fixer for Linux

This tool fixes Vortex Mod Manager's broken mod deployment on Linux by correctly symlinking mods from the staging directory to the game folder.

## Problem

When running Vortex Mod Manager on Linux (especially for Subnautica), the mod installer doesn't properly deploy mods to the game directory. All enabled mods remain in the staging directory and are never symlinked to the game folder, causing them not to load.

## Solution

The `deploy_mods.py` script reads Vortex's LevelDB database to find enabled mods and correctly symlinks them to the game directory, respecting the proper deployment order and structure.

**⚠️ IMPORTANT: All scripts are READ-ONLY** - They never write to the Vortex database. Your Vortex configuration is completely safe.

**🔒 NEW: Database Corruption Protection** - All scripts now check for Vortex's lockfile and work with a local copy of the database to prevent any corruption, even from read-only access. See [SAFETY_LOCKFILE.md](SAFETY_LOCKFILE.md) for details.

## Features

✅ **Automatic profile detection** - Finds and uses your currently active profile
✅ **Correct deployment order** - BepInEx framework first, then plugins
✅ **Smart filtering** - Only deploys enabled mods, skips collections
✅ **Path conversion** - Handles Windows to Linux path conversion
✅ **Safe preview mode** - Dry-run option to preview changes before applying
✅ **Proper structure** - BepInEx framework → game root, plugins → BepInEx/plugins/
✅ **Lockfile protection** - Prevents database access while Vortex is running
✅ **Local copy safety** - Works with a local database copy to prevent corruption

## Installation

### 1. Clone the Repository

Clone this repository into your tools directory:

```bash
mkdir -p ~/tools
cd ~/tools
git clone https://github.com/yourusername/vortex-subnautica-deployer.git
cd vortex-subnautica-deployer
```

### 2. Proton GE Setup

Install Lutris and ProtonUp-Qt for managing Proton versions:

```bash
# Install Lutris (method varies by distro)

# Steam Deck / SteamOS (recommended - use Flatpak):
flatpak install flathub net.lutris.Lutris

# Ubuntu/Debian:
sudo apt install lutris

# Arch/Manjaro/EndeavourOS:
sudo pacman -S lutris

# Install ProtonUp-Qt (all distros - use Flatpak)
flatpak install flathub net.davidotek.pupgui2
```

Install GE-Proton 10.29:

```bash
# Launch ProtonUp-Qt
flatpak run net.davidotek.pupgui2

# In ProtonUp-Qt:
# 1. Select "Steam" as the install location
# 2. Click "Add version"
# 3. Select "GE-Proton" from the compatibility tool dropdown
# 4. Select version "10.29" from the list
# 5. Click "Install"
```

### 3. Linuxbrew Python Setup

Install Linuxbrew (Homebrew for Linux):

```bash
# Install Linuxbrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to your PATH (add these lines to your ~/.bashrc or ~/.zshrc)
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

Install dependencies via Homebrew:

```bash
# Install GCC, LevelDB, and Python 3.12
brew install gcc leveldb python@3.12
```

Create and activate a Python virtual environment:

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Add Bin Files to PATH

Add the `bin` directory to your PATH for easy access to commands:

```bash
# Add to your ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/tools/vortex-subnautica-deployer/bin:$PATH"' >> ~/.bashrc

# Reload your shell configuration
source ~/.bashrc
```

Now you can use commands like `vortex-deploy`, `vortex-cleanup`, and `vortex-mods` from anywhere.

### 5. Install Desktop Files

Copy the desktop files to enable GUI integration and NXM link handling:

```bash
# Copy desktop files
cp desktop-files/*.desktop ~/.local/share/applications/

# Set the default handler for NXM links (Nexus Mods download links)
xdg-mime default vortex-dl.desktop x-scheme-handler/nxm-protocol
xdg-mime default vortex-dl.desktop x-scheme-handler/nxm
```

This allows you to:

- Click NXM links in your browser to download mods directly to Vortex
- Access Vortex tools from your application menu

## Quick Start

### 1. Preview what will be deployed

```bash
vortex-deploy --dry-run
```

### 2. Deploy the mods

```bash
vortex-deploy
```

That's it! Your mods should now be properly deployed and will load when you start the game.

**Note:** If Vortex is running, you'll get an error message asking you to close it first. This is a safety feature to prevent database corruption.

## Safety Features

### Database Corruption Protection

All scripts now implement **lockfile-based safety** to prevent database corruption:

1. **Checks for Vortex lockfile** before accessing the database
2. **Aborts if Vortex is running** with a clear error message
3. **Creates a local copy** of the database (`state.v2.local`) when safe
4. **Uses the local copy** for all operations

This means:

- ✅ **Zero risk of corruption** - Never accesses database while Vortex is running
- ✅ **Automatic safety** - No manual checks needed
- ✅ **Clear error messages** - You'll know exactly what to do if Vortex is running
- ✅ **Fast operations** - Local copy means no Wine/Proton overhead
- ✅ **Always fresh data** - Creates a new copy every time you run a script

For more details, see [SAFETY_LOCKFILE.md](SAFETY_LOCKFILE.md).

## Configuration

The scripts automatically detect your Vortex database and game paths using `config.py`:

- **Vortex Database**: `~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/state.v2`
- **Subnautica Game**: `~/.steam/steam/steamapps/common/Subnautica`

To verify your configuration:

```bash
cd ~/tools/vortex-subnautica-deployer
python3 config.py
```

If your paths are different, edit `config.py` to match your setup.

## Usage

```bash
# Preview deployment (recommended first step)
vortex-deploy --dry-run

# Actually deploy mods
vortex-deploy

# Use custom database path
vortex-deploy --db /path/to/vortex/state/

# Specify different game
vortex-deploy --game subnautica
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

## Other Useful Commands

### `vortex-mods`

Shows currently enabled mods for the active profile.

```bash
vortex-mods
```

### `find_mod_paths.py`

Shows installation paths and details for mods.

```bash
# Show only enabled mods
cd ~/tools/vortex-subnautica-deployer
python3 find_mod_paths.py

# Show all mods
python3 find_mod_paths.py --all
```

### `explore_db.py`

General database exploration and statistics.

```bash
cd ~/tools/vortex-subnautica-deployer
python3 explore_db.py
```

## Removing Symlinks

If you want to undeploy all mods and remove the symlinks, use the cleanup command:

### `vortex-cleanup`

```bash
# Preview what symlinks would be removed
vortex-cleanup --dry-run

# Actually remove all symlinks
vortex-cleanup

# Remove with verbose output (shows each symlink)
vortex-cleanup --verbose
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
A: Make sure the Vortex database path in `config.py` is correct, or use `--db` to specify the path.

**Q: Mods still don't load in game**
A: Make sure you ran the script without `--dry-run`. Check that symlinks were created in the game directory.

**Q: I want to undeploy mods**
A: Use `vortex-cleanup` to remove all symlinks. You can also disable specific mods in Vortex and re-run `vortex-deploy`.

**Q: How do I know if mods are deployed?**
A: Run `vortex-cleanup --dry-run` to see how many symlinks exist in your game directory.

**Q: Will vortex-cleanup delete my mod files?**
A: No! It only removes symlinks, never real files. Your mods remain safe in the staging directory.

**Q: Commands not found after adding to PATH**
A: Make sure you've reloaded your shell configuration with `source ~/.bashrc` or opened a new terminal window.

## License

This is a utility script created to fix a specific issue with Vortex Mod Manager on Linux. Use at your own risk.
