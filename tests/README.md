# NAF Solution Wizard Test Framework

This directory contains a comprehensive test framework for the NAF Solution Wizard, including data generation, API testing, upload validation, and complete end-to-end testing capabilities.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Test Framework Overview](#test-framework-overview)
- [Test Components](#test-components)
- [Running Tests](#running-tests)
- [Test Data Generation](#test-data-generation)
- [API Testing](#api-testing)
- [Upload Validation](#upload-validation)
- [Comprehensive Test Suite](#comprehensive-test-suite)
- [Test Results and Reports](#test-results-and-reports)
- [Directory Structure](#directory-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### One-Command Test Execution
```bash
# Run all tests (recommended for development)
uv run naf-test --quick

# Run complete test suite including code quality
uv run naf-test

# Run specific test components
uv run python test_lorem.py
uv run python test_upload_validation.py
uv run python tests/test_data_generator.py
```

### 🔗 Linking Commands

#### API Server Linking
```bash
# Link the API module for proper imports
cd "/Users/claudiadeluna/Indigo Wire Networks Dropbox/Claudia de Luna/scripts/python/2026/naf_framework_solution_wizard"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/api"

# Start API server with proper path
uv run naf-api

# Alternative: Run API server directly
cd api && uv run python -m main
```

#### Module Import Linking
```bash
# Set up Python path for all modules
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests with proper module linking
uv run python -m pytest tests/
uv run python test_lorem.py
uv run python test_upload_validation.py
```

#### Development Environment Setup
```bash
# Complete environment setup with linking
cd naf_framework_solution_wizard

# Install dependencies
uv sync

# Set up Python paths
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/api"

# Start API server (terminal 1)
uv run naf-api

# Run tests (terminal 2)
uv run naf-test --quick
```

#### 🔧 Advanced Linking Solutions

##### 1. Symlink Method (Recommended for Development)
```bash
# Create symlinks for proper module resolution
cd naf_framework_solution_wizard

# Link API main to root (optional)
ln -sf api/main.py api_main.py

# Update PYTHONPATH permanently
echo 'export PYTHONPATH="${PYTHONPATH}:'"$(pwd)"':$(pwd)/api"' >> ~/.zshrc
source ~/.zshrc
```

##### 2. Virtual Environment Activation
```bash
# Activate with proper paths
cd naf_framework_solution_wizard
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e .
uv pip install -e api/

# Set paths
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/api"
```

##### 3. Module Import Fix
```bash
# Fix import issues by adding __init__.py files
touch api/__init__.py
touch tests/__init__.py

# Update imports in test files
# Use relative imports: from ..api.main import app
```

#### 🐛 Linking Troubleshooting

##### Common Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'api'
export PYTHONPATH="${PYTHONPATH}:$(pwd)/api"

# Error: ModuleNotFoundError: No module named 'main'
cd api && python -m main

# Error: Cannot find module 'csat_utils'
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

##### MyPy Module Conflicts
```bash
# Fix duplicate main.py module error
uv run mypy . --exclude main.py

# Or exclude specific files
uv run mypy . --exclude "main.py" --exclude "api/main.py"
```

##### Development Server Issues
```bash
# If API server doesn't start:
cd api && uv run python main.py

# Check port conflicts
lsof -i :8001
kill -9 <PID>

# Start on different port
uv run naf-api --port 8002
```

### 📁 Main.py File Structure

**Important Note**: There are two `main.py` files in the project:

1. **Root `main.py`** - Simple "Hello World" entry point (can be removed)
2. **`api/main.py`** - Contains the actual FastAPI application

**Recommended Action**: Remove the root `main.py` to avoid module conflicts:
```bash
# Remove conflicting main.py (optional)
rm main.py

# The api/main.py is the actual FastAPI server
uv run naf-api  # Uses api/main.py
```

### Prerequisites
1. **API Server Running**: Start the FastAPI server
   ```bash
   uv run naf-api
   ```
2. **Dependencies Installed**: Ensure all dependencies are installed
   ```bash
   uv sync
   ```

## 📊 Test Framework Overview

The NAF Solution Wizard test framework provides comprehensive testing capabilities:

### 🎯 Test Categories

| Category | Purpose | Files | Status |
|----------|---------|-------|--------|
| **Data Generation** | Creates lorem ipsum test data | `test_data_generator.py` | ✅ Complete |
| **API Testing** | Tests REST API endpoints | `run_lorem_test.py` | ✅ Complete |
| **Upload Validation** | Validates file upload functionality | `upload_validator.py` | ✅ Complete |
| **Unit Tests** | Individual component testing | `test_*.py` | ✅ Complete |
| **Integration Tests** | End-to-end workflows | `test_api.py` | ✅ Complete |
| **Code Quality** | Formatting, linting, type checking | Various tools | ✅ Available |

### 🧪 Test Coverage

- **11 Wizard Sections**: All Solution Wizard sections validated
- **CRUD Operations**: Create, Read, Update, Delete, List solutions
- **Export Functionality**: JSON and Markdown export testing
- **File Upload**: Wizard-compatible JSON file generation and validation
- **Data Integrity**: Field validation and type checking
- **Error Handling**: Exception and edge case testing

## 🧩 Test Components

### 1. Data Generation (`test_data_generator.py`)

**Purpose**: Generates comprehensive lorem ipsum test data for all wizard fields.

**Features**:
- Generates test data for all 11 wizard sections
- Preserves standard pulldown/select options
- Uses wizard naming convention for file compatibility
- Creates realistic lorem ipsum content for text fields

**Usage**:
```bash
# Generate test data only
uv run python tests/test_data_generator.py

# Output: tests/naf_report_lorem_test_YYYYMMDD_HHMMSS.json
```

**Generated Data Structure**:
```json
{
  "initiative": {
    "title": "LOREM TEST",
    "description": "Lorem ipsum dolor sit amet...",
    "category": "Network Automation",
    "problem_statement": "Lorem ipsum problem statement...",
    "out_of_scope": "Lorem ipsum out of scope...",
    "expected_use": "Lorem ipsum expected use...",
    "error_conditions": "Lorem ipsum error conditions...",
    "assumptions": "Lorem ipsum assumptions...",
    "deployment_strategy": "Phased Rollout",
    "deployment_strategy_description": "Lorem ipsum deployment strategy...",
    "no_move_forward": "Lorem ipsum no move forward...",
    "no_move_forward_reasons": ["Lorem ipsum reason 1...", "Lorem ipsum reason 2..."]
  },
  "my_role": {
    "who": "Lorem ipsum role description...",
    "skills": "Lorem ipsum skills description...",
    "developer": "External vendor"
  },
  "stakeholders": {
    "choices": {
      "Technical Stakeholders": "Network Engineering Team",
      "Business Stakeholders": "IT Director",
      "User Stakeholders": "End Users"
    },
    "other": "Lorem ipsum additional stakeholders..."
  },
  // ... all 11 sections with comprehensive lorem ipsum data
}
```

### 2. API Testing (`run_lorem_test.py`)

**Purpose**: Tests all REST API endpoints with generated test data.

**Test Coverage**:
- ✅ Health Check (`/health`)
- ✅ Create Solution (`POST /api/v1/solutions`)
- ✅ Get Solution (`GET /api/v1/solutions/{id}`)
- ✅ Update Solution (`PUT /api/v1/solutions/{id}`)
- ✅ Delete Solution (`DELETE /api/v1/solutions/{id}`)
- ✅ List Solutions (`GET /api/v1/solutions`)
- ✅ Export Solutions (`POST /api/v1/solutions/{id}/export`)

**Usage**:
```bash
# Complete API test suite
uv run python test_lorem.py

# Specific API tests
uv run python test_lorem.py --test create
uv run python test_lorem.py --test read
uv run python test_lorem.py --test update
uv run python test_lorem.py --test delete
uv run python test_lorem.py --test export
uv run python test_lorem.py --test list
```

### 3. Upload Validation (`upload_validator.py`)

**Purpose**: Validates that JSON files can be uploaded to the Solution Wizard and all fields are properly loaded.

**Validation Features**:
- ✅ File upload via API
- ✅ Field-by-field validation
- ✅ Data type preservation
- ✅ Export functionality testing
- ✅ Manual upload compatibility

**Usage**:
```bash
# Complete upload validation
uv run python test_upload_validation.py

# Generate test file only (for manual upload)
uv run python test_upload_validation.py --generate-only

# Custom API URL
uv run python test_upload_validation.py --api-url http://localhost:8000
```

### 4. Unit Tests (`test_*.py`)

**Purpose**: Individual component testing.

**Available Tests**:
- `test_data_generator.py` - Data generation functionality
- `test_wizard_utils.py` - Utility functions
- `test_csat_utils.py` - CSAT utilities (skipped - missing dependencies)

**Usage**:
```bash
# Run all unit tests
uv run python -m pytest tests/test_*.py

# Run specific unit test
uv run python tests/test_data_generator.py
```

### 5. Integration Tests (`test_api.py`)

**Purpose**: API integration and connectivity testing.

**Features**:
- ✅ API endpoint connectivity
- ✅ Request/response validation
- ✅ Error handling testing

**Usage**:
```bash
# Run integration tests
uv run python api/test_api.py
```

## 🎮 Running Tests

### Primary Commands

| Command | Purpose | Scope |
|---------|---------|-------|
| `uv run naf-test` | **Complete test suite** | All tests including code quality |
| `uv run naf-test --quick` | **Quick tests** | Core functionality only |
| `uv run python test_lorem.py` | **API tests** | REST API functionality |
| `uv run python test_upload_validation.py` | **Upload validation** | File upload testing |
| `uv run python tests/test_data_generator.py` | **Data generation** | Test data creation |

### Test Execution Options

#### 1. Quick Development Tests
```bash
# Fast feedback during development
uv run naf-test --quick
```
**Includes**: Unit tests, data generation, API tests, upload validation
**Duration**: ~1-2 seconds
**Purpose**: Rapid development feedback

#### 2. Full Test Suite
```bash
# Complete testing including code quality
uv run naf-test
```
**Includes**: All quick tests + integration tests + code quality checks
**Duration**: ~20-30 seconds
**Purpose**: CI/CD pipeline, pre-commit checks

#### 3. Custom Test Execution
```bash
# Skip code quality checks
uv run naf-test --skip-quality

# Skip integration tests
uv run naf-test --skip-integration

# Custom API URL
uv run naf-test --api-url http://localhost:8080

# Direct Python execution
uv run python run_all_tests.py --quick --api-url http://localhost:8001
```

### Test Requirements

#### Prerequisites
1. **API Server**: FastAPI server must be running
   ```bash
   uv run naf-api
   ```
2. **Dependencies**: All project dependencies installed
   ```bash
   uv sync
   ```
3. **Ports**: API server accessible on configured port (default: 8001)

#### Environment Setup
```bash
# Clone and setup
cd naf_framework_solution_wizard
uv sync

# Start API server (in separate terminal)
uv run naf-api

# Run tests
uv run naf-test
```

## 📝 Test Data Generation

### Automatic Generation

The test framework automatically generates test data using the wizard naming convention:

```bash
# Generate test data
uv run python tests/test_data_generator.py

# Output file: tests/naf_report_lorem_test_20251224_083000.json
```

### Manual Upload Testing

Generated files are compatible with manual upload to the Solution Wizard:

1. **Generate Test File**:
   ```bash
   uv run python test_upload_validation.py --generate-only
   ```

2. **Upload to Wizard**:
   - Open Solution Wizard web interface
   - Use "Upload naf_report_*.json" option
   - Select generated test file

3. **Validation**: All fields should populate with lorem ipsum content

### Data Structure

**Wizard-Compliant Format**:
```json
{
  "initiative": {
    "title": "LOREM TEST",
    "description": "Comprehensive lorem ipsum description...",
    "category": "Network Automation",
    "problem_statement": "Lorem ipsum problem statement...",
    "out_of_scope": "Lorem ipsum out of scope...",
    "expected_use": "Lorem ipsum expected use...",
    "error_conditions": "Lorem ipsum error conditions...",
    "assumptions": "Lorem ipsum assumptions...",
    "deployment_strategy": "Phased Rollout",
    "deployment_strategy_description": "Lorem ipsum deployment strategy...",
    "no_move_forward": "Lorem ipsum no move forward...",
    "no_move_forward_reasons": ["Lorem ipsum reason 1...", "Lorem ipsum reason 2..."]
  },
  "my_role": {
    "who": "Lorem ipsum role description...",
    "skills": "Lorem ipsum skills description...",
    "developer": "External vendor"
  },
  "stakeholders": {
    "choices": {
      "Technical Stakeholders": "Network Engineering Team",
      "Business Stakeholders": "IT Director",
      "User Stakeholders": "End Users"
    },
    "other": "Lorem ipsum additional stakeholders..."
  },
  // ... all 11 sections with comprehensive lorem ipsum data
}
```

## 🌐 API Testing

### Test Coverage

The API testing framework validates all REST API endpoints:

| Endpoint | Method | Test Coverage | Status |
|----------|--------|---------------|--------|
| `/health` | GET | Health check | ✅ |
| `/api/v1/solutions` | POST | Create solution | ✅ |
| `/api/v1/solutions/{id}` | GET | Get solution | ✅ |
| `/api/v1/solutions/{id}` | PUT | Update solution | ✅ |
| `/api/v1/solutions/{id}` | DELETE | Delete solution | ✅ |
| `/api/v1/solutions` | GET | List solutions | ✅ |
| `/api/v1/solutions/{id}/export` | POST | Export solution | ✅ |

### API Test Execution

```bash
# Complete API test suite
uv run python test_lorem.py

# Specific API tests
uv run python test_lorem.py --test create
uv run python test_lorem.py --test read
uv run python test_lorem.py --test update
uv run python test_lorem.py --test delete
uv run python test_lorem.py --test export
uv run python test_lorem.py --test list
```

### API Test Results

```
🧪 Running NAF Solution Wizard Lorem Test
✅ Health Check: API is healthy
✅ Create Solution: Solution ID: 12345678-1234-1234-1234-123456789abc
✅ Get Solution: Retrieved successfully
✅ Update Solution: Updated successfully
✅ Export Solution: JSON and Markdown exported
✅ List Solutions: Found 1 solutions
✅ Delete Solution: Deleted successfully
📊 Test Results: 7/7 passed
🎉 All API tests passed!
```

## 📤 Upload Validation

### Validation Process

The upload validation framework ensures complete data integrity:

1. **File Generation**: Creates wizard-compatible JSON files
2. **API Upload**: Uploads file via REST API
3. **Field Validation**: Validates each field and section
4. **Export Testing**: Tests JSON and Markdown export
5. **Manual Upload**: Validates manual upload compatibility

### Upload Validation Execution

```bash
# Complete validation
uv run python test_upload_validation.py

# Generate test file for manual upload
uv run python test_upload_validation.py --generate-only

# Custom API configuration
uv run python test_upload_validation.py --api-url http://localhost:8080
```

### Validation Results

```
🧪 Starting NAF Solution Wizard Upload Validation
✅ Generate Test File: Created: naf_report_lorem_test_20251224_083000.json
✅ API Upload: Solution ID: 87654321-4321-4321-4321-210987654321
✅ Title Validation: Title correctly set to LOREM TEST
✅ Initiative Section: All fields validated
✅ My_Role Section: All fields validated
✅ Stakeholders Section: All fields validated
✅ Presentation Section: All fields validated
✅ Intent Section: All fields validated
✅ Observability Section: All fields validated
✅ Orchestration Section: All fields validated
✅ Collector Section: All fields validated
✅ Executor Section: All fields validated
✅ Dependencies Section: All fields validated
✅ Timeline Section: All fields validated
✅ Overall Validation: All sections validated successfully
✅ Export Validation: All sections present in export
✅ Markdown Export: Export contains test data
📊 Validation Results: 17/17 passed
🎉 All upload validations passed!
```

## 🔧 Comprehensive Test Suite

### Complete Test Execution

The comprehensive test suite runs all available tests:

```bash
# Run all tests
uv run naf-test

# Equivalent command
uv run python run_all_tests.py
```

### Test Suite Components

| Component | Purpose | Duration | Status |
|-----------|---------|----------|--------|
| Unit Tests | Individual component testing | ~0.5s | ✅ |
| Data Generation | Test data creation | ~0.5s | ✅ |
| API Tests | REST API functionality | ~1.0s | ✅ |
| Upload Validation | File upload testing | ~2.0s | ✅ |
| Integration Tests | End-to-end workflows | ~1.0s | ✅ |
| Code Quality | Formatting, linting, typing | ~15.0s | ⚠️ |

### Quick Test Mode

For rapid development feedback:

```bash
# Quick tests only (skip code quality and integration)
uv run naf-test --quick

# Duration: ~4 seconds
# Coverage: Core functionality only
```

### Custom Test Execution

```bash
# Skip code quality checks
uv run naf-test --skip-quality

# Skip integration tests
uv run naf-test --skip-integration

# Both options (equivalent to --quick)
uv run naf-test --skip-quality --skip-integration

# Custom API URL
uv run naf-test --api-url http://localhost:8080
```

## 📊 Test Results and Reports

### Result Files

Test results are automatically saved to `tests/results/`:

```
tests/results/
├── comprehensive_test_results_COMPREHENSIVE_20251224_083000.json
├── upload_validation_results_UPLOAD_VALIDATION_20251224_083000.json
├── test_results_LOREM_TEST_20251224_083000.json
└── ...
```

### Result Format

**Comprehensive Test Results**:
```json
{
  "test_run": "COMPREHENSIVE_20251224_083000",
  "start_time": "2025-12-24T08:30:00.000000",
  "end_time": "2025-12-24T08:30:20.000000",
  "api_url": "http://localhost:8001",
  "total_duration": 20.5,
  "test_suites": [
    {
      "name": "Unit Test: test_data_generator.py",
      "success": true,
      "duration_seconds": 0.5,
      "output": "✅ Test data saved to: tests/naf_report_lorem_test_20251224_083000.json",
      "error": "",
      "timestamp": "2025-12-24T08:30:01.000000"
    },
    // ... more test results
  ],
  "summary": {
    "total_tests": 9,
    "passed": 6,
    "failed": 3,
    "success_rate": 66.7
  }
}
```

### Test Summary Output

```
============================================================
📊 COMPREHENSIVE TEST RESULTS
============================================================
🧪 Total Tests: 9
✅ Passed: 6
❌ Failed: 3
📈 Success Rate: 66.7%
⏱️  Total Duration: 20.5 seconds

❌ Failed Tests:
   • Code Quality: Black Formatting: would reformat 16 files
   • Code Quality: Ruff Linting: linting issues found
   • Code Quality: MyPy Type Checking: type errors found

============================================================
⚠️  3 test(s) failed.

💾 Detailed results saved to: tests/results/comprehensive_test_results_COMPREHENSIVE_20251224_083000.json
```

## 📁 Directory Structure

```
tests/
├── README.md                           # This file
├── __init__.py                         # Package initialization
├── conftest.py                         # Pytest configuration
├── test_data_generator.py              # Data generation tests
├── run_lorem_test.py                   # API test runner
├── upload_validator.py                 # Upload validation tests
├── test_csat_utils.py                  # CSAT utilities tests
├── test_wizard_utils.py                # Wizard utilities tests
├── results/                            # Test results directory
│   ├── comprehensive_test_results_*.json
│   ├── upload_validation_results_*.json
│   └── test_results_*.json
├── generated/                          # Generated test data
│   └── naf_report_lorem_test_*.json
├── exports/                            # Export test outputs
│   └── lorem_export_*.json
│   └── lorem_export_*.md
└── ../run_all_tests.py                 # Comprehensive test runner
├── ../test_lorem.py                    # Quick API test runner
└── ../test_upload_validation.py        # Quick upload validation runner
```

## ⚙️ Configuration

### Default Configuration

```python
# Default API URL
API_URL = "http://localhost:8001"

# Test timeout
TIMEOUT = 300  # 5 minutes

# Test data title
TEST_TITLE = "LOREM TEST"

# File naming convention
FILENAME_PATTERN = "naf_report_{title}_{timestamp}.json"
```

### Custom Configuration

**Environment Variables**:
```bash
export NAF_API_URL="http://localhost:8080"
export NAF_TEST_TIMEOUT="600"
export NAF_TEST_TITLE="CUSTOM_TEST"
```

**Command Line Options**:
```bash
uv run naf-test --api-url http://localhost:8080
uv run python test_upload_validation.py --api-url http://localhost:8080
uv run python run_all_tests.py --quick --api-url http://localhost:8080
```

### Test Data Configuration

**Custom Test Data**:
```python
# In test_data_generator.py
generator = LoremTestDataGenerator(
    title="CUSTOM_TEST",
    sentence_count=5,
    word_count=10
)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Connection Failed
```
❌ API health check failed: Connection refused
```
**Solution**: Start the API server
```bash
uv run naf-api
```

#### 2. Missing Dependencies
```
ModuleNotFoundError: No module named 'lorem-text'
```
**Solution**: Install dependencies
```bash
uv sync
```

#### 3. Port Conflicts
```
❌ API returned status 404
```
**Solution**: Check API server port or use custom URL
```bash
uv run naf-api --port 8001
uv run naf-test --api-url http://localhost:8001
```

#### 4. Code Quality Failures
```
❌ Code Quality: Black Formatting: would reformat 16 files
```
**Solution**: Format code (optional for development)
```bash
uv run black .
uv run ruff check --fix .
uv run mypy .
```

#### 5. Test File Permissions
```
PermissionError: [Errno 13] Permission denied: 'tests/results/'
```
**Solution**: Check directory permissions
```bash
chmod 755 tests/results/
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Run with debug output
uv run python run_all_tests.py --quick

# Check API health manually
curl http://localhost:8001/health

# Test data generation manually
uv run python tests/test_data_generator.py
```

### Log Files

Test logs are saved in result files:
```bash
# View latest test results
ls -la tests/results/ | tail -1
cat tests/results/comprehensive_test_results_*.json
```

### Performance Issues

**Slow Test Execution**:
- Use `--quick` mode for development
- Skip code quality checks with `--skip-quality`
- Check API server performance

**Memory Issues**:
- Reduce test data size
- Run tests individually
- Check system resources

## 📞 Support

### Getting Help

1. **Check this README** for comprehensive documentation
2. **Review test results** in `tests/results/` directory
3. **Check API server** is running and accessible
4. **Verify dependencies** are installed

### Test Framework Maintenance

**Adding New Tests**:
1. Create test file in `tests/` directory with `test_*.py` prefix
2. Add to comprehensive test runner in `run_all_tests.py`
3. Update documentation in this README

**Updating Test Data**:
1. Modify `test_data_generator.py`
2. Test with `uv run python tests/test_data_generator.py`
3. Update validation logic in `upload_validator.py`

**Code Quality Standards**:
```bash
# Format code
uv run black .

# Check linting
uv run ruff check .

# Type checking
uv run mypy .
```

## 🚀 Advanced Usage Examples

### Custom Test Scenarios

#### 1. Performance Testing
```bash
# Run multiple test iterations for performance analysis
for i in {1..10}; do
    echo "Running test iteration $i/10"
    uv run naf-test --quick
done

# Measure execution time
time uv run naf-test --quick
```

#### 2. Parallel Test Execution
```bash
# Run data generation and API tests in parallel
uv run python tests/test_data_generator.py &
uv run python test_lorem.py &
wait

# Run upload validation after data is ready
uv run python test_upload_validation.py
```

#### 3. Custom Test Data Generation
```python
# Create custom test data with specific parameters
from tests.test_data_generator import LoremTestDataGenerator

generator = LoremTestDataGenerator(
    title="PERFORMANCE_TEST",
    sentence_count=3,  # Shorter sentences for faster tests
    word_count=5       # Fewer words for reduced memory
)

# Generate and save
data = generator.generate_complete_test_data()
generator.save_test_data(data, "custom_performance_test.json")
```

### CI/CD Integration Examples

#### GitHub Actions
```yaml
name: NAF Solution Wizard Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run naf-api &
      - run: sleep 10
      - run: uv run naf-test --quick
      - run: uv run naf-test  # Full suite for main branch
      if: github.ref == 'refs/heads/main'
```

#### Docker Testing
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv
RUN uv sync
EXPOSE 8001
CMD ["uv", "run", "naf-test", "--quick"]
```

### Test Data Analysis

#### Analyzing Generated Test Data
```python
import json
from pathlib import Path

def analyze_test_data(file_path):
    """Analyze generated test data for completeness"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Total sections: {len(data)}")
    for section, content in data.items():
        if isinstance(content, dict):
            print(f"  {section}: {len(content)} fields")
        elif isinstance(content, list):
            print(f"  {section}: {len(content)} items")
        else:
            print(f"  {section}: {type(content).__name__}")

# Usage
analyze_test_data("tests/naf_report_lorem_test_20251224_083000.json")
```

#### Validation Report Generation
```python
def generate_validation_report(results_file):
    """Generate human-readable validation report"""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    print(f"Test Run: {results['test_run']}")
    print(f"Duration: {results['total_duration']:.2f} seconds")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    
    for test in results['test_suites']:
        status = "✅" if test['success'] else "❌"
        print(f"{status} {test['name']} ({test['duration_seconds']:.2f}s)")

# Usage
generate_validation_report("tests/results/comprehensive_test_results_*.json")
```

### Environment-Specific Testing

#### Development Environment
```bash
# Development configuration
export NAF_API_URL="http://localhost:8001"
export NAF_TEST_TITLE="DEV_TEST"
export NAF_TEST_TIMEOUT="60"

uv run naf-test --quick --skip-quality
```

#### Staging Environment
```bash
# Staging configuration
export NAF_API_URL="https://staging-api.naf-solution.com"
export NAF_TEST_TITLE="STAGING_TEST"
export NAF_TEST_TIMEOUT="300"

uv run naf-test --api-url $NAF_API_URL
```

#### Production Environment (Read-only Tests)
```bash
# Production configuration - read-only tests only
export NAF_API_URL="https://api.naf-solution.com"

# Test health and read operations only
curl $NAF_API_URL/health
uv run python test_lorem.py --test read
```

### Debugging and Troubleshooting

#### Advanced Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug output to test execution
def debug_test_execution():
    print("=== DEBUG: Test Environment ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Environment variables: {dict(os.environ)}")
    
    # Test API connectivity
    import requests
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"API Health: {response.json()}")
    except Exception as e:
        print(f"API Error: {e}")

debug_test_execution()
```

#### Memory Profiling
```bash
# Profile memory usage during tests
uv run python -m memory_profiler test_lorem.py

# Check for memory leaks
for i in {1..5}; do
    uv run naf-test --quick
    echo "Memory usage after iteration $i:"
    ps aux | grep python | head -5
done
```

#### Network Debugging
```bash
# Monitor API calls during tests
tcpdump -i lo port 8001 -w api_calls.pcap &
UV_RUN_PID=$!
uv run naf-test --quick
kill $UV_RUN_PID

# Analyze network traffic
tcpdump -r api_calls.pcap -A
```

### Test Data Management

#### Automated Cleanup
```bash
#!/bin/bash
# cleanup_tests.sh - Clean up old test files

# Remove test results older than 7 days
find tests/results/ -name "*.json" -mtime +7 -delete

# Remove generated data older than 3 days
find tests/generated/ -name "*.json" -mtime +3 -delete

# Remove export files older than 1 day
find tests/exports/ -name "*" -mtime +1 -delete

echo "Cleanup completed"
```

#### Test Data Backup
```bash
#!/bin/bash
# backup_tests.sh - Backup important test results

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy latest test results
cp tests/results/*.json "$BACKUP_DIR/" 2>/dev/null || true

# Copy generated test data
cp tests/generated/*.json "$BACKUP_DIR/" 2>/dev/null || true

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup created: $BACKUP_DIR.tar.gz"
```

### Custom Test Extensions

#### Adding New Test Types
```python
# tests/custom_test.py
import unittest
from tests.test_data_generator import LoremTestDataGenerator

class CustomFeatureTest(unittest.TestCase):
    """Custom test for new features"""
    
    def setUp(self):
        self.generator = LoremTestDataGenerator()
        self.test_data = self.generator.generate_complete_test_data()
    
    def test_custom_functionality(self):
        """Test new custom functionality"""
        # Add your custom test logic here
        self.assertIn("initiative", self.test_data)
        self.assertEqual(self.test_data["initiative"]["title"], "LOREM TEST")
    
    def test_performance_requirements(self):
        """Test performance requirements"""
        import time
        start_time = time.time()
        
        # Perform operation
        result = perform_custom_operation(self.test_data)
        
        duration = time.time() - start_time
        self.assertLess(duration, 5.0, "Operation should complete within 5 seconds")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
```

#### Integration with External Tools
```python
# tests/integration_test.py
import subprocess
import json

def test_external_tool_integration():
    """Test integration with external tools"""
    
    # Generate test data
    generator = LoremTestDataGenerator()
    test_data = generator.generate_complete_test_data()
    
    # Save to file for external tool
    with open("external_input.json", "w") as f:
        json.dump(test_data, f)
    
    # Run external tool
    result = subprocess.run([
        "external_tool", 
        "--input", "external_input.json",
        "--output", "external_output.json"
    ], capture_output=True, text=True)
    
    # Validate results
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    
    # Clean up
    import os
    os.remove("external_input.json")
    os.remove("external_output.json")
```

## 📊 Test Metrics and Analytics

#### Performance Metrics Collection
```python
# tests/metrics_collector.py
import time
import psutil
import json
from datetime import datetime

class TestMetricsCollector:
    """Collect and analyze test performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "memory_usage": [],
            "cpu_usage": [],
            "test_results": []
        }
    
    def start_collection(self):
        """Start metrics collection"""
        self.metrics["start_time"] = datetime.now().isoformat()
    
    def record_metric(self, test_name, duration, success):
        """Record individual test metric"""
        self.metrics["test_results"].append({
            "test": test_name,
            "duration": duration,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
        self.metrics["cpu_usage"].append(psutil.cpu_percent())
    
    def generate_report(self, output_file):
        """Generate metrics report"""
        self.metrics["end_time"] = datetime.now().isoformat()
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Metrics report saved to: {output_file}")

# Usage in tests
collector = TestMetricsCollector()
collector.start_collection()
# ... run tests ...
collector.generate_report("tests/metrics/test_metrics.json")
```

---

## 🎉 Summary

The NAF Solution Wizard test framework provides comprehensive testing capabilities:

- ✅ **Complete Coverage**: All wizard sections and API endpoints
- ✅ **Easy Execution**: One-command test running
- ✅ **Detailed Reporting**: Comprehensive test results and logs
- ✅ **Flexible Configuration**: Customizable for different environments
- ✅ **Manual Upload Support**: Wizard-compatible test file generation
- ✅ **Code Quality**: Integrated formatting, linting, and type checking
- ✅ **Advanced Features**: Performance testing, CI/CD integration, debugging tools
- ✅ **Extensible**: Easy to add new tests and custom functionality

**Run all tests with a single command:**
```bash
uv run naf-test --quick
```

For detailed testing including code quality:
```bash
uv run naf-test
```

**For advanced usage and customization, see the Advanced Usage Examples section above.**

Happy testing! 🧪
