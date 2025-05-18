# SPDX-FileCopyrightText: 2025 Authors (see AUTHORS.txt)
#
# SPDX-License-Identifier: Apache-2.0

"""Utilities for make wrapper."""

import sys
import functools
import logging
import shutil
import subprocess

# Logger
logger = logging.getLogger("LuxCore Build")


# Cmake
@functools.cache
def ensure_cmake_app():
    """Ensure cmake is installed."""
    logger.debug("Looking for cmake")
    if not (res := shutil.which("cmake")):
        logger.error("CMake not found!")
        sys.exit(1)
    logger.debug(
        "CMake found: '%s'",
        res,
    )
    return res


def run_cmake(
    args,
    **kwargs,
):
    """Run cmake statement."""
    cmake_app = ensure_cmake_app()
    args = [cmake_app] + args
    logger.debug(args)
    res = subprocess.run(
        args,
        shell=False,
        check=False,
        **kwargs,
    )
    if res.returncode:
        logger.error("Error while executing cmake")
        print(res.stdout)
        print(res.stderr)
        sys.exit(1)
    return res


def unpack(path, dest):
    """Unpack a wheel."""
    args = [
        sys.executable,
        "-m",
        "wheel",
        "unpack",
        f"--dest={dest}",
        str(path),
    ]
    try:
        output = subprocess.check_output(
            args, text=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as err:
        logger.error(err.output)
        sys.exit(1)
    logger.info(output)


def pack(directory, dest_dir):
    """(Re)pack a wheel."""
    args = [
        sys.executable,
        "-m",
        "wheel",
        "pack",
        f"--dest-dir={dest_dir}",
        str(directory),
    ]
    try:
        output = subprocess.check_output(
            args, text=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as err:
        logger.error(err.output)
        sys.exit(1)
    logger.info(output)
