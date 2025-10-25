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
        "custom_components/hue_cleaner/translations/en.json",
        "custom_components/hue_cleaner/translations/it.json",
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

def test_config_flow_steps():
    """Test that config flow has all required steps."""
    config_flow_path = "custom_components/hue_cleaner/config_flow.py"
    
    if not os.path.exists(config_flow_path):
        print(f"❌ {config_flow_path} not found")
        return False
    
    try:
        with open(config_flow_path, 'r') as f:
            content = f.read()
        
        required_steps = [
            "async_step_user",
            "async_step_api_key",
            "async_step_retry_api_key",
            "async_step_final_test"
        ]
        
        missing_steps = []
        for step in required_steps:
            if step not in content:
                missing_steps.append(step)
        
        if missing_steps:
            print(f"❌ Missing config flow steps: {missing_steps}")
            return False
        
        print(f"✅ {config_flow_path} has all required steps")
        return True
        
    except Exception as e:
        print(f"❌ Error reading {config_flow_path}: {e}")
        return False

def test_translations():
    """Test that translation files have all required step descriptions."""
    translation_files = [
        "custom_components/hue_cleaner/translations/en.json",
        "custom_components/hue_cleaner/translations/it.json"
    ]
    
    required_steps = [
        "user", "api_key", "retry_api_key", "final_test"
    ]
    
    for translation_path in translation_files:
        if not os.path.exists(translation_path):
            print(f"❌ {translation_path} not found")
            return False
        
        try:
            with open(translation_path, 'r') as f:
                translations = json.load(f)
            
            missing_steps = []
            for step in required_steps:
                if step not in translations.get("config", {}).get("step", {}):
                    missing_steps.append(step)
            
            if missing_steps:
                print(f"❌ Missing translations for steps in {translation_path}: {missing_steps}")
                return False
            
            print(f"✅ {translation_path} has all required step descriptions")
            
        except json.JSONDecodeError as e:
            print(f"❌ {translation_path} is not valid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading {translation_path}: {e}")
            return False
    
    return True

def test_pytest_structure():
    """Test that pytest test structure exists."""
    required_files = [
        "tests/__init__.py",
        "tests/conftest.py", 
        "tests/test_config_flow.py",
        "tests/test_coordinator.py",
        "tests/test_sensor.py",
        "pytest.ini"
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
        ("Config Flow Steps", test_config_flow_steps),
        ("Translations", test_translations),
        ("Pytest Structure", test_pytest_structure),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        if not test_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All tests passed! Component is ready for testing.")
        print("\n💡 To run pytest tests: pytest tests/")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
