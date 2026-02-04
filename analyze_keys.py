#!/usr/bin/env python3
"""
Analyze key patterns in the LevelDB database
"""
import plyvel
import sys
from collections import defaultdict

def analyze_keys(db_path='state/'):
    """Analyze key patterns and structure"""
    try:
        db = plyvel.DB(db_path, create_if_missing=False)
    except Exception as e:
        print(f"Error opening database: {e}")
        return
    
    # Collect key patterns
    key_prefixes = defaultdict(int)
    key_by_length = defaultdict(list)
    
    print("Analyzing keys...")
    for key, value in db:
        # Group by length
        key_by_length[len(key)].append((key, value))
        
        # Try to find common prefixes (first 1-4 bytes)
        for prefix_len in [1, 2, 4, 8]:
            if len(key) >= prefix_len:
                prefix = key[:prefix_len]
                key_prefixes[(prefix_len, prefix)] += 1
    
    # Print results
    print("\n" + "="*80)
    print("KEY LENGTH DISTRIBUTION")
    print("="*80)
    for length in sorted(key_by_length.keys()):
        count = len(key_by_length[length])
        print(f"Length {length:3d}: {count:6d} keys")
        
        # Show a few examples
        if count <= 5:
            for key, value in key_by_length[length][:5]:
                print(f"  Example: {key.hex()}")
    
    print("\n" + "="*80)
    print("COMMON KEY PREFIXES")
    print("="*80)
    
    for prefix_len in [1, 2, 4, 8]:
        print(f"\n{prefix_len}-byte prefixes:")
        prefixes_at_len = [(prefix, count) for (plen, prefix), count in key_prefixes.items() if plen == prefix_len]
        prefixes_at_len.sort(key=lambda x: x[1], reverse=True)
        
        for prefix, count in prefixes_at_len[:10]:  # Top 10
            print(f"  {prefix.hex():20s} : {count:6d} keys")
    
    # Detailed analysis of each key length group
    print("\n" + "="*80)
    print("DETAILED ANALYSIS BY KEY LENGTH")
    print("="*80)
    
    for length in sorted(key_by_length.keys()):
        entries = key_by_length[length]
        print(f"\n--- Keys of length {length} ({len(entries)} total) ---")
        
        # Show first 3 examples with their values
        for i, (key, value) in enumerate(entries[:3], 1):
            print(f"\nExample {i}:")
            print(f"  Key (hex):   {key.hex()}")
            print(f"  Value (hex): {value.hex()[:100]}{'...' if len(value.hex()) > 100 else ''}")
            print(f"  Value size:  {len(value)} bytes")
    
    db.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'state/'
    analyze_keys(db_path)

