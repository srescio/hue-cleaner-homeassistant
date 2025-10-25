#!/usr/bin/env python3
"""Test error handling logic without Home Assistant dependencies."""

import sys
import os
import re

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_error_handling_methods_exist():
    """Test that error handling methods exist in coordinator."""
    coordinator_path = "custom_components/hue_cleaner/coordinator.py"
    
    with open(coordinator_path, 'r') as f:
        content = f.read()
    
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
        print(f"❌ Missing error handling methods: {missing_methods}")
        return False
    
    print("✅ All error handling methods exist")
    return True

def test_error_detection_logic():
    """Test error detection logic in coordinator."""
    coordinator_path = "custom_components/hue_cleaner/coordinator.py"
    
    with open(coordinator_path, 'r') as f:
        content = f.read()
    
    # Check for IP change detection
    if "Connection refused" not in content or "No route to host" not in content:
        print("❌ IP change detection logic missing")
        return False
    
    # Check for API key expiration detection
    if "Unauthorized" not in content or "401" not in content:
        print("❌ API key expiration detection logic missing")
        return False
    
    # Check for error handling calls
    if "_handle_connection_error" not in content:
        print("❌ Error handling calls missing")
        return False
    
    print("✅ Error detection logic exists")
    return True

def test_repair_flow_exists():
    """Test repair flow exists in config flow."""
    config_flow_path = "custom_components/hue_cleaner/config_flow.py"
    
    with open(config_flow_path, 'r') as f:
        content = f.read()
    
    # Check for repair step
    if "async_step_issue_repair" not in content:
        print("❌ Repair step missing")
        return False
    
    # Check for issue context handling
    if "issue_id" not in content:
        print("❌ Issue context handling missing")
        return False
    
    print("✅ Repair flow exists")
    return True

def test_notification_creation():
    """Test notification creation logic."""
    coordinator_path = "custom_components/hue_cleaner/coordinator.py"
    
    with open(coordinator_path, 'r') as f:
        content = f.read()
    
    # Check for notification creation
    if "persistent_notification" not in content:
        print("❌ Notification creation missing")
        return False
    
    # Check for different error types
    if "ip_change" not in content or "api_key_expired" not in content:
        print("❌ Error type handling missing")
        return False
    
    print("✅ Notification creation logic exists")
    return True

def test_repair_issue_creation():
    """Test repair issue creation logic."""
    coordinator_path = "custom_components/hue_cleaner/coordinator.py"
    
    with open(coordinator_path, 'r') as f:
        content = f.read()
    
    # Check for issue registry usage
    if "issue_registry" not in content:
        print("❌ Issue registry usage missing")
        return False
    
    # Check for issue creation
    if "async_create_issue" not in content:
        print("❌ Issue creation missing")
        return False
    
    print("✅ Repair issue creation logic exists")
    return True

def test_translation_keys():
    """Test translation keys for error handling."""
    for lang in ["en", "it"]:
        translation_path = f"custom_components/hue_cleaner/translations/{lang}.json"
        
        with open(translation_path, 'r') as f:
            content = f.read()
        
        # Check for issues section
        if '"issues"' not in content:
            print(f"❌ Issues translations missing in {lang}")
            return False
        
        # Check for specific error types
        if "ip_change" not in content or "api_key_expired" not in content:
            print(f"❌ Error type translations missing in {lang}")
            return False
    
    print("✅ Translation keys exist")
    return True

def test_connection_issues_counter():
    """Test connection issues counter logic."""
    coordinator_path = "custom_components/hue_cleaner/coordinator.py"
    
    with open(coordinator_path, 'r') as f:
        content = f.read()
    
    # Check for counter variables
    if "_connection_issues" not in content or "_max_connection_issues" not in content:
        print("❌ Connection issues counter missing")
        return False
    
    # Check for counter logic
    if "self._connection_issues +=" not in content:
        print("❌ Counter increment logic missing")
        return False
    
    print("✅ Connection issues counter logic exists")
    return True

def test_error_handling_integration():
    """Test error handling integration in main flow."""
    coordinator_path = "custom_components/hue_cleaner/coordinator.py"
    
    with open(coordinator_path, 'r') as f:
        content = f.read()
    
    # Check for error handling in main update method
    if "_async_update_data" not in content:
        print("❌ Main update method missing")
        return False
    
    # Check for error handling calls in update method
    update_method = re.search(r'async def _async_update_data\(.*?\):(.*?)(?=async def|\Z)', content, re.DOTALL)
    if not update_method or "_handle_connection_error" not in update_method.group(1):
        print("❌ Error handling not integrated in main flow")
        return False
    
    print("✅ Error handling integrated in main flow")
    return True

def main():
    """Run all error handling tests."""
    print("🧪 Testing Hue Cleaner Error Handling Logic...\n")
    
    tests = [
        ("Error Handling Methods", test_error_handling_methods_exist),
        ("Error Detection Logic", test_error_detection_logic),
        ("Repair Flow", test_repair_flow_exists),
        ("Notification Creation", test_notification_creation),
        ("Repair Issue Creation", test_repair_issue_creation),
        ("Translation Keys", test_translation_keys),
        ("Connection Issues Counter", test_connection_issues_counter),
        ("Error Handling Integration", test_error_handling_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1
        print()
    
    print(f"🎯 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All error handling logic tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
