#!/usr/bin/env python3
"""
Compare what find_enabled_mods.py and deploy_mods.py see
"""
import plyvel
import json
import config

def compare_mods():
    db_path = config.get_safe_db_path()
    db = plyvel.DB(db_path, create_if_missing=False)
    
    active_profile_id = None
    mod_enabled_status = {}
    enabled_mods_with_time = {}
    mods_info = {}
    
    # Scan database
    for key, value in db:
        key_str = key.decode('utf-8', errors='ignore')
        
        # Find active profile
        if key_str == 'settings###profiles###lastActiveProfile###subnautica':
            try:
                active_profile_id = json.loads(value.decode('utf-8'))
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
        
        # Find enabled mods with enabledTime
        if '###modState###' in key_str and key_str.endswith('###enabledTime'):
            parts = key_str.split('###')
            if len(parts) >= 5:
                profile_id = parts[2]
                mod_id = parts[4]
                try:
                    enabled_time = value.decode('utf-8')
                    if profile_id not in enabled_mods_with_time:
                        enabled_mods_with_time[profile_id] = {}
                    enabled_mods_with_time[profile_id][mod_id] = enabled_time
                except:
                    pass
        
        # Collect mod information
        if key_str.startswith('persistent###mods###subnautica###'):
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
    
    db.close()
    
    if not active_profile_id:
        print("ERROR: Could not find active profile")
        return
    
    print(f"Active Profile: {active_profile_id}\n")
    
    # Get enabled mods from both methods
    enabled_by_flag = set(mod_id for mod_id, enabled in mod_enabled_status.get(active_profile_id, {}).items() if enabled)
    enabled_by_time = set(enabled_mods_with_time.get(active_profile_id, {}).keys())
    
    print(f"Mods with enabled=true flag: {len(enabled_by_flag)}")
    print(f"Mods with enabledTime: {len(enabled_by_time)}")
    print()
    
    # Find differences
    only_flag = enabled_by_flag - enabled_by_time
    only_time = enabled_by_time - enabled_by_flag
    both = enabled_by_flag & enabled_by_time
    
    print(f"Mods in BOTH (enabled=true AND enabledTime): {len(both)}")
    print(f"Mods ONLY with enabled=true flag: {len(only_flag)}")
    print(f"Mods ONLY with enabledTime: {len(only_time)}")
    print()
    
    # Check types for deploy_mods filtering
    deployable_mods = []
    for mod_id in both:
        mod_info = mods_info.get(mod_id, {})
        mod_type = mod_info.get('type', 'unknown')
        if mod_type in ['bepinex-5', 'bepinex-plugin']:
            deployable_mods.append(mod_id)
    
    print(f"Mods that deploy_mods.py would deploy (bepinex-5 or bepinex-plugin): {len(deployable_mods)}")
    print()
    
    # Show mods that find_enabled_mods sees but deploy_mods doesn't
    find_enabled_sees = both  # find_enabled_mods uses both flags
    deploy_sees = set(deployable_mods)
    
    missing_from_deploy = find_enabled_sees - deploy_sees
    
    if missing_from_deploy:
        print(f"Mods that find_enabled_mods.py shows but deploy_mods.py skips: {len(missing_from_deploy)}")
        print()
        for mod_id in sorted(missing_from_deploy):
            mod_info = mods_info.get(mod_id, {})
            mod_name = mod_info.get('name', mod_id)
            mod_type = mod_info.get('type', 'unknown')
            print(f"  - {mod_name}")
            print(f"    Type: {mod_type}")
            print(f"    Reason: {'Not bepinex-5 or bepinex-plugin' if mod_type not in ['bepinex-5', 'bepinex-plugin'] else 'Unknown'}")
            print()

if __name__ == "__main__":
    compare_mods()

