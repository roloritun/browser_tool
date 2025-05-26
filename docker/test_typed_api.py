#!/usr/bin/env python3
"""
Test script to verify the typed API models work correctly.
This script tests the Pydantic models and endpoint type checking.
"""
import sys
import asyncio
from pydantic import ValidationError

# Add the browser_api to the path
sys.path.insert(0, '/Users/rahmanoloritun/code_projects/scrtach/brower_tool/docker')

from browser_api.models.action_models import (
    GoToUrlAction,
    SearchGoogleAction,
    ClickElementAction,
    ClickCoordinatesAction,
    InputTextAction,
    SendKeysAction,
    SwitchTabAction,
    OpenTabAction,
    CloseTabAction,
    ScrollAction,
    NoParamsAction,
    DragDropAction,
    SwitchToFrameAction,
    SetNetworkConditionsAction,
    ScrollToTextAction,
    SetCookieAction,
    WaitAction,
    ExtractContentAction,
    PDFOptionsAction,
    GetDropdownOptionsAction,
    SelectDropdownOptionAction
)

def test_action_models():
    """Test that all action models can be created and validated correctly"""
    print("🧪 Testing Action Models...")
    
    tests = [
        ("GoToUrlAction", lambda: GoToUrlAction(url="https://example.com")),
        ("SearchGoogleAction", lambda: SearchGoogleAction(query="test search")),
        ("ClickElementAction", lambda: ClickElementAction(index=0)),
        ("ClickCoordinatesAction", lambda: ClickCoordinatesAction(x=100, y=200)),
        ("InputTextAction", lambda: InputTextAction(index=0, text="hello world")),
        ("SendKeysAction", lambda: SendKeysAction(keys="Enter")),
        ("SwitchTabAction", lambda: SwitchTabAction(page_id=1)),
        ("OpenTabAction", lambda: OpenTabAction(url="https://example.com")),
        ("CloseTabAction", lambda: CloseTabAction(page_id=1)),
        ("ScrollAction", lambda: ScrollAction(amount=300)),
        ("ScrollAction (no amount)", lambda: ScrollAction()),
        ("NoParamsAction", lambda: NoParamsAction()),
        ("DragDropAction", lambda: DragDropAction(coord_source_x=10, coord_source_y=20, coord_target_x=30, coord_target_y=40)),
        ("SwitchToFrameAction", lambda: SwitchToFrameAction(frame="frame1")),
        ("SetNetworkConditionsAction", lambda: SetNetworkConditionsAction(offline=True, latency=100)),
        ("ScrollToTextAction", lambda: ScrollToTextAction(text="search text")),
        ("SetCookieAction", lambda: SetCookieAction(name="test", value="value")),
        ("WaitAction", lambda: WaitAction()),
        ("ExtractContentAction", lambda: ExtractContentAction(goal="extract links")),
        ("PDFOptionsAction", lambda: PDFOptionsAction(format="Letter")),
        ("GetDropdownOptionsAction", lambda: GetDropdownOptionsAction(index=0)),
        ("SelectDropdownOptionAction", lambda: SelectDropdownOptionAction(index=0, option_text="Option 1")),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            action = test_func()
            # Test that it can be converted to dict (needed for API)
            action_dict = action.dict()
            print(f"✅ {test_name}: {action_dict}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return failed == 0

def test_validation_errors():
    """Test that validation works correctly for invalid inputs"""
    print("\n🔍 Testing Validation Errors...")
    
    validation_tests = [
        ("GoToUrlAction missing url", lambda: GoToUrlAction()),
        ("ClickElementAction missing index", lambda: ClickElementAction()),
        ("SetCookieAction missing name", lambda: SetCookieAction(value="test")),
        ("SwitchTabAction invalid page_id", lambda: SwitchTabAction(page_id="invalid")),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in validation_tests:
        try:
            action = test_func()
            print(f"❌ {test_name}: Should have failed but didn't - {action}")
            failed += 1
        except ValidationError as e:
            print(f"✅ {test_name}: Correctly caught validation error")
            passed += 1
        except TypeError as e:
            print(f"✅ {test_name}: Correctly caught type error")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
            failed += 1
    
    print(f"\n📊 Validation Test Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all tests"""
    print("🚀 Starting API Model Tests...\n")
    
    success1 = test_action_models()
    success2 = test_validation_errors()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The typed API models are working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
