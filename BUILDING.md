# Building and Publishing Guide

This document describes how to build, test, and publish the `iowarp-core` package.

## Prerequisites

Ensure you have the following installed:
- Python 3.8 or newer
- CMake 3.10 or newer
- C++17 compatible compiler
- Git
- pip and setuptools

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/iowarp/iowarp-core
cd iowarp-core
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install the package in editable mode:
```bash
pip install -e .
```

This will clone and build all four IOWarp components. **Note**: The build process can take 10-30 minutes depending on your system.

## Testing the Package Structure

Before building, you can test just the Python package structure (without building C++ components):

```bash
python test_package.py
```

This validates that the Python module structure is correct.

## Building the Distribution

### Build Source Distribution and Wheel

```bash
python -m build
```

This creates:
- `dist/iowarp-core-0.1.0.tar.gz` (source distribution)
- `dist/iowarp_core-0.1.0-*.whl` (wheel)

### Build Source Distribution Only

```bash
python setup.py sdist
```

## Testing the Build

1. Create a fresh virtual environment:
```bash
python3 -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
```

2. Install from the built distribution:
```bash
pip install dist/iowarp-core-0.1.0.tar.gz
```

3. Test the installation:
```bash
python -c "import iowarp_core; print(iowarp_core.get_version())"
```

## Publishing to PyPI

### Test PyPI (Recommended First)

1. Create an account on [TestPyPI](https://test.pypi.org/)

2. Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

3. Test installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ iowarp-core
```

### Production PyPI

1. Create an account on [PyPI](https://pypi.org/)

2. Upload to PyPI:
```bash
python -m twine upload dist/*
```

3. Test installation:
```bash
pip install iowarp-core
```

## Build Troubleshooting

### CMake Not Found
```bash
pip install cmake
```

### Git Not Found
Install git from your system package manager or https://git-scm.com/

### Compiler Errors

Make sure you have a C++17 compatible compiler:
- **Linux**: `sudo apt-get install build-essential` (Ubuntu/Debian)
- **macOS**: `xcode-select --install`
- **Windows**: Install Visual Studio 2019 or newer with C++ support

### Build Takes Too Long

The build process compiles four C++ projects. To speed up:
- Use parallel builds: `pip install . --global-option="build_ext" --global-option="-j8"`
- Or set in setup: Edit `setup.py` and adjust the parallel count

### Memory Issues During Build

If you run out of memory during compilation:
- Reduce parallel jobs: Edit `setup.py` and lower the CPU count
- Close other applications
- Consider building on a machine with more RAM (recommended: 8GB+)

## Package Structure

```
iowarp-core/
├── iowarp_core/           # Python package
│   └── __init__.py        # Package initialization
├── setup.py               # Build script with CMake integration
├── pyproject.toml         # Package metadata
├── README.md              # User documentation
├── BUILDING.md            # This file
├── LICENSE                # MIT License
├── MANIFEST.in            # Package files to include
├── requirements.txt       # Runtime requirements
├── requirements-dev.txt   # Development requirements
├── test_package.py        # Package structure tests
└── .gitignore             # Git ignore patterns
```

## Version Updates

To release a new version:

1. Update version in `pyproject.toml`:
```toml
version = "0.2.0"
```

2. Update version in `iowarp_core/__init__.py`:
```python
__version__ = "0.2.0"
```

3. Build and publish as described above.

## Continuous Integration

Consider setting up GitHub Actions for:
- Automated testing on multiple platforms
- Automated builds
- Automated PyPI publishing on release tags

Example workflow file (`.github/workflows/publish.yml`):
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Support

For issues or questions:
- Open an issue: https://github.com/iowarp/iowarp-core/issues
- Check component repos for component-specific issues
