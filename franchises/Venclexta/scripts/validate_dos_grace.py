"""
OBJECTIVE:
  Validate configuration/aml_dos_grace.yaml and show what it will apply, so a
  DOS/GRACE change can be checked before it reaches a query.

USER INPUTS:
  None. Optional --config path, --sql to print generated SQL, --product to inspect one.

SOURCE TABLES:
  None. Reads configuration only; issues no queries.

OUTPUT:
  Summary and exit status. Exit 0 = valid, 1 = invalid.

Run after any edit to the DOS/GRACE configuration:

    python franchises/Venclexta/scripts/validate_dos_grace.py
    python franchises/Venclexta/scripts/validate_dos_grace.py --sql
    python franchises/Venclexta/scripts/validate_dos_grace.py --product MYLOTARG

Used by the /update-dos-grace skill as its verification step.
"""

import argparse
import sys

from dos_grace_config import (
    ConfigError,
    build_dos_case_sql,
    build_grace_case_sql,
    build_product_exclusion_sql,
    load_config,
    summarise,
)


def _days(value):
    if value is None:
        return "NULL"
    return "%d day%s" % (value, "" if value == 1 else "s")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate the AML DOS/GRACE configuration and show what it applies."
    )
    parser.add_argument("--config", help="path to aml_dos_grace.yaml (default: alongside this script)")
    parser.add_argument("--sql", action="store_true", help="print the generated SQL fragments")
    parser.add_argument("--product", help="show the values for a single product")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print("INVALID\n")
        print(exc)
        print("\nNothing was changed. Fix the problems above and re-run.")
        return 1

    if args.product:
        name = args.product.strip().upper()
        entry = cfg["products"].get(name)
        if entry is None:
            print("%s is not in the configuration." % name)
            close = sorted(p for p in cfg["products"] if name in p or p in name)
            if close:
                print("Did you mean: %s" % ", ".join(close))
            print("\nProducts (%d): %s" % (len(cfg["products"]), ", ".join(sorted(cfg["products"]))))
            return 1
        print("%s" % name)
        print("  grace   %s" % _days(entry.get("grace")))
        print("  dos_px  %s" % _days(entry.get("dos_px")))
        if entry.get("notes"):
            print("  notes   %s" % entry["notes"])
        return 0

    print("VALID\n")
    print(summarise(cfg))

    if args.sql:
        print("\n--- GRACE_VALUE ---")
        print(build_grace_case_sql(cfg))
        print("\n--- DOS_FINAL ---")
        print(build_dos_case_sql(cfg))
        print("\n--- product exclusion predicate ---")
        print(build_product_exclusion_sql(cfg))

    print(
        "\nReminder: a DOS or GRACE change moves reported lines of therapy. "
        "Record the reason in CONTEXT.md and state the blast radius in the PR."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
