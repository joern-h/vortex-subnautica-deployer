#!/usr/bin/env python3
"""
Deploy Subnautica mods by symlinking from staging to game directory.
Fixes Vortex's broken mod installer on Linux.
"""
import plyvel
import json
import os
import sys
import shutil
from pathlib import Path
import config

def win_to_linux(win_path):
    r"""Convert Windows path (Z:\...) to Linux path"""
    if not win_path:
        return None
    if win_path.startswith('Z:\\'):
        # Remove Z:\ and convert backslashes to forward slashes
        linux_path = win_path[3:].replace('\\', '/')
        return '/' + linux_path
    return win_path.replace('\\', '/')

def get_mod_data(db_path='state/', game='subnautica'):
    """Extract mod data from Vortex database"""
    try:
        db = plyvel.DB(db_path, create_if_missing=False)
    except Exception as e:
        print(f"ERROR: Could not open database: {e}")
        return None
    
    # Collect data
    active_profile_id = None
    mods_info = {}
    mod_enabled_status = {}
    game_path = None
    staging_path = None
    
    for key, value in db:
        key_str = key.decode('utf-8', errors='ignore')
        
        # Find active profile
        if key_str == f'settings###profiles###lastActiveProfile###{game}':
            try:
                active_profile_id = json.loads(value.decode('utf-8'))
            except:
                pass
        
        # Find enabled status
        if '###modState###' in key_str and key_str.endswith('###enabled'):
            parts = key_str.split('###')
            if len(parts) >= 5:
                profile_id = parts[2]
                mod_id = parts[4]
                try:
                    is_enabled = value.decode('utf-8') == 'true'
                    if profile_id not in mod_enabled_status:
                        mod_enabled_status[profile_id] = {}
                    mod_enabled_status[profile_id][mod_id] = is_enabled
                except:
                    pass
        
        # Collect mod information
        if key_str.startswith(f'persistent###mods###{game}###'):
            parts = key_str.split('###')
            if len(parts) >= 4:
                mod_id = parts[3]
                if mod_id not in mods_info:
                    mods_info[mod_id] = {'id': mod_id}
                
                if len(parts) == 5:
                    field = parts[4]
                    try:
                        value_str = value.decode('utf-8')
                        if field in ['installationPath', 'type', 'state']:
                            mods_info[mod_id][field] = json.loads(value_str)
                    except:
                        pass
                
                # Get name from attributes
                if len(parts) >= 6 and parts[4] == 'attributes' and parts[5] == 'name':
                    try:
                        mods_info[mod_id]['name'] = json.loads(value.decode('utf-8'))
                    except:
                        pass
        
        # Get game path
        if key_str == f'settings###gameMode###discovered###{game}###path':
            try:
                game_path = json.loads(value.decode('utf-8'))
            except:
                pass
        
        # Get staging path
        if key_str == f'settings###mods###installPath###{game}':
            try:
                staging_path = json.loads(value.decode('utf-8'))
            except:
                pass
    
    db.close()
    
    if not active_profile_id:
        print(f"ERROR: Could not find active profile for {game}")
        return None
    
    return {
        'active_profile_id': active_profile_id,
        'mods_info': mods_info,
        'mod_enabled_status': mod_enabled_status.get(active_profile_id, {}),
        'game_path': win_to_linux(game_path),
        'staging_path': win_to_linux(staging_path)
    }

def symlink_directory_contents(src_dir, dest_dir, dry_run=False):
    """Recursively symlink directory contents"""
    if not os.path.exists(src_dir):
        return []
    
    created_links = []
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isdir(src_path):
            # Create directory if it doesn't exist
            if not dry_run and not os.path.exists(dest_path):
                os.makedirs(dest_path, exist_ok=True)
            # Recursively symlink contents
            created_links.extend(symlink_directory_contents(src_path, dest_path, dry_run))
        else:
            # Symlink file
            if os.path.exists(dest_path) or os.path.islink(dest_path):
                if not dry_run:
                    os.remove(dest_path)
            
            if not dry_run:
                os.symlink(src_path, dest_path)
            created_links.append(dest_path)
    
    return created_links

def deploy_mods(db_path='state/', game='subnautica', dry_run=False):
    """Deploy mods by symlinking from staging to game directory"""
    print("="*80)
    print("VORTEX MOD DEPLOYMENT SCRIPT FOR LINUX")
    print("="*80)
    print()

    # Get mod data
    data = get_mod_data(db_path, game)
    if not data:
        return False

    mods_info = data['mods_info']
    enabled_status = data['mod_enabled_status']
    game_path = data['game_path']
    staging_path = data['staging_path']

    print(f"Game Path: {game_path}")
    print(f"Staging Path: {staging_path}")
    print(f"Active Profile: {data['active_profile_id']}")
    print()

    # Verify paths exist
    if not os.path.exists(game_path):
        print(f"ERROR: Game path does not exist: {game_path}")
        return False

    if not os.path.exists(staging_path):
        print(f"ERROR: Staging path does not exist: {staging_path}")
        return False

    # Filter enabled mods
    enabled_mods = []
    for mod_id, mod_info in mods_info.items():
        if enabled_status.get(mod_id, False):
            mod_type = mod_info.get('type', 'unknown')
            # Skip collections
            if mod_type == 'collection':
                continue
            # Only process bepinex-5 and bepinex-plugin
            if mod_type in ['bepinex-5', 'bepinex-plugin']:
                enabled_mods.append((mod_id, mod_info))

    # Sort: bepinex-5 first, then bepinex-plugin
    enabled_mods.sort(key=lambda x: (0 if x[1].get('type') == 'bepinex-5' else 1, x[1].get('name', x[0])))

    # Print summary
    print(f"Found {len(enabled_mods)} enabled mods to deploy:")
    print()

    bepinex_count = sum(1 for _, m in enabled_mods if m.get('type') == 'bepinex-5')
    plugin_count = sum(1 for _, m in enabled_mods if m.get('type') == 'bepinex-plugin')

    print(f"  - BepInEx Framework: {bepinex_count}")
    print(f"  - BepInEx Plugins: {plugin_count}")
    print()

    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()

    # Deploy mods
    total_links = 0

    for mod_id, mod_info in enabled_mods:
        mod_name = mod_info.get('name', mod_id)
        mod_type = mod_info.get('type', 'unknown')
        install_path = mod_info.get('installationPath')

        if not install_path:
            print(f"⚠ SKIP: {mod_name} - No installation path")
            continue

        mod_staging_path = os.path.join(staging_path, install_path)

        if not os.path.exists(mod_staging_path):
            print(f"⚠ SKIP: {mod_name} - Staging directory not found: {mod_staging_path}")
            continue

        print(f"{'[DRY RUN] ' if dry_run else ''}Deploying: {mod_name}")
        print(f"  Type: {mod_type}")
        print(f"  From: {mod_staging_path}")

        created_links = []

        if mod_type == 'bepinex-5':
            # Deploy BepInEx framework to game root
            print(f"  To: {game_path} (game root)")
            created_links = symlink_directory_contents(mod_staging_path, game_path, dry_run)

        elif mod_type == 'bepinex-plugin':
            # Deploy plugins to BepInEx/plugins directory
            bepinex_plugins_dir = os.path.join(game_path, 'BepInEx', 'plugins')

            # Create BepInEx/plugins if it doesn't exist
            if not dry_run and not os.path.exists(bepinex_plugins_dir):
                os.makedirs(bepinex_plugins_dir, exist_ok=True)

            print(f"  To: {bepinex_plugins_dir}")
            created_links = symlink_directory_contents(mod_staging_path, bepinex_plugins_dir, dry_run)

        print(f"  Created {len(created_links)} symlinks")
        total_links += len(created_links)
        print()

    print("="*80)
    print(f"DEPLOYMENT {'PREVIEW' if dry_run else 'COMPLETE'}")
    print("="*80)
    print(f"Total mods processed: {len(enabled_mods)}")
    print(f"Total symlinks {'would be ' if dry_run else ''}created: {total_links}")
    print()

    if dry_run:
        print("Run without --dry-run to actually deploy the mods")

    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Deploy Subnautica mods from Vortex staging to game directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be deployed
  python3 deploy_mods.py --dry-run

  # Actually deploy the mods
  python3 deploy_mods.py

  # Use custom database path
  python3 deploy_mods.py --db /path/to/state/
        """
    )
    parser.add_argument('--db', default=None, help='Path to LevelDB database (default: auto-detect from config)')
    parser.add_argument('--game', default=config.DEFAULT_GAME, help=f'Game name (default: {config.DEFAULT_GAME})')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without making them')

    args = parser.parse_args()

    # Use config if no db path specified
    if args.db is None:
        try:
            args.db = config.get_db_path()
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    success = deploy_mods(args.db, args.game, args.dry_run)
    sys.exit(0 if success else 1)
