# IOWarp Core

**High-performance distributed I/O and task execution runtime for scientific computing and HPC workloads.**

## Overview

IOWarp Core is a PyPI package that provides automated installation and build management for the complete IOWarp ecosystem. It orchestrates the compilation and installation of four core C++ components:

1. **Context Transport Primitives (HermesShm)** - High-performance shared memory library with IPC-safe containers and synchronization primitives
2. **Runtime (Chimaera)** - Distributed task execution runtime with microsecond-level latencies
3. **Context Transfer Engine (Hermes)** - Multi-tiered, heterogeneous-aware I/O buffering system
4. **Context Assimilation Engine** - Data ingestion and processing engine for heterogeneous storage systems

All components are built from source using CMake with minimalistic dependencies (no CUDA, ROCm, compression, or encryption by default).

## Features

- **Automated Build Process**: Clones, builds, and installs all components in the correct dependency order
- **CMake Integration**: Seamlessly integrates C++ CMake projects with Python packaging
- **Minimalistic Dependencies**: Built without optional features (CUDA, ROCm, MPI, ZMQ) for easier deployment
- **Cross-Platform**: Supports Linux, macOS, and Windows (where applicable)
- **Performance-Oriented**: All components optimized for HPC and scientific computing workloads

## Requirements

### System Requirements
- **CMake** ≥ 3.10
- **C++17** compatible compiler (GCC ≥9, Clang ≥10, MSVC ≥2019)
- **Git** (for cloning component repositories)
- **Python** ≥ 3.8

### Operating Systems
- Linux (Ubuntu 20.04+, CentOS 8+, or similar)
- macOS (10.15+)
- Windows (with Visual Studio 2019+ or MinGW)

## Installation

### From PyPI (when published)

```bash
pip install iowarp-core
```

### From Source

```bash
git clone https://github.com/iowarp/iowarp-core
cd iowarp-core
pip install .
```

### Development Installation

```bash
pip install -e .
```

## Build Process

When you install `iowarp-core`, the following happens automatically:

1. **Context Transport Primitives** is cloned from GitHub and built with:
   - CUDA support: OFF
   - ROCm support: OFF
   - MPI support: OFF
   - ZMQ support: OFF

2. **Runtime (Chimaera)** is cloned and built, linking against the installed Context Transport Primitives

3. **Context Transfer Engine (Hermes)** is cloned and built with dependencies on previous components

4. **Context Assimilation Engine** is cloned and built as the final component

All components are installed to your Python environment's prefix (e.g., `/usr/local` or virtual environment directory).

## Usage

After installation, the IOWarp components are available as system libraries and executables:

```python
import iowarp_core

# Get information about installed components
print(iowarp_core.get_component_info())

# Get version
print(iowarp_core.get_version())
```

The C++ libraries and headers are installed to standard system locations and can be used in your own projects:

```cmake
find_package(chimaera REQUIRED)
find_package(hermes REQUIRED)

target_link_libraries(your_app chimaera::core hermes::hermes)
```

## Component Details

### Context Transport Primitives (HermesShm)
- IPC-safe containers (vectors, lists, maps, ring queues)
- Memory management with custom allocators
- Threading and synchronization primitives
- **Repository**: https://github.com/iowarp/context-transport-primitives

### Runtime (Chimaera)
- Microsecond-level task latencies
- Up to 50 GB/s memory bandwidth with RAM backends
- Thousands of concurrent coroutine-based tasks
- Dynamically loadable modules (ChiMods)
- **Repository**: https://github.com/iowarp/runtime

### Context Transfer Engine (Hermes)
- Multi-tiered buffering across memory/storage hierarchies
- I/O pathway adapters for various backends
- HPC runtime integration
- **Repository**: https://github.com/iowarp/context-transfer-engine

### Context Assimilation Engine
- High-performance data ingestion
- Multiple format support (Parquet, CSV, binary)
- MPI-based parallel processing
- YAML-based job orchestration
- **Repository**: https://github.com/iowarp/context-assimilation-engine

## Troubleshooting

### Build Failures

If the build fails, check that you have:
- CMake 3.10 or newer: `cmake --version`
- A C++17 compiler: `g++ --version` or `clang++ --version`
- Git installed: `git --version`

### Missing Dependencies

On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install build-essential cmake git python3-dev
```

On CentOS/RHEL:
```bash
sudo yum groupinstall "Development Tools"
sudo yum install cmake git python3-devel
```

On macOS:
```bash
brew install cmake git
```

## Development

To contribute to this package:

```bash
git clone https://github.com/iowarp/iowarp-core
cd iowarp-core
pip install -e ".[dev]"
```

## License

MIT License - See LICENSE file for details.

Note: Individual IOWarp components may have different licenses (typically BSD-3-Clause). Please refer to each component's repository for specific licensing information.

## Links

- **GitHub Organization**: https://github.com/iowarp
- **Issue Tracker**: https://github.com/iowarp/iowarp-core/issues

## Credits

Developed by the Gnosis Research Center at Illinois Institute of Technology and the IOWarp community.
