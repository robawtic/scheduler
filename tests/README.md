# Scheduler Application Test Suite

This directory contains tests for the Scheduler application, including unit tests, integration tests, and a manual testing guide.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for testing multiple components together
- `MANUAL_TESTING_GUIDE.md`: Guide for manual testing of the application

## Prerequisites

Before running the tests, make sure you have:

1. Python 3.8+ installed
2. All dependencies installed: `pip install -r requirements.txt`
3. A test database configured (SQLite is used by default for tests)

## Running the Tests

### Running All Tests

To run all tests, use the following command from the project root:

```bash
pytest tests/
```

### Running Unit Tests Only

```bash
pytest tests/unit/
```

### Running Integration Tests Only

```bash
pytest tests/integration/
```

### Running Specific Test Files

```bash
pytest tests/unit/test_user_endpoints.py
```

### Running Tests with Coverage

```bash
pytest --cov=. tests/
```

To generate an HTML coverage report:

```bash
pytest --cov=. --cov-report=html tests/
```

The report will be available in the `htmlcov` directory.

## Test Configuration

The tests use a separate configuration from the main application. The test configuration is defined in `conftest.py` and includes:

- A test database (SQLite in-memory by default)
- Test fixtures for common objects like the FastAPI test client, database session, and CSRF token
- Mock services for external dependencies

## Writing New Tests

When writing new tests, follow these guidelines:

1. **Unit Tests**: Test a single component in isolation. Mock any dependencies.
2. **Integration Tests**: Test how multiple components work together.
3. **Use Fixtures**: Use the provided fixtures for common objects.
4. **Clean Up**: Make sure tests clean up after themselves.
5. **Descriptive Names**: Use descriptive test names that explain what is being tested.

### Example Test

```python
def test_user_registration(client, csrf_token):
    """Test that a user can register with valid data."""
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == "testuser"
```

## Test Reports

To generate a test report, use the following command:

```bash
pytest --junitxml=test-results.xml tests/
```

This will generate a JUnit XML report that can be used by CI/CD systems.

## Continuous Integration

The tests are automatically run on every pull request and push to the main branch using GitHub Actions. The workflow is defined in `.github/workflows/tests.yml`.

## Manual Testing

For manual testing instructions, see the [Manual Testing Guide](MANUAL_TESTING_GUIDE.md).

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Make sure the test database is configured correctly.
2. **Import Errors**: Make sure you're running the tests from the project root.
3. **CSRF Token Errors**: The tests use a mock CSRF token. Make sure it's being passed correctly.

### Getting Help

If you encounter any issues with the tests, please:

1. Check the error message and traceback
2. Check the test logs
3. Consult the documentation
4. Ask for help from the development team

## Contributing

When contributing new features or bug fixes, please include tests that cover your changes. All pull requests should maintain or increase the test coverage.