# Browser API Testing Documentation

This document provides instructions for running tests with the modular Browser API structure.

## Test Structure

The tests have been migrated to the modular structure in:
- `browser_api/tests/test_browser_automation.py` - Main browser automation tests
- `browser_api/tests/test_dom_handler.py` - DOM handler specific tests

These files contain the following test functions:
1. `test_browser_api()` - Tests basic browser automation functionality
2. `test_browser_api_2()` - Tests chess page-specific functionality
3. `test_dom_handler()` - Tests DOM state extraction and manipulation

## Running Tests

### Option 1: Using run_tests.py

The `run_tests.py` script provides a convenient way to run the tests:

```bash
# Run the basic browser test
python run_tests.py --test1

# Run the chess page test
python run_tests.py --test2

# Run the DOM handler test
python run_tests.py --dom

# Run all tests
python run_tests.py --all
```

### Option 2: Using the adapter

For backward compatibility, you can run tests via the adapter:

```bash
# Run the basic browser test
python browser_api_adapter.py --test

# Run the chess page test
python browser_api_adapter.py --test2
```

### Option 3: Using the modular structure directly

You can also run tests directly from the modular structure:

```bash
# Run the basic browser test
python -m browser_api.main --test

# Run the chess page test
python -m browser_api.main --test2

# Run the DOM handler test
python -m browser_api.tests.test_dom_handler

# Run all tests
python -m browser_api.main --all
```

## Test Dependencies

The tests require the following:
- An active browser (Chromium)
- Internet connectivity for navigating to test pages
- Sufficient permissions for browser automation

## Troubleshooting

If tests fail with browser initialization errors:
1. Ensure no other browser automation instances are running
2. Check system resources (memory, CPU)
3. Verify internet connectivity

For other issues, check the error messages and browser logs for specific details.
