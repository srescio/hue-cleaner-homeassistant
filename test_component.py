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

def test_http_protocol_usage():
    """Test that all Hue Hub interactions use HTTP (not HTTPS)."""
    try:
        # Read the constants file directly to avoid import issues
        const_path = "custom_components/hue_cleaner/const.py"
        if not os.path.exists(const_path):
            print(f"❌ {const_path} not found")
            return False
            
        with open(const_path, 'r') as f:
            content = f.read()
        
        # Check for HTTP usage in the constants
        if 'HUE_API_BASE = "http://{ip}/api"' not in content:
            print(f"❌ HUE_API_BASE must use HTTP in {const_path}")
            return False
            
        if 'HUE_ENTERTAINMENT_API = "http://{ip}/clip/v2/resource/entertainment_configuration"' not in content:
            print(f"❌ HUE_ENTERTAINMENT_API must use HTTP in {const_path}")
            return False
            
        # Ensure no HTTPS usage for Hue Hub APIs
        if 'https://{ip}/api' in content:
            print(f"❌ HUE_API_BASE must not use HTTPS in {const_path}")
            return False
            
        if 'https://{ip}/clip/v2/resource/entertainment_configuration' in content:
            print(f"❌ HUE_ENTERTAINMENT_API must not use HTTPS in {const_path}")
            return False
        
        print(f"✅ HUE_API_BASE uses HTTP in {const_path}")
        print(f"✅ HUE_ENTERTAINMENT_API uses HTTP in {const_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error checking HTTP protocol usage: {e}")
        return False

def test_error_handling_structure():
    """Test that error handling components are properly structured."""
    try:
        # Check coordinator has error handling methods
        coordinator_path = "custom_components/hue_cleaner/coordinator.py"
        if not os.path.exists(coordinator_path):
            print(f"❌ {coordinator_path} not found")
            return False
            
        with open(coordinator_path, 'r') as f:
            content = f.read()
        
        # Check for error handling methods
        required_methods = [
            "_handle_connection_error",
            "_create_error_notification", 
            "_create_repair_issue",
            "_clear_repair_issues"
        ]
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing error handling methods in {coordinator_path}: {missing_methods}")
            return False
        
        # Check config flow has repair step
        config_flow_path = "custom_components/hue_cleaner/config_flow.py"
        if not os.path.exists(config_flow_path):
            print(f"❌ {config_flow_path} not found")
            return False
            
        with open(config_flow_path, 'r') as f:
            content = f.read()
        
        if "async_step_issue_repair" not in content:
            print(f"❌ Missing issue repair step in {config_flow_path}")
            return False
        
        # Check translations have error handling
        for lang in ["en", "it"]:
            translation_path = f"custom_components/hue_cleaner/translations/{lang}.json"
            if not os.path.exists(translation_path):
                print(f"❌ {translation_path} not found")
                return False
                
            with open(translation_path, 'r') as f:
                content = f.read()
            
            if '"issues"' not in content:
                print(f"❌ Missing issues translations in {translation_path}")
                return False
        
        print(f"✅ Error handling structure is complete")
        return True
        
    except Exception as e:
        print(f"❌ Error checking error handling structure: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Hue Cleaner component structure...\n")
    
    tests = [
        ("File Structure", test_structure),
        ("Manifest", test_manifest),
        ("Config Flow Steps", test_config_flow_steps),
        ("Translations", test_translations),
        ("Pytest Structure", test_pytest_structure),
        ("HTTP Protocol Usage", test_http_protocol_usage),
        ("Error Handling Structure", test_error_handling_structure),
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
