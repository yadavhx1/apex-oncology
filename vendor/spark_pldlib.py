"""
OBJECTIVE:
  Ship the vendored ZS pldlib library to a Spark session, so a notebook can
  `from pldlib import stencil` without a copy of the egg in its launch directory.

USER INPUTS:
  None. Set PLDLIB_EGG only when a cluster stages the egg somewhere else.

SOURCE TABLES:
  None. This module handles library distribution only; it issues no queries.

OUTPUT:
  pldlib, businessLogic and common_utilities importable on the driver and on the
  executors. attach() returns the path it shipped.

Provenance, version and upgrade steps: vendor/README.md
Self-check without a cluster: python vendor/spark_pldlib.py
"""

import os
import sys
import zipfile

EGG_FILENAME = "pldlib.egg"

VENDOR_DIR = os.path.dirname(os.path.abspath(__file__))

# Default egg location, resolved relative to this file so a notebook works
# regardless of the directory it is launched from. Override with PLDLIB_EGG.
DEFAULT_EGG_PATH = os.path.join(VENDOR_DIR, EGG_FILENAME)

# Top-level packages the egg provides, from its EGG-INFO/top_level.txt.
PROVIDED_PACKAGES = ("pldlib", "businessLogic", "common_utilities")

# Marker identifying the repository root when walking up from a working directory.
REPO_ROOT_MARKER = "AGENTS.md"

# Egg paths already shipped to a session, so re-running a cell is harmless.
_ATTACHED = set()


class PldlibError(Exception):
    """Raised when the vendored egg is missing, corrupt or incomplete."""


# ---------------------------------------------------------------------------
# Locating the egg
# ---------------------------------------------------------------------------


def egg_path(path=None):
    """Absolute path to the egg: explicit argument, then PLDLIB_EGG, then vendored."""
    path = path or os.environ.get("PLDLIB_EGG") or DEFAULT_EGG_PATH
    return os.path.abspath(path)


def repo_root(start=None):
    """Repository root, found by walking up from `start` (default: working directory).

    Notebooks have no __file__, so they cannot resolve vendor/ the way a .py can.
    """
    current = os.path.abspath(start or os.getcwd())
    while not os.path.exists(os.path.join(current, REPO_ROOT_MARKER)):
        parent = os.path.dirname(current)
        if parent == current:
            raise PldlibError(
                "repository root not found above %s (looked for %s) — run from inside "
                "the apex-oncology checkout, or set PLDLIB_EGG to the egg's location"
                % (os.path.abspath(start or os.getcwd()), REPO_ROOT_MARKER)
            )
        current = parent
    return current


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify(path=None):
    """Check the egg is present, a readable archive, and holds the expected packages.

    Fails here rather than letting the job die later inside an executor with a bare
    ImportError, which is considerably harder to diagnose.
    """
    path = egg_path(path)

    if not os.path.exists(path):
        raise PldlibError(
            "pldlib egg not found at %s — check out vendor/ in full, or set PLDLIB_EGG"
            % path
        )

    if not zipfile.is_zipfile(path):
        raise PldlibError(
            "%s is not a readable egg archive. A text-mode checkout corrupts it; "
            "confirm .gitattributes marks *.egg as binary (see vendor/README.md)" % path
        )

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()

    missing = [
        package
        for package in PROVIDED_PACKAGES
        if not any(name.startswith(package + "/") for name in names)
    ]
    if missing:
        raise PldlibError(
            "%s is missing package(s) %s — wrong or truncated egg"
            % (path, ", ".join(missing))
        )

    return path


# ---------------------------------------------------------------------------
# Attaching to a Spark session
# ---------------------------------------------------------------------------


def attach(spark, path=None):
    """Ship the egg to the executors and make it importable on the driver.

    Returns the egg path attached. Safe to call again — a repeated call for the same
    egg is a no-op, so re-running the cell does not re-ship the file.
    """
    path = verify(path)

    if path not in _ATTACHED:
        spark.sparkContext.addPyFile(path)
        _ATTACHED.add(path)

    # addPyFile puts the executor-side copy on the driver's path too, but that copy
    # lives in a Spark temp directory. Add the vendored egg as well so a driver-side
    # import holds even if that staging directory is cleaned up mid-session.
    if path not in sys.path:
        sys.path.append(path)

    return path


def describe(path=None):
    """One-line-per-fact summary of what will be attached. Printed by the notebook."""
    path = verify(path)

    with zipfile.ZipFile(path) as archive:
        try:
            metadata = archive.read("EGG-INFO/PKG-INFO").decode("utf-8", "replace")
        except KeyError:
            metadata = ""

    version = "unknown"
    for line in metadata.splitlines():
        if line.startswith("Version:"):
            version = line.split(":", 1)[1].strip()
            break

    return "\n".join(
        [
            "pldlib egg:   %s" % path,
            "version:      %s" % version,
            "provides:     %s" % ", ".join(PROVIDED_PACKAGES),
            "size:         %d bytes" % os.path.getsize(path),
        ]
    )


if __name__ == "__main__":
    # Self-check: verifies the egg without needing a Spark session or a cluster.
    try:
        print(describe())
    except PldlibError as exc:
        sys.exit("FAIL: %s" % exc)
    print("\nOK — egg is present and complete.")
