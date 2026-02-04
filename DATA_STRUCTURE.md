# LevelDB Data Structure Analysis

## Overview
This LevelDB database contains **4,593 entries** and appears to be the state storage for **Vortex Mod Manager** (a mod manager for games like Subnautica, Skyrim, etc.).

## Key Structure

Keys use a hierarchical structure with `###` as a delimiter:
```
<namespace>###<category>###<subcategory>###<property>
```

### Main Namespaces

1. **`app`** (139 keys) - Application-level data
2. **`persistent`** (4,372 keys) - Persistent user data (95% of database)
3. **`settings`** (78 keys) - User settings
4. **`confidential`** (3 keys) - Confidential data
5. **`user`** (1 key) - User information

## Detailed Breakdown

### 1. App Namespace (`app###...`)
Stores application metadata and extension information:
- **`app###version`** - App version (e.g., "1.15.2")
- **`app###appVersion`** - Same as version
- **`app###instanceId`** - Unique instance identifier
- **`app###migrations`** - Migration history
- **`app###installType`** - Installation type (e.g., "regular")
- **`app###warnedAdmin`** - Admin warning flag
- **`app###extensions###<extension-name>###version`** - Version of each installed extension

Example extensions:
- Mount and Blade II Bannerlord support
- Collections
- Game-specific extensions (game-subnautica, game-skyrim, etc.)
- Various dashlets and utilities

### 2. Persistent Namespace (`persistent###...`)
The largest section containing user data:

#### 2.1 Downloads (`persistent###downloads###...`)
- **`persistent###downloads###speed`** - Current download speed
- **`persistent###downloads###speedHistory`** - Array of historical speeds
- **`persistent###downloads###files###<file-id>###...`** - Download file metadata

File metadata includes:
- `game` - Game identifier (e.g., ["subnautica"])
- `size` - File size in bytes
- `modInfo###nexus###fileInfo###...` - Nexus Mods file information
- `modInfo###nexus###modInfo###...` - Nexus Mods mod information
- `modInfo###nexus###revisionInfo###collection###...` - Collection information

#### 2.2 Mods (`persistent###mods###<game>###<mod-id>###...`)
Stores installed mod information per game:

**Mod ID format**: `<mod-name>-<nexus-id>-<version>-<timestamp>`

Example: `Ancient Sword (BepInEx - Nautilus)-226-1-9-1755769809`

**Mod attributes**:
- `name` - Mod display name
- `author` - Mod author
- `version` / `modVersion` - Mod version
- `description` - Full description (can be very long, HTML formatted)
- `shortDescription` - Brief description
- `pictureUrl` - Thumbnail/image URL
- `fileId` - Nexus file ID
- `fileMD5` - MD5 hash of the file
- `fileName` - Original filename
- `customFileName` - User-customized name
- `logicalFileName` - Logical name used internally
- `category` - Category ID
- `source` - Source (e.g., "nexus")
- `downloadGame` - Game identifier
- `newestFileId` - Latest available file ID
- `uploadedTimestamp` - Upload time (Unix timestamp)
- `updatedTimestamp` - Last update time
- `installTime` - Installation timestamp (ISO 8601)
- `installationPath` - Installation directory
- `isPrimary` - Boolean flag
- `allowRating` - Whether rating is allowed
- `bugMessage` - Bug/warning message (usually empty)

#### 2.3 Profiles (`persistent###profiles###<profile-id>###...`)
User profiles for different game configurations:

- `name` - Profile name
- `modState###<mod-id>###enabledTime` - When mod was enabled (Unix timestamp in ms)

#### 2.4 Categories (`persistent###categories###<game>###<category-id>###...`)
Game-specific mod categories:
- `order` - Display order

#### 2.5 Nexus (`persistent###nexus###...`)
Nexus Mods integration data:
- `userInfo###name` - Nexus username
- `userInfo###isPremium` - Premium status
- `newestVersion` - Latest Vortex version available

#### 2.6 Changelogs (`persistent###changelogs###changelogs`)
Large JSON array containing version changelogs (47,446 bytes - the largest single value)

### 3. Settings Namespace (`settings###...`)
User preferences and configuration:

#### 3.1 Automation (`settings###automation###...`)
- `start` - Auto-start on boot
- `deploy` - Auto-deploy mods
- `enable` - Auto-enable mods
- `install` - Auto-install
- `minimized` - Start minimized

#### 3.2 Downloads (`settings###downloads###...`)
- `path` - Download directory (e.g., "{USERDATA}\\downloads")
- `maxChunks` - Max concurrent download chunks
- `minChunkSize` - Minimum chunk size
- `maxBandwidth` - Bandwidth limit
- `copyOnIFF` - Copy on IFF flag
- `showGraph` - Show download graph

#### 3.3 Interface (`settings###interface###...`)
- `language` - UI language (e.g., "en")
- `advanced` - Advanced mode toggle
- `relativeTimes` - Show relative timestamps

#### 3.4 Window (`settings###window###...`)
- `maximized` - Window maximized state

#### 3.5 Nexus (`settings###nexus###...`)
- `associateNXM` - Associate .nxm files

#### 3.6 Plugins (`settings###plugins###...`)
- `autoSort` - Auto-sort plugins
- `autoEnable` - Auto-enable plugins

#### 3.7 Game Mode (`settings###gameMode###...`)
- `searchPaths` - Additional search paths
- `sortManaged` - Sort method (e.g., "alphabetical")

#### 3.8 Collections (`settings###collections###...`)
- `sortAdded` - Sort method (e.g., "datedownloaded")

#### 3.9 Update (`settings###update###...`)
- `channel` - Update channel (e.g., "stable")

#### 3.10 First Steps (`settings###firststeps###...`)
- `dismissAll` - Dismiss all first-time tips

#### 3.11 Game-specific (`settings###<game>###...`)
- Game-specific settings (e.g., `settings###baldursgate3###migration`)
- FNIS integration: `settings###fnis###autoRun`

## Value Encoding

Values are stored as **JSON-encoded strings**:
- Strings: `"value"` (with quotes)
- Numbers: `123` or `"123"`
- Booleans: `true`, `false`
- Arrays: `[...]`
- Objects: `{...}`
- Null: `null`

## Key Statistics

- **Total entries**: 4,593
- **Key length**: 13-135 bytes (avg: 88.88 bytes)
- **Value length**: 1-47,446 bytes (avg: 131.39 bytes)
- **Largest value**: Changelogs (47,446 bytes)

## Common Prefixes

| Prefix (hex) | Count | Meaning |
|--------------|-------|---------|
| `70657273` ("pers") | 4,372 | persistent### |
| `61707023` ("app#") | 139 | app### |
| `73657474` ("sett") | 78 | settings### |

## Games Detected

Based on the data, this Vortex installation manages mods for:
- **Subnautica** (primary game in this database)
- Baldur's Gate 3
- Mount and Blade II
- And many others (via installed game extensions)

## Mod Installation Structure

### Paths
- **Game Path**: `Z:\home\joern\.steam\steam\steamapps\common\Subnautica`
- **Staging Path**: `Z:\home\joern\.vortex\staging`

### Mod Types
Mods are categorized by type:
- **`bepinex-5`** - BepInEx framework (core modding framework)
- **`bepinex-plugin`** - BepInEx plugins (most mods)
- **`collection`** - Mod collections (curated sets of mods)

### Installation Process
1. Mods are downloaded and extracted to the staging path
2. Each mod gets its own subdirectory: `{staging_path}/{mod_id}`
3. Mod ID format: `{name}-{nexus_id}-{version}-{timestamp}`
4. Vortex manages deployment from staging to game directory

## Scripts Available

### `explore_db.py`
General database exploration showing statistics and sample entries.

### `analyze_keys.py`
Detailed analysis of key patterns and structure.

### `dump_all.py`
Export all database entries to JSON format.

### `find_enabled_mods.py`
Shows currently enabled mods for the active profile.
- Automatically detects active profile
- Shows only enabled mods
- Clean, readable output

### `find_mod_paths.py`
Shows installation paths and details for mods.
- Usage: `python3 find_mod_paths.py [--all]`
- Without `--all`: Shows only enabled mods
- With `--all`: Shows all installed mods
- Displays: version, type, state, installation path, full path

### `deploy_mods.py` ⭐ **MAIN SCRIPT**
Deploys mods by symlinking from staging to game directory.
**Fixes Vortex's broken mod installer on Linux.**

- Usage: `python3 deploy_mods.py [--dry-run]`
- **Features**:
  - Automatically detects active profile
  - Only deploys enabled mods
  - Deploys BepInEx framework first (to game root)
  - Then deploys all plugins (to BepInEx/plugins/)
  - Skips collections
  - Handles Windows to Linux path conversion
  - Supports dry-run mode to preview changes
- **Options**:
  - `--dry-run`: Preview without making changes
  - `--db PATH`: Custom database path
  - `--game NAME`: Game name (default: subnautica)

**Example workflow**:
```bash
# 1. Preview what will be deployed
python3 deploy_mods.py --dry-run

# 2. Actually deploy the mods
python3 deploy_mods.py
```

### `cleanup_mods.py`
Removes mod symlinks from the game directory.
**Safely undeploys all mods.**

- Usage: `python3 cleanup_mods.py [--dry-run] [--verbose]`
- **Features**:
  - Scans game directory for symlinks
  - Only removes symlinks (never real files)
  - Recursive scanning of BepInEx directory
  - Shows detailed list of what will be removed
  - Supports dry-run mode for safety
- **Options**:
  - `--dry-run`: Preview without making changes
  - `--verbose`: Show each symlink being removed
  - `--game-path PATH`: Custom game directory path

**Example workflow**:
```bash
# 1. Check what symlinks exist
python3 cleanup_mods.py --dry-run

# 2. Remove all symlinks
python3 cleanup_mods.py
```

