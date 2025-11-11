#!/usr/bin/env python3
"""
Setup script for iowarp-core package.
Builds and installs C++ components using CMake in the correct order.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """Extension class for CMake-based C++ projects."""

    def __init__(self, name, sourcedir="", repo_url="", **kwargs):
        super().__init__(name, sources=[], **kwargs)
        self.sourcedir = os.path.abspath(sourcedir)
        self.repo_url = repo_url


class CMakeBuild(build_ext):
    """Custom build command that builds CMake projects in order."""

    # Define the components to build in order
    COMPONENTS = [
        {
            "name": "context-transport-primitives",
            "repo": "https://github.com/iowarp/context-transport-primitives",
            "cmake_args": [
                "-DHSHM_ENABLE_CUDA=OFF",
                "-DHSHM_ENABLE_ROCM=OFF",
                "-DHSHM_ENABLE_MPI=OFF",
                "-DHSHM_ENABLE_ZMQ=OFF",
            ]
        },
        {
            "name": "runtime",
            "repo": "https://github.com/iowarp/runtime",
            "cmake_args": []
        },
        {
            "name": "context-transfer-engine",
            "repo": "https://github.com/iowarp/context-transfer-engine",
            "cmake_args": []
        },
        {
            "name": "context-assimilation-engine",
            "repo": "https://github.com/iowarp/context-assimilation-engine",
            "cmake_args": []
        },
    ]

    def run(self):
        """Build all CMake components in order."""
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build iowarp-core. "
                "Install with: pip install cmake"
            )

        # Create build directory
        build_temp = Path(self.build_temp).absolute()
        build_temp.mkdir(parents=True, exist_ok=True)

        # Build each component in order
        for component in self.COMPONENTS:
            self.build_component(component, build_temp)

    def build_component(self, component, build_temp):
        """Clone and build a single component."""
        name = component["name"]
        repo = component["repo"]
        cmake_args = component.get("cmake_args", [])

        print(f"\n{'='*60}")
        print(f"Building component: {name}")
        print(f"{'='*60}\n")

        # Set up directories
        source_dir = build_temp / name
        build_dir = build_temp / f"{name}-build"
        install_prefix = Path(sys.prefix).absolute()

        # Clone repository if not already present
        if not source_dir.exists():
            print(f"Cloning {repo}...")
            subprocess.check_call(["git", "clone", repo, str(source_dir)])
        else:
            print(f"Using existing source at {source_dir}")

        # Create build directory
        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure CMake
        cmake_configure_args = [
            "cmake",
            str(source_dir),
            f"-DCMAKE_INSTALL_PREFIX={install_prefix}",
            f"-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_SHARED_LIBS=ON",
            "-DBUILD_TESTING=OFF",  # Disable tests to avoid Catch2 dependency
        ]
        cmake_configure_args.extend(cmake_args)

        # Add Python-specific paths
        if sys.platform.startswith("win"):
            cmake_configure_args.append(f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={self.build_lib}")

        print(f"Configuring with CMake...")
        print(f"Command: {' '.join(cmake_configure_args)}")
        subprocess.check_call(cmake_configure_args, cwd=build_dir)

        # Build
        print(f"Building {name}...")
        build_args = ["cmake", "--build", ".", "--config", "Release"]

        # Determine number of parallel jobs
        if hasattr(self, "parallel") and self.parallel:
            build_args.extend(["--parallel", str(self.parallel)])
        else:
            # Use all available cores
            import multiprocessing
            build_args.extend(["--parallel", str(multiprocessing.cpu_count())])

        subprocess.check_call(build_args, cwd=build_dir)

        # Install
        print(f"Installing {name}...")
        install_args = ["cmake", "--install", "."]
        subprocess.check_call(install_args, cwd=build_dir)

        print(f"\n{name} built and installed successfully!\n")


# Create extensions list
ext_modules = [
    CMakeExtension(
        "iowarp_core._native",
        sourcedir=".",
    )
]


if __name__ == "__main__":
    setup(
        ext_modules=ext_modules,
        cmdclass={"build_ext": CMakeBuild},
    )
