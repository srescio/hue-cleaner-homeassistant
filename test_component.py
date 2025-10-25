#!/usr/bin/env python3
"""Simple test script to verify the component structure."""

import json
import os
import sys

def test_manifest():
    """Test that manifest.json is valid."""
    manifest_path = "custom_components/hue_cleaner/manifest.json"
    
    if not os.path.exists(manifest_path):
        print(f"❌ {manifest_path} not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        required_fields = ["domain", "name", "version", "requirements"]
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ {manifest_path} is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {manifest_path} is not valid JSON: {e}")
        return False

def test_structure():
    """Test that all required files exist."""
    required_files = [
        "custom_components/hue_cleaner/__init__.py",
        "custom_components/hue_cleaner/manifest.json",
        "custom_components/hue_cleaner/const.py",
        "custom_components/hue_cleaner/config_flow.py",
        "custom_components/hue_cleaner/coordinator.py",
        "custom_components/hue_cleaner/sensor.py",
        "custom_components/hue_cleaner/services.py",
        "custom_components/hue_cleaner/services.yaml",
        "custom_components/hue_cleaner/strings.json",
        "hacs.json",
        "README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🧪 Testing Hue Cleaner component structure...\n")
    
    tests = [
        ("File Structure", test_structure),
        ("Manifest", test_manifest),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        if not test_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All tests passed! Component is ready for testing.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
