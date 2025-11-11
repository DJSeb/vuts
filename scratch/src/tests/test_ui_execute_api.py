#!/usr/bin/env python3
"""
Test suite for UI execute API endpoint
Tests the /api/execute endpoint that runs vuts commands
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.app import app


def test_execute_api_validation():
    """Test API validation for execute endpoint"""
    print("\n" + "=" * 60)
    print("TESTING: UI Execute API Validation")
    print("=" * 60)
    
    with app.test_client() as client:
        # Test missing command
        response = client.post('/api/execute',
                               json={},
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert not data['success']
        print("✓ Missing command properly rejected")
        
        # Test invalid command
        response = client.post('/api/execute',
                               json={'command': 'invalid'},
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid command' in data['error']
        print("✓ Invalid command properly rejected")
        
        # Test fetch without config
        response = client.post('/api/execute',
                               json={'command': 'fetch', 'args': {}},
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Config file is required' in data['error']
        print("✓ Fetch without config properly rejected")
        
        # Test market without symbols
        response = client.post('/api/execute',
                               json={'command': 'market', 'args': {}},
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'symbols are required' in data['error']
        print("✓ Market without symbols properly rejected")


def test_execute_api_command_building():
    """Test that commands are built correctly"""
    print("\n" + "=" * 60)
    print("TESTING: Command Building Logic")
    print("=" * 60)
    
    with app.test_client() as client:
        # Test fetch with non-existent config (should fail at validation)
        response = client.post('/api/execute',
                               json={
                                   'command': 'fetch',
                                   'args': {
                                       'config': 'nonexistent.json',
                                       'output_dir': 'output'
                                   }
                               },
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Config file not found' in data['error']
        print("✓ Non-existent config file properly rejected")
        
        # Test market with invalid symbols format
        response = client.post('/api/execute',
                               json={
                                   'command': 'market',
                                   'args': {
                                       'symbols': '   ',
                                       'days': 30,
                                       'output_dir': 'output/market_data'
                                   }
                               },
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No valid stock symbols' in data['error']
        print("✓ Empty symbols properly rejected")


def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("UI EXECUTE API TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("API Validation", test_execute_api_validation),
        ("Command Building", test_execute_api_command_building),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n✓ PASS: {test_name}")
        except AssertionError as e:
            failed += 1
            print(f"\n✗ FAIL: {test_name}")
            print(f"  Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n✗ ERROR: {test_name}")
            print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, _ in tests:
        status = "✓ PASS" if test_name in [t[0] for t in tests[:passed]] else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
