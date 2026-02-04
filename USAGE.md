# Quick Usage Guide

## Main Scripts

### 🚀 Deploy Mods (Fix Vortex on Linux)
```bash
# Preview deployment
python3 deploy_mods.py --dry-run

# Deploy mods
python3 deploy_mods.py
```

### 🧹 Remove All Symlinks
```bash
# Preview cleanup
python3 cleanup_mods.py --dry-run

# Remove symlinks
python3 cleanup_mods.py
```

## Information Scripts

### 📋 Show Enabled Mods
```bash
python3 find_enabled_mods.py
```

### 📁 Show Mod Paths
```bash
# Only enabled mods
python3 find_mod_paths.py

# All mods
python3 find_mod_paths.py --all
```

### 🔍 Explore Database
```bash
python3 explore_db.py
```

## Common Workflows

### First Time Setup
```bash
# 1. Check what mods are enabled
python3 find_enabled_mods.py

# 2. Preview deployment
python3 deploy_mods.py --dry-run

# 3. Deploy mods
python3 deploy_mods.py
```

### Switching Profiles in Vortex
```bash
# 1. Switch profile in Vortex
# 2. Clean up old symlinks
python3 cleanup_mods.py

# 3. Deploy new profile's mods
python3 deploy_mods.py
```

### Troubleshooting
```bash
# Check if mods are deployed
python3 cleanup_mods.py --dry-run

# See what mods should be enabled
python3 find_enabled_mods.py

# Check mod installation paths
python3 find_mod_paths.py
```

### Complete Reset
```bash
# Remove all symlinks
python3 cleanup_mods.py

# Redeploy from scratch
python3 deploy_mods.py
```

## Quick Reference

| Script | Purpose | Key Options |
|--------|---------|-------------|
| `deploy_mods.py` | Deploy mods to game | `--dry-run` |
| `cleanup_mods.py` | Remove symlinks | `--dry-run`, `--verbose` |
| `find_enabled_mods.py` | List enabled mods | - |
| `find_mod_paths.py` | Show mod paths | `--all` |
| `explore_db.py` | Database stats | - |
| `analyze_keys.py` | Key patterns | - |
| `dump_all.py` | Export to JSON | - |

## Safety Tips

✅ **Always use `--dry-run` first** to preview changes  
✅ **cleanup_mods.py only removes symlinks**, never real files  
✅ **Your mods stay safe** in the staging directory  
✅ **You can always redeploy** by running deploy_mods.py again  

## Help

All scripts support `--help`:
```bash
python3 deploy_mods.py --help
python3 cleanup_mods.py --help
python3 find_mod_paths.py --help
```

