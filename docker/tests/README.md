# Test Suite Documentation

This directory contains comprehensive test suites for the Docker Browser Automation Environment.

## Test Files

### Comprehensive System Tests
- **`comprehensive_system_test_v3.py`** - Latest and most robust test suite with improved error handling
- **`comprehensive_system_test_v2.py`** - Previous version with 13 test cases
- **`comprehensive_system_test.py`** - Original comprehensive test suite

### API Testing
- **`test_api_endpoints.py`** - API endpoint validation tests
- **`test_typed_api.py`** - Type validation for API responses
- **`comprehensive_endpoint_verification.py`** - Detailed API endpoint verification

### Debugging and Verification
- **`debug_test.py`** - Debug utilities for troubleshooting
- **`check_endpoints.py`** - Quick endpoint availability checks
- **`run_tests.py`** - Test runner utility

### Legacy Tests
- **`comprehensive_test.py`** - Earlier test implementation

## Running Tests

### Recommended Test Suite
```bash
# Run the latest comprehensive test
python3 comprehensive_system_test_v3.py
```

### API-Specific Tests
```bash
# Test API endpoints
python3 test_api_endpoints.py

# Verify endpoint availability
python3 check_endpoints.py
```

### Debug Mode
```bash
# Run debug tests for troubleshooting
python3 debug_test.py
```

## Test Coverage

The comprehensive test suite covers:
- Container status and health
- Supervisor service management
- noVNC web interface
- Browser automation API (internal and external)
- File server functionality
- Process monitoring
- VNC processes
- Workspace setup

## Success Criteria

- **90%+ pass rate**: System fully functional
- **75%+ pass rate**: System mostly functional with minor issues
- **50%+ pass rate**: System has significant issues
- **<50% pass rate**: System has major problems

## Notes

Some test failures may be due to testing environment limitations rather than actual system problems. Always verify manually when automated tests show inconsistent results.
