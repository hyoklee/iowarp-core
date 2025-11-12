# IOWarp Core

**High-performance distributed I/O and task execution runtime for scientific computing and HPC workloads.**

## Overview

IOWarp Core is a PyPI package that provides automated installation and build management for the complete IOWarp ecosystem. It orchestrates the compilation and installation of four core C++ components:

1. **Context Transport Primitives** - High-performance shared memory library with IPC-safe containers and synchronization primitives
2. **Runtime** - Distributed task execution runtime with microsecond-level latencies
3. **Context Transfer Engine** - Multi-tiered, heterogeneous-aware I/O buffering system
4. **Context Assimilation Engine** - Data ingestion and processing engine for heterogeneous storage systems

All components are built from source using CMake with minimalistic dependencies (no CUDA, ROCm, compression, or encryption by default).

## Features

- **Automated Build Process**: Clones, builds, and installs all components in the correct dependency order
- **CMake Integration**: Seamlessly integrates C++ CMake projects with Python packaging
- **Minimalistic Dependencies**: Built without optional features (CUDA, ROCm, MPI, ZMQ) for easier deployment
- **Performance-Oriented**: All components optimized for HPC and scientific computing workloads

## Requirements

### System Requirements
- **CMake** ≥ 3.10
- **C++17** compatible compiler (GCC ≥9, Clang ≥10, MSVC ≥2019)
- **Git** (for cloning component repositories)
- **Python** ≥ 3.8

### Operating Systems
- Linux (Ubuntu 20.04+, CentOS 8+, or similar)

## Installation

### From PyPI

```bash
pip install iowarp-core
```

## License

BSD License - See LICENSE file for details.

Note: Individual IOWarp components may have different licenses (typically BSD-3-Clause).
Please refer to each component's repository for specific licensing information.

## Links

- **GitHub Organization**: https://github.com/iowarp
- **Issue Tracker**: https://github.com/iowarp/iowarp/issues

## Credits

Developed by the Gnosis Research Center at Illinois Institute of Technology and the IOWarp community.
