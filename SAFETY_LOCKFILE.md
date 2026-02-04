# Database Safety: Lockfile Protection

## Problem

Even opening the Vortex database in **read-only mode** can lead to corruption if Vortex is running simultaneously. This is because LevelDB uses internal locking mechanisms and shared state that can be disrupted by concurrent access.

## Solution

All scripts now implement a **lockfile-based safety mechanism** that:

1. **Checks for Vortex lockfile** before accessing the database
2. **Aborts if Vortex is running** to prevent any corruption
3. **Creates a local copy** of the database when safe to access
4. **Uses the local copy** for all read operations

## Implementation Details

### Lockfile Location

```
~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/lockfile
```

This file exists **only when Vortex is running**.

### Local Database Copy

When Vortex is not running, scripts automatically:
- Copy `state.v2` → `state.v2.local` (in current directory)
- **Always create a fresh copy** to ensure latest data
- Use the local copy for all database operations

### Updated Functions in `config.py`

#### `is_vortex_running()`
Returns `True` if lockfile exists (Vortex is running).

#### `get_safe_db_path()`
- **Checks lockfile first**
- **Aborts if Vortex is running** with clear error message
- **Always creates a fresh local copy** if safe
- **Returns path to local copy**

#### `copy_database_to_local()`
Copies entire `state.v2` directory to `state.v2.local`.

## Updated Scripts

All scripts now use `config.get_safe_db_path()` instead of `config.get_db_path()`:

- ✅ `deploy_mods.py`
- ✅ `find_enabled_mods.py`
- ✅ `find_mod_paths.py`
- ✅ `explore_db.py`
- ✅ `analyze_keys.py`
- ✅ `dump_all.py`

## Usage

### Normal Usage (Automatic)

Just run any script as before:

```bash
python3 deploy_mods.py
python3 find_enabled_mods.py
```

The script will automatically:
1. Check if Vortex is running
2. Abort if running, or create a fresh local copy if safe
3. Use the local copy

### If Vortex is Running

You'll see this error:

```
ERROR: Vortex is currently running (lockfile detected)!
Lockfile: ~/.steam/steam/steamapps/compatdata/264710/pfx/drive_c/users/steamuser/AppData/Roaming/Vortex/lockfile

Please close Vortex before running this script to prevent database corruption.
```

**Solution:** Close Vortex, then run the script again.

### Fresh Copy Every Time

Every script run automatically creates a fresh copy of the database, ensuring you always have the latest data. No manual refresh needed!

## Testing the Configuration

```bash
python3 config.py
```

This will show:
- Vortex database path and existence
- **Lockfile path and status**
- **Whether Vortex is running**
- Safe database path (or error if Vortex is running)
- Game path

## Benefits

1. ✅ **Zero risk of corruption** - Never accesses database while Vortex is running
2. ✅ **Automatic safety** - No manual checks needed
3. ✅ **Clear error messages** - Users know exactly what to do
4. ✅ **Fast operations** - Local copy means no Wine/Proton overhead
5. ✅ **Always fresh data** - Creates a new copy every time
6. ✅ **Backward compatible** - All scripts work the same way

## Technical Notes

- The local copy is a complete snapshot of the database
- **A fresh copy is created on every script run** to ensure latest data
- Scripts are still **read-only** on the local copy
- The original database is **never modified**
- Local copy can be safely deleted anytime (it will be recreated on next run)

