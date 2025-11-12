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
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


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
                "-DHSHM_ENABLE_ZMQ=ON",
                "-DHSHM_ENABLE_ELF=ON",
                "-DHSHM_BUILD_TESTS=OFF",
            ],
            "test_flags": [
                "-DBUILD_TESTS=OFF",
                "-DBUILD_TEST=OFF",
                "-DENABLE_TESTS=OFF",
                "-DENABLE_TESTING=OFF",
            ]
        },
        {
            "name": "runtime",
            "repo": "https://github.com/iowarp/runtime",
            "cmake_args": [],
            "test_flags": [
                "-DBUILD_TESTS=OFF",
                "-DBUILD_TEST=OFF",
                "-DENABLE_TESTS=OFF",
                "-DENABLE_TESTING=OFF",
            ]
        },
        {
            "name": "context-transfer-engine",
            "repo": "https://github.com/iowarp/context-transfer-engine",
            "cmake_args": [
                "-DCTE_BUILD_TESTS=OFF",
                "-DCTE_ENABLE_TESTS=OFF",
            ],
            "test_flags": [
                "-DBUILD_TESTS=OFF",
                "-DBUILD_TEST=OFF",
                "-DENABLE_TESTS=OFF",
                "-DENABLE_TESTING=OFF",
            ]
        },
        {
            "name": "context-assimilation-engine",
            "repo": "https://github.com/iowarp/context-assimilation-engine",
            "cmake_args": [
                "-DCAE_BUILD_TESTS=OFF",
                "-DCAE_ENABLE_TESTS=OFF",
            ],
            "test_flags": [
                "-DBUILD_TESTS=OFF",
                "-DBUILD_TEST=OFF",
                "-DENABLE_TESTS=OFF",
                "-DENABLE_TESTING=OFF",
            ]
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

        # If bundling binaries, copy them to the package directory
        if os.environ.get("IOWARP_BUNDLE_BINARIES", "OFF").upper() == "ON":
            self.copy_binaries_to_package(build_temp)

    def apply_patches(self, component_name, source_dir):
        """Apply necessary patches to component source code."""
        if component_name == "context-assimilation-engine":
            # Fix HDF5 1.12+ API compatibility
            hdf5_file = source_dir / "core/src/factory/hdf5_file_assimilator.cc"
            if hdf5_file.exists():
                print(f"Patching {hdf5_file} for HDF5 1.12+ API compatibility...")
                content = hdf5_file.read_text()

                # Fix H5O_info_t to H5O_info2_t
                content = content.replace("H5O_info_t obj_info;", "H5O_info2_t obj_info;")

                # Fix H5Oget_info_by_name to H5Oget_info_by_name3 with fields parameter
                content = content.replace(
                    "H5Oget_info_by_name(loc_id, name, &obj_info, H5P_DEFAULT)",
                    "H5Oget_info_by_name3(loc_id, name, &obj_info, H5O_INFO_BASIC, H5P_DEFAULT)"
                )

                hdf5_file.write_text(content)
                print(f"Successfully patched {hdf5_file}")

    def build_component(self, component, build_temp):
        """Clone and build a single component."""
        name = component["name"]
        repo = component["repo"]
        cmake_args = component.get("cmake_args", [])
        test_flags = component.get("test_flags", [])

        print(f"\n{'='*60}")
        print(f"Building component: {name}")
        print(f"{'='*60}\n")

        # Set up directories
        source_dir = build_temp / name
        build_dir = build_temp / f"{name}-build"

        # Determine install prefix based on whether we're bundling binaries
        bundle_binaries = os.environ.get("IOWARP_BUNDLE_BINARIES", "OFF").upper() == "ON"
        if bundle_binaries:
            # Install to a staging directory that we'll copy into the wheel
            install_prefix = build_temp / "install"
        else:
            # Install to system prefix (for editable installs)
            install_prefix = Path(sys.prefix).absolute()

        # Clone repository if not already present
        if not source_dir.exists():
            print(f"Cloning {repo}...")
            subprocess.check_call(["git", "clone", "--recursive", repo, str(source_dir)])
        else:
            print(f"Using existing source at {source_dir}")
            # Update submodules if using existing source
            print(f"Updating submodules for {name}...")
            subprocess.check_call(["git", "submodule", "update", "--init", "--recursive"], cwd=source_dir)

        # Apply patches for specific components
        self.apply_patches(name, source_dir)

        # Create build directory
        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure CMake
        cmake_configure_args = [
            "cmake",
            str(source_dir),
            f"-DCMAKE_INSTALL_PREFIX={install_prefix}",
            f"-DCMAKE_PREFIX_PATH={install_prefix}",
            f"-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_SHARED_LIBS=ON",
            "-DBUILD_TESTING=OFF",  # Disable tests to avoid Catch2 dependency
            f"-DPython3_EXECUTABLE={sys.executable}",  # Explicitly pass Python executable
        ]

        # Add HDF5_ROOT to use conda's HDF5 (compatible version) instead of system HDF5
        # This avoids API compatibility issues with HDF5 2.0
        conda_prefix = os.environ.get("CONDA_PREFIX")
        if conda_prefix:
            cmake_configure_args.append(f"-DHDF5_ROOT={conda_prefix}")

        cmake_configure_args.extend(cmake_args)

        # Add test-disabling flags if not building tests
        if os.environ.get("IOWARP_BUILD_TESTS", "OFF").upper() == "OFF":
            cmake_configure_args.extend(test_flags)

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

    def copy_binaries_to_package(self, build_temp):
        """Copy built binaries and headers into the Python package for wheel bundling."""
        print("\n" + "="*60)
        print("Copying binaries to package directory")
        print("="*60 + "\n")

        install_prefix = build_temp / "install"
        package_dir = Path(self.build_lib) / "iowarp_core"

        # Create directories in the package
        lib_dir = package_dir / "lib"
        include_dir = package_dir / "include"
        bin_dir = package_dir / "bin"

        lib_dir.mkdir(parents=True, exist_ok=True)
        include_dir.mkdir(parents=True, exist_ok=True)
        bin_dir.mkdir(parents=True, exist_ok=True)

        # Copy libraries
        src_lib_dir = install_prefix / "lib"
        if src_lib_dir.exists():
            print(f"Copying libraries from {src_lib_dir} to {lib_dir}")
            for lib_file in src_lib_dir.rglob("*"):
                if lib_file.is_file():
                    # Copy .so, .a, and .dylib files
                    if lib_file.suffix in [".so", ".a", ".dylib"] or ".so." in lib_file.name:
                        rel_path = lib_file.relative_to(src_lib_dir)
                        dest = lib_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(lib_file, dest)
                        print(f"  Copied: {rel_path}")

        # Copy lib64 if it exists (some systems use lib64)
        src_lib64_dir = install_prefix / "lib64"
        if src_lib64_dir.exists():
            print(f"Copying libraries from {src_lib64_dir} to {lib_dir}")
            for lib_file in src_lib64_dir.rglob("*"):
                if lib_file.is_file():
                    if lib_file.suffix in [".so", ".a", ".dylib"] or ".so." in lib_file.name:
                        rel_path = lib_file.relative_to(src_lib64_dir)
                        dest = lib_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(lib_file, dest)
                        print(f"  Copied: {rel_path}")

        # Copy headers
        src_include_dir = install_prefix / "include"
        if src_include_dir.exists():
            print(f"Copying headers from {src_include_dir} to {include_dir}")
            for header_file in src_include_dir.rglob("*"):
                if header_file.is_file():
                    rel_path = header_file.relative_to(src_include_dir)
                    dest = include_dir / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(header_file, dest)

        # Copy binaries/executables
        src_bin_dir = install_prefix / "bin"
        if src_bin_dir.exists():
            print(f"Copying binaries from {src_bin_dir} to {bin_dir}")
            for bin_file in src_bin_dir.rglob("*"):
                if bin_file.is_file():
                    rel_path = bin_file.relative_to(src_bin_dir)
                    dest = bin_dir / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(bin_file, dest)
                    # Make executable
                    dest.chmod(dest.stat().st_mode | 0o111)
                    print(f"  Copied: {rel_path}")

        print("\nBinary copying complete!\n")


class bdist_wheel(_bdist_wheel):
    """Custom bdist_wheel command to set the proper platform tag."""

    def finalize_options(self):
        super().finalize_options()
        # Set platform tag to manylinux_2_39 (or detect from system)
        # This corresponds to glibc 2.39
        self.plat_name = self.plat_name.replace('linux', 'manylinux_2_39')


# Create extensions list
# Only include extensions if we want to bundle binaries in the wheel
# By default, we build as a pure Python wheel since C++ components
# are installed to the system prefix during installation
if os.environ.get("IOWARP_BUNDLE_BINARIES", "OFF").upper() == "ON":
    ext_modules = [
        CMakeExtension(
            "iowarp_core._native",
            sourcedir=".",
        )
    ]
    cmdclass = {
        "build_ext": CMakeBuild,
        "bdist_wheel": bdist_wheel,
    }
else:
    ext_modules = []
    cmdclass = {}


if __name__ == "__main__":
    setup(
        ext_modules=ext_modules,
        cmdclass=cmdclass,
    )
