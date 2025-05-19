# SPDX-FileCopyrightText: 2025 Authors (see AUTHORS.txt)
#
# SPDX-License-Identifier: Apache-2.0

"""Check whether requirements are installed."""

import shutil
import subprocess
import re
from dataclasses import dataclass

from .utils import logger, fail


@dataclass
class Require:
    """Requirement."""

    name: str
    min_version: tuple
    mandatory: bool


REQUIREMENTS = (
    Require("conan", None, True),
    Require("wheel", None, True),
    Require("cmake", (3, 29), True),
    Require("git", None, True),
    Require("act", None, False),
    Require("gh", None, False),
    Require("repairwheel", None, False),
)


def _version_tuple(version_str):
    """Translate version into a tuple of int."""
    if not version_str:
        return None
    if "-" in version_str:
        version_str, *_ = version_str.rpartition("-")
    try:
        return tuple(int(i) for i in version_str.split("."))
    except ValueError:
        return None


def check(name, min_version=None, mandatory=True):
    """Check whether an app exists and whether its version is correct."""

    def error(*args):
        log = logger.error if mandatory else logger.warning
        log(*args)
        return not mandatory

    # Existence
    if not (app := shutil.which(name)):
        return error("'%s' is missing!", name)

    # Get version
    result = subprocess.run(
        [app, "--version"], capture_output=True, text=True, check=False
    )
    output = result.stdout.strip() or result.stderr.strip()
    # Match version patterns like 1.2.3, 4.5, 2.0.1-alpha, etc.
    if match := re.search(r"\d+\.\d+(?:\.\d+)?(?:[-.\w]*)?", output):
        version_str = match.group(0)
    else:
        version_str = None

    # Check Version, if necessary
    if min_version:
        min_version_str = ".".join(str(i) for i in min_version)

        # Translate version
        if not (version := _version_tuple(version_str)):
            return error("Cannot read '%s' version", name)
        if version < min_version:
            return error(
                "'%s': installed version ('%s') is lower than required ('%s')",
                app,
                version_str,
                min_version_str,
            )
    if version_str:
        logger.info("Looking for '%s' - Found '%s', version '%s'", name, app, version_str)
    else:
        logger.info("Looking for '%s' - Found '%s'", name, app)

    return True


def check_requirements():
    """Check all requirements."""
    logger.info("Checking requirements:")
    checks = (
        check(req.name, req.min_version, req.mandatory) for req in REQUIREMENTS
    )
    if not all(checks):
        fail("Some mandatory requirements are missing. Please check...")
    logger.info("Requirements - OK")
