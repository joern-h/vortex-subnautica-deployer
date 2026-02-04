#!/usr/bin/env python3
"""
Find installation paths and details for Subnautica mods
"""
import plyvel
import json
import sys
import os
import config

def find_mod_paths(db_path='state/', game='subnautica', show_all=False):
    """Find installation paths for mods"""
    try:
        db = plyvel.DB(db_path, create_if_missing=False)
    except Exception as e:
        print(f"Error opening database: {e}")
        return
    
    # Collect data
    active_profile_id = None
    profiles = {}
    mods_info = {}
    mod_enabled_status = {}
    game_path = None
    staging_path = None
    
    print("Scanning database...")
    
    for key, value in db:
        key_str = key.decode('utf-8', errors='ignore')
        
        # Find active profile
        if key_str == f'settings###profiles###lastActiveProfile###{game}':
            try:
                active_profile_id = json.loads(value.decode('utf-8'))
            except:
                pass
        
        # Find profile names
        if key_str.startswith('persistent###profiles###') and key_str.endswith('###name'):
            profile_id = key_str.split('###')[2]
            try:
                profile_name = json.loads(value.decode('utf-8'))
                profiles[profile_id] = profile_name
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
                    mods_info[mod_id] = {}
                
                # Get installation path
                if len(parts) == 5 and parts[4] == 'installationPath':
                    try:
                        mods_info[mod_id]['installationPath'] = json.loads(value.decode('utf-8'))
                    except:
                        pass
                
                # Get mod type
                if len(parts) == 5 and parts[4] == 'type':
                    try:
                        mods_info[mod_id]['type'] = json.loads(value.decode('utf-8'))
                    except:
                        pass
                
                # Get mod state
                if len(parts) == 5 and parts[4] == 'state':
                    try:
                        mods_info[mod_id]['state'] = json.loads(value.decode('utf-8'))
                    except:
                        pass
                
                # Get attributes
                if len(parts) >= 6 and parts[4] == 'attributes':
                    attr_name = parts[5]
                    try:
                        attr_value = json.loads(value.decode('utf-8'))
                        mods_info[mod_id][attr_name] = attr_value
                    except:
                        pass
        
        # Get game path
        if key_str == f'settings###gameMode###discovered###{game}###path':
            try:
                game_path = json.loads(value.decode('utf-8'))
            except:
                pass
        
        # Get staging/install path
        if key_str == f'settings###mods###installPath###{game}':
            try:
                staging_path = json.loads(value.decode('utf-8'))
            except:
                pass
    
    db.close()
    
    if not active_profile_id:
        print(f"ERROR: Could not find active profile for {game}!")
        return
    
    # Get enabled mods for active profile
    profile_enabled_status = mod_enabled_status.get(active_profile_id, {})
    
    # Display results
    profile_name = profiles.get(active_profile_id, f"Unknown ({active_profile_id})")
    
    print("\n" + "="*80)
    print(f"INSTALLATION PATHS - {game.upper()}")
    print("="*80)
    print(f"Current Profile: {profile_name} ({active_profile_id})")
    print(f"\nGame Path: {game_path}")
    print(f"Staging Path: {staging_path}")
    print(f"\nTotal mods: {len(mods_info)}")
    
    # Filter mods if not showing all
    if not show_all:
        enabled_count = sum(1 for mod_id in mods_info.keys() 
                          if profile_enabled_status.get(mod_id, False))
        print(f"Enabled mods: {enabled_count}")
    
    print("\n" + "="*80)
    print("MOD INSTALLATION DETAILS")
    print("="*80 + "\n")
    
    # Sort mods by name
    sorted_mods = sorted(mods_info.items(), 
                        key=lambda x: x[1].get('name', x[0]))
    
    for mod_id, mod_info in sorted_mods:
        is_enabled = profile_enabled_status.get(mod_id, False)
        
        # Skip disabled mods if not showing all
        if not show_all and not is_enabled:
            continue
        
        mod_name = mod_info.get('name', mod_id)
        mod_version = mod_info.get('modVersion', 'unknown')
        install_path = mod_info.get('installationPath', 'N/A')
        mod_type = mod_info.get('type', 'unknown')
        mod_state = mod_info.get('state', 'unknown')
        
        status = "✓ ENABLED" if is_enabled else "✗ Disabled"
        
        print(f"[{status}] {mod_name}")
        print(f"  Version: {mod_version}")
        print(f"  Type: {mod_type}")
        print(f"  State: {mod_state}")
        print(f"  Installation Path: {install_path}")
        
        if staging_path:
            full_path = os.path.join(staging_path, install_path)
            print(f"  Full Path: {full_path}")
        
        print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Find mod installation paths')
    parser.add_argument('--db', default=None, help='Path to LevelDB database (default: auto-detect from config)')
    parser.add_argument('--game', default=config.DEFAULT_GAME, help=f'Game name (default: {config.DEFAULT_GAME})')
    parser.add_argument('--all', action='store_true', help='Show all mods (not just enabled)')

    args = parser.parse_args()

    # Use config if no db path specified
    if args.db is None:
        try:
            args.db = config.get_safe_db_path()
        except (FileNotFoundError, RuntimeError) as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    find_mod_paths(args.db, args.game, args.all)

