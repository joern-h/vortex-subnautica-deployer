#!/usr/bin/env python3
"""
Find enabled mods for Subnautica (current profile only)
"""
import plyvel
import json
import sys
import config

def find_enabled_mods(db_path='state/', game='subnautica'):
    """Find all enabled mods for the current profile"""
    try:
        db = plyvel.DB(db_path, create_if_missing=False)
    except Exception as e:
        print(f"Error opening database: {e}")
        return

    # First, find the active profile for the game
    active_profile_id = None
    profiles = {}
    mods_info = {}
    enabled_mods = {}
    mod_enabled_status = {}

    print("Scanning database...")

    for key, value in db:
        key_str = key.decode('utf-8', errors='ignore')

        # Find active profile for the game
        if key_str == f'settings###profiles###lastActiveProfile###subnautica':
            try:
                active_profile_id = json.loads(value.decode('utf-8'))
                print(f"Active profile ID: {active_profile_id}")
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

        # Find enabled status (true/false flag)
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

        # Find enabled mods in profiles (modState entries with enabledTime)
        if '###modState###' in key_str and key_str.endswith('###enabledTime'):
            parts = key_str.split('###')
            if len(parts) >= 5:
                profile_id = parts[2]
                mod_id = parts[4]
                try:
                    enabled_time = value.decode('utf-8')
                    if profile_id not in enabled_mods:
                        enabled_mods[profile_id] = {}
                    enabled_mods[profile_id][mod_id] = enabled_time
                except:
                    pass

        # Collect mod information for subnautica
        if key_str.startswith('persistent###mods###subnautica###'):
            parts = key_str.split('###')
            if len(parts) >= 4:
                mod_id = parts[3]
                if mod_id not in mods_info:
                    mods_info[mod_id] = {}

                # Extract the attribute name
                if len(parts) >= 6 and parts[4] == 'attributes':
                    attr_name = parts[5]
                    try:
                        attr_value = json.loads(value.decode('utf-8'))
                        mods_info[mod_id][attr_name] = attr_value
                    except:
                        pass

    db.close()

    if not active_profile_id:
        print("ERROR: Could not find active profile for Subnautica!")
        return

    # Get the active profile's mods
    profile_name = profiles.get(active_profile_id, f"Unknown ({active_profile_id})")
    profile_mods = enabled_mods.get(active_profile_id, {})
    profile_enabled_status = mod_enabled_status.get(active_profile_id, {})

    # Filter to only truly enabled mods (where enabled=true)
    truly_enabled_mods = {}
    for mod_id, enabled_time in profile_mods.items():
        if profile_enabled_status.get(mod_id, False):
            truly_enabled_mods[mod_id] = enabled_time

    # Display results
    print("\n" + "="*80)
    print(f"CURRENT PROFILE: {profile_name}")
    print("="*80)
    print(f"Profile ID: {active_profile_id}")
    print(f"Total enabled mods: {len(truly_enabled_mods)}")
    print(f"Total installed mods: {len(mods_info)}\n")

    if not truly_enabled_mods:
        print("No mods are currently enabled in this profile.")
        return

    # Sort by enabled time (most recent first)
    sorted_mods = sorted(truly_enabled_mods.items(), key=lambda x: x[1], reverse=True)

    print("="*80)
    print("ENABLED MODS")
    print("="*80 + "\n")

    for i, (mod_id, enabled_time) in enumerate(sorted_mods, 1):
        mod_info = mods_info.get(mod_id, {})
        mod_name = mod_info.get('name', mod_id)
        mod_version = mod_info.get('modVersion', 'unknown')
        mod_author = mod_info.get('author', 'unknown')

        print(f"{i:3d}. {mod_name}")
        print(f"     Version: {mod_version}")
        print(f"     Author: {mod_author}")

        # Show short description if available
        short_desc = mod_info.get('shortDescription', '')
        if short_desc:
            # Truncate if too long
            if len(short_desc) > 100:
                short_desc = short_desc[:97] + "..."
            print(f"     Description: {short_desc}")

        # Optionally show mod ID and enabled time (commented out for cleaner output)
        # print(f"     Mod ID: {mod_id}")
        # print(f"     Enabled: {enabled_time}")
        print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Find enabled mods for current profile')
    parser.add_argument('--db', default=None, help='Path to LevelDB database (default: auto-detect from config)')
    parser.add_argument('--game', default=config.DEFAULT_GAME, help=f'Game name (default: {config.DEFAULT_GAME})')

    args = parser.parse_args()

    # Use config if no db path specified
    if args.db is None:
        try:
            args.db = config.get_db_path()
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    find_enabled_mods(args.db, args.game)

