#!/usr/bin/env python3
"""Check commit message length."""
import sys

MAX_LENGTH = 150

def main():
    if len(sys.argv) != 2:
        print("Usage: check_commit_length.py <commit_message_file>")
        sys.exit(1)
    
    commit_file = sys.argv[1]
    
    try:
        with open(commit_file, 'r') as f:
            commit_msg = f.read().strip()
        
        if len(commit_msg) > MAX_LENGTH:
            print(f"❌ Commit message too long!")
            print(f"Current length: {len(commit_msg)} characters")
            print(f"Maximum allowed: {MAX_LENGTH} characters")
            print(f"Message: {commit_msg}")
            sys.exit(1)
        
        print(f"✅ Commit message length OK ({len(commit_msg)}/{MAX_LENGTH} chars)")
        sys.exit(0)
        
    except FileNotFoundError:
        print(f"❌ Commit message file not found: {commit_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading commit message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
