#!/usr/bin/env python3
"""
Dump all entries from the LevelDB database
"""
import plyvel
import sys
import json
import config

def dump_database(db_path='state/', output_file=None):
    """Dump all database entries"""
    try:
        db = plyvel.DB(db_path, create_if_missing=False)
    except Exception as e:
        print(f"Error opening database: {e}")
        return
    
    entries = []
    
    print("Reading all entries...")
    for key, value in db:
        entry = {
            'key_hex': key.hex(),
            'key_bytes': list(key),
            'value_hex': value.hex(),
            'value_bytes': list(value),
            'key_length': len(key),
            'value_length': len(value)
        }
        
        # Try to decode as UTF-8
        try:
            entry['key_utf8'] = key.decode('utf-8')
        except:
            pass
        
        try:
            entry['value_utf8'] = value.decode('utf-8')
        except:
            pass
        
        entries.append(entry)
    
    db.close()
    
    print(f"Total entries: {len(entries)}")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(entries, f, indent=2)
        print(f"Dumped to {output_file}")
    else:
        # Print to stdout
        print(json.dumps(entries, indent=2))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Dump all entries from the LevelDB database')
    parser.add_argument('--db', default=None, help='Path to LevelDB database (default: auto-detect from config)')
    parser.add_argument('--output', '-o', default=None, help='Output file (default: stdout)')

    args = parser.parse_args()

    # Use config if no db path specified
    if args.db is None:
        try:
            args.db = config.get_safe_db_path()
        except (FileNotFoundError, RuntimeError) as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    dump_database(args.db, args.output)

