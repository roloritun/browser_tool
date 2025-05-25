# Browser Automation Tool

This project provides a browser automation sandbox using Playwright. It includes a modular browser API for programmatic browser control and a Docker environment for running browser automation tasks.

## Project Structure

- **browser_api/**: Modular implementation of browser automation functionality
  - **actions/**: Specific browser actions (navigation, interaction, etc.)
  - **core/**: Core functionality (browser automation, DOM handling)
  - **models/**: Data models for actions, DOM state, and results
  - **tests/**: Test functions and utilities
  - **utils/**: Utility functions for screenshots, PDFs, etc.

- **browser_api.py**: Backward compatibility layer for the old monolithic implementation
- **browser_api_adapter.py**: Adapter that bridges old code to the new modular structure
- **run_tests.py**: Script for running tests

## Docker Environment

The project includes Docker configuration for running the browser automation in a containerized environment:

- **Dockerfile**: Container configuration with browser dependencies
- **docker-compose.yml**: Multi-container setup
- **supervisord.conf**: Process management
- **startup.sh**: Container startup script

## Usage

### Running Tests

```bash
# Run basic browser test
python run_tests.py --test1

# Run chess page test
python run_tests.py --test2

# Run DOM handler test
python run_tests.py --dom

# Run all tests
python run_tests.py --all
```

### Using the API

The browser automation can be used as an API server:

```bash
# Start the API server
python -m browser_api.main
```

### Docker Deployment

```bash
# Build and start the Docker containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## Documentation

For more detailed documentation, see:

- [Browser API Documentation](browser_api/README.md)
- [Test Documentation](browser_api/tests/README.md)
