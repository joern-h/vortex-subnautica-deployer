#!/usr/bin/env python3
"""
Remove mod symlinks from the game directory.
Safely undeploys mods by removing only symlinks (not real files).
"""
import os
import sys
from pathlib import Path
import config

def find_symlinks(directory, recursive=True):
    """Find all symlinks in a directory"""
    symlinks = []
    
    if not os.path.exists(directory):
        return symlinks
    
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.islink(item_path):
                symlinks.append(item_path)
            elif recursive and os.path.isdir(item_path) and not os.path.islink(item_path):
                # Recursively search subdirectories
                symlinks.extend(find_symlinks(item_path, recursive=True))
    except PermissionError:
        pass
    
    return symlinks

def cleanup_mods(game_path, dry_run=False, verbose=False):
    """Remove mod symlinks from game directory"""
    print("="*80)
    print("VORTEX MOD CLEANUP SCRIPT")
    print("="*80)
    print()
    
    if not os.path.exists(game_path):
        print(f"ERROR: Game path does not exist: {game_path}")
        return False
    
    print(f"Game Path: {game_path}")
    print()
    
    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    # Find symlinks in game root
    print("Scanning for symlinks in game root...")
    root_symlinks = []
    for item in os.listdir(game_path):
        item_path = os.path.join(game_path, item)
        if os.path.islink(item_path):
            root_symlinks.append(item_path)
    
    print(f"Found {len(root_symlinks)} symlinks in game root")
    
    # Find symlinks in BepInEx directory
    bepinex_dir = os.path.join(game_path, 'BepInEx')
    bepinex_symlinks = []
    
    if os.path.exists(bepinex_dir):
        print("Scanning for symlinks in BepInEx directory...")
        bepinex_symlinks = find_symlinks(bepinex_dir, recursive=True)
        print(f"Found {len(bepinex_symlinks)} symlinks in BepInEx directory")
    
    all_symlinks = root_symlinks + bepinex_symlinks
    
    if not all_symlinks:
        print()
        print("No symlinks found. Nothing to clean up.")
        return True
    
    print()
    print(f"Total symlinks to remove: {len(all_symlinks)}")
    print()
    
    if verbose or dry_run:
        print("Symlinks to be removed:")
        for symlink in all_symlinks:
            target = os.readlink(symlink) if os.path.islink(symlink) else "?"
            rel_path = os.path.relpath(symlink, game_path)
            print(f"  {rel_path} -> {target}")
        print()
    
    if not dry_run:
        print("Removing symlinks...")
        removed_count = 0
        failed_count = 0
        
        for symlink in all_symlinks:
            try:
                os.remove(symlink)
                removed_count += 1
                if verbose:
                    print(f"  ✓ Removed: {os.path.relpath(symlink, game_path)}")
            except Exception as e:
                failed_count += 1
                print(f"  ✗ Failed to remove {symlink}: {e}")
        
        print()
        print("="*80)
        print("CLEANUP COMPLETE")
        print("="*80)
        print(f"Symlinks removed: {removed_count}")
        if failed_count > 0:
            print(f"Failed: {failed_count}")
    else:
        print("="*80)
        print("CLEANUP PREVIEW")
        print("="*80)
        print(f"Symlinks would be removed: {len(all_symlinks)}")
        print()
        print("Run without --dry-run to actually remove the symlinks")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Remove mod symlinks from game directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be removed
  python3 cleanup_mods.py --dry-run
  
  # Actually remove symlinks
  python3 cleanup_mods.py
  
  # Remove with verbose output
  python3 cleanup_mods.py --verbose
  
  # Use custom game path
  python3 cleanup_mods.py --game-path /path/to/game/
        """
    )
    parser.add_argument('--game-path',
                       default=None,
                       help='Path to game directory (default: auto-detect from config)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without making them')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')

    args = parser.parse_args()

    # Use config if no game path specified
    if args.game_path is None:
        try:
            args.game_path = config.get_game_path()
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    success = cleanup_mods(args.game_path, args.dry_run, args.verbose)
    sys.exit(0 if success else 1)

