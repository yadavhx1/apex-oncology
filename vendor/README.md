# vendor/

Third-party libraries that Spark workloads need at run time but that are **not**
installed in the cluster image. Everything here is a build artifact from outside this
repository — not our code, and not edited in place.

This directory is deliberately outside `franchises/`. It holds no business rules and
nothing franchise-specific, and every franchise's notebooks use the same artifact, so
duplicating a binary per franchise would be worse than sharing one copy.

---

## pldlib.egg

| | |
|---|---|
| Library | `pldlib` — patient-level data analysis library for PySpark |
| Version | 0.0.1 |
| Author | ZS Associates (`kuldeepsingh.chauhan@zs.com`) |
| Provides | `pldlib.stencil`, `businessLogic`, `common_utilities` |
| SHA-256 | `381B997D6C62EA72EA4B0BFD1F4D8DC76C017C7F8FBC8B7C66DA4F22B64946DD` |
| Size | 67,468 bytes |
| Upstream source | TODO — record the authoritative location (artifact repository, or the ZS contact who issues builds). Added from a locally staged copy. |

`pldlib.stencil.init(spark)` exposes the standard PLD metrics the line-of-therapy
notebooks are built on: `sob`, `episode`, `regimen`, `compliance`, `eligibility`,
`oneNdone`, `patientSelection`, `patientPersistency`, `episodePersistency`.

## Using it from a notebook

`spark_pldlib.attach(spark)` ships the egg to the executors and makes it importable on
the driver. Copy this cell verbatim into any notebook that needs `pldlib` — it resolves
the repository root from the working directory, so the notebook runs from anywhere:

```python
import os
import sys

# Notebooks have no __file__: walk up from the working directory to the repo root.
_repo_root = os.path.abspath(os.getcwd())
while not os.path.exists(os.path.join(_repo_root, "AGENTS.md")):
    _parent = os.path.dirname(_repo_root)
    if _parent == _repo_root:
        raise RuntimeError("run this notebook from inside the apex-oncology checkout")
    _repo_root = _parent
sys.path.insert(0, os.path.join(_repo_root, "vendor"))

import spark_pldlib

spark_pldlib.attach(spark)          # ships the egg to the executors
print(spark_pldlib.describe())      # confirm the version in use

from pldlib import stencil
```

Working reference: `franchises/Venclexta/scripts/AML_LOT_VAL.ipynb`, cell 3.

A cluster that stages the egg elsewhere can point at it with the `PLDLIB_EGG`
environment variable; nothing in the notebook changes.

## Verifying without a cluster

```
python vendor/spark_pldlib.py
```

Confirms the egg is present, is a readable archive and contains all three packages.
Exit 0 = usable. Worth running after a fresh clone, because a mis-handled binary
checkout is otherwise only discovered when an executor fails to import.

## Why the egg is tracked

`.gitignore` ignores `*.egg` — those are normally build output of the repository
itself. This one is a dependency we must pin, so it is re-included explicitly:

```gitignore
*.egg
!vendor/*.egg
```

`.gitattributes` marks `*.egg binary`. Without it the repository-wide
`* text=auto eol=lf` rule risks line-ending translation, which corrupts the archive.

## Upgrading

1. Drop the new egg in as `vendor/pldlib.egg` — same filename, so no caller changes.
2. `python vendor/spark_pldlib.py` — checks the archive and prints the new version.
3. Update the version, SHA-256 and size in the table above.
4. Re-run the line-of-therapy notebooks and compare patient counts before and after.
   `stencil.sob`, `episode` and `regimen` feed line-of-therapy assignment directly, so
   a behaviour change moves reported lines of therapy.
5. Keep the upgrade in its own commit, separate from any logic change.

## Known quirks

- The egg carries Python 2-era `.pyc` files next to its `.py` sources. Python 3 ignores
  them and imports from source, so this is harmless.
- Importing raises `SyntaxWarning: "is" with 'str' literal` from
  `common_utilities/dataChecks.py`. It comes from the vendored source; do not patch the
  egg to silence it — report it upstream.
