#!/usr/bin/env python3
"""
Explore the LevelDB database structure
"""
import plyvel
import sys
import config

def explore_database(db_path='state/'):
    """Explore the LevelDB database and show statistics"""
    try:
        db = plyvel.DB(db_path, create_if_missing=False)
    except Exception as e:
        print(f"Error opening database: {e}")
        return
    
    # Collect statistics
    total_entries = 0
    key_lengths = []
    value_lengths = []
    sample_entries = []
    
    print("Scanning database...")
    for key, value in db:
        total_entries += 1
        key_lengths.append(len(key))
        value_lengths.append(len(value))
        
        # Store first 10 entries as samples
        if len(sample_entries) < 10:
            sample_entries.append((key, value))
    
    # Print statistics
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    print(f"Total entries: {total_entries}")
    
    if key_lengths:
        print(f"\nKey lengths:")
        print(f"  Min: {min(key_lengths)} bytes")
        print(f"  Max: {max(key_lengths)} bytes")
        print(f"  Avg: {sum(key_lengths)/len(key_lengths):.2f} bytes")
        
        print(f"\nValue lengths:")
        print(f"  Min: {min(value_lengths)} bytes")
        print(f"  Max: {max(value_lengths)} bytes")
        print(f"  Avg: {sum(value_lengths)/len(value_lengths):.2f} bytes")
    
    # Show sample entries
    print("\n" + "="*80)
    print("SAMPLE ENTRIES (first 10)")
    print("="*80)
    
    for i, (key, value) in enumerate(sample_entries, 1):
        print(f"\n--- Entry {i} ---")
        print(f"Key length: {len(key)} bytes")
        print(f"Key (hex): {key.hex()}")
        print(f"Key (bytes): {key}")
        
        # Try to interpret key as string
        try:
            key_str = key.decode('utf-8')
            print(f"Key (utf-8): {key_str}")
        except:
            pass
        
        print(f"\nValue length: {len(value)} bytes")
        print(f"Value (hex): {value.hex()[:200]}{'...' if len(value.hex()) > 200 else ''}")
        
        # Try to interpret value as string
        try:
            value_str = value.decode('utf-8')
            print(f"Value (utf-8): {value_str[:200]}{'...' if len(value_str) > 200 else ''}")
        except:
            print(f"Value (raw bytes): {value[:100]}{'...' if len(value) > 100 else ''}")
    
    db.close()
    print("\n" + "="*80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Explore the LevelDB database structure')
    parser.add_argument('--db', default=None, help='Path to LevelDB database (default: auto-detect from config)')

    args = parser.parse_args()

    # Use config if no db path specified
    if args.db is None:
        try:
            args.db = config.get_safe_db_path()
        except (FileNotFoundError, RuntimeError) as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    explore_database(args.db)

