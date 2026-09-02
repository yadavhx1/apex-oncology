"""
OBJECTIVE:
  Prove the configuration-driven DOS/GRACE assignment reproduces the values that
  were hardcoded in AML_LOT_VAL.ipynb, and that the generated SQL says what the
  configuration says.

USER INPUTS:
  None.

SOURCE TABLES:
  None. Configuration only; issues no queries and needs no Spark.

OUTPUT:
  Pass/fail per check. Exit 0 = all passed.

Run with either:

    python franchises/Venclexta/scripts/test_dos_grace_config.py
    pytest franchises/Venclexta/scripts/test_dos_grace_config.py

MIGRATION_BASELINE below is the mapping extracted from the notebook's original
hardcoded CASE expressions. It is a deliberate snapshot: if you intentionally change
a grace or DOS value, this test SHOULD fail, and you update the baseline in the same
commit with the business reason in the message. That makes every movement in reported
lines of therapy an explicit, reviewable act rather than a silent config edit.
"""

import re
import sys

from dos_grace_config import (
    ConfigError,
    build_dos_case_sql,
    build_grace_case_sql,
    build_product_exclusion_sql,
    dos_px_map,
    grace_map,
    load_config,
)

# ---------------------------------------------------------------------------
# Frozen snapshot of the original hardcoded values. Do not edit casually.
# ---------------------------------------------------------------------------

MIGRATION_BASELINE_GRACE = {
    "ARSENIC_TRIOXIDE": 60, "AZACITIDINE": 60, "CLADRIBINE": 7, "CLOFARABINE": 5,
    "CYCLOPHOSPHAMIDE": 5, "DAUNORUBICIN": 5, "DAURISMO": 60, "DECITABINE": 60,
    "ETOPOSIDE": 5, "FLUDARABINE": 5, "HI-DAC": 7, "IDARUBICIN": 5, "IDHIFA": 60,
    "INQOVI": 28, "L-DAC": 60, "MITOXANTRONE": 3, "MYLOTARG": 7, "NEXAVAR": 18,
    "ONUREG": 28, "REZLIDHIA": 60, "RYDAPT": 60, "S-DAC": 7, "TIBSOVO": 60,
    "VANFLYTA": 28, "VENCLEXTA": 60, "VINCRISTINE": 28, "VYXEOS": 5, "XOSPATA": 60,
}

MIGRATION_BASELINE_DOS_PX = {
    "ARSENIC_TRIOXIDE": 28, "AZACITIDINE": 28, "CLADRIBINE": 1, "CLOFARABINE": 1,
    "CYCLOPHOSPHAMIDE": 1, "DAUNORUBICIN": 1, "DECITABINE": 28, "ETOPOSIDE": 1,
    "FLUDARABINE": 1, "HI-DAC": 1, "IDARUBICIN": 1, "L-DAC": 1, "MITOXANTRONE": 1,
    "MYLOTARG": 1, "S-DAC": 1, "VINCRISTINE": 1, "VYXEOS": 1,
}

MIGRATION_BASELINE_RX_FALLBACK = 28
MIGRATION_BASELINE_EXCLUSIONS = ["FILGRASTIM"]


# ---------------------------------------------------------------------------
# Helpers — parse a generated CASE expression back into {product: value}
# ---------------------------------------------------------------------------

_BRANCH = re.compile(
    r"WHEN\s+FINAL_PRODUCT_NAME\s*(?:IN\s*\(([^)]*)\)|=\s*('[A-Z0-9_\-]+'))\s*THEN\s*(\d+)",
    re.IGNORECASE,
)
_NAMES = re.compile(r"'([A-Z0-9_\-]+)'")


def parse_case(sql):
    out = {}
    for names_in, name_eq, value in _BRANCH.findall(sql):
        for product in _NAMES.findall(names_in or name_eq):
            assert product not in out, "product %s matched twice in generated SQL" % product
            out[product] = int(value)
    return out


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_config_is_valid():
    load_config()


def test_grace_matches_migration_baseline():
    cfg = load_config()
    assert grace_map(cfg) == MIGRATION_BASELINE_GRACE


def test_dos_px_matches_migration_baseline():
    cfg = load_config()
    assert dos_px_map(cfg) == MIGRATION_BASELINE_DOS_PX


def test_rx_fallback_matches_migration_baseline():
    cfg = load_config()
    assert cfg["dos"]["rx_fallback_days_supply"] == MIGRATION_BASELINE_RX_FALLBACK


def test_exclusions_match_migration_baseline():
    cfg = load_config()
    assert sorted(cfg.get("product_exclusions") or []) == sorted(MIGRATION_BASELINE_EXCLUSIONS)


def test_generated_grace_sql_round_trips():
    """The SQL must assign exactly what the config says — no product lost or doubled."""
    cfg = load_config()
    assert parse_case(build_grace_case_sql(cfg)) == grace_map(cfg)


def test_generated_dos_sql_round_trips():
    cfg = load_config()
    sql = build_dos_case_sql(cfg)
    # Only the PX arm carries per-product branches.
    px_arm = sql.split("'PX'", 1)[1]
    assert parse_case(px_arm) == dos_px_map(cfg)


def test_generated_grace_sql_defaults_to_null():
    cfg = load_config()
    assert "ELSE NULL" in build_grace_case_sql(cfg)


def test_generated_dos_px_arm_has_no_else():
    """Original PX CASE had no ELSE; an unlisted product must stay NULL, not inherit a default."""
    cfg = load_config()
    px_arm = build_dos_case_sql(cfg).split("'PX'", 1)[1]
    assert "ELSE" not in px_arm.upper()


def test_rx_arm_uses_claim_days_supply():
    cfg = load_config()
    sql = build_dos_case_sql(cfg)
    rx_arm = sql.split("'PX'", 1)[0]
    assert "PRODUCT_DAYS_SUPPLY IS NULL OR PRODUCT_DAYS_SUPPLY <= 0" in rx_arm
    assert "ELSE PRODUCT_DAYS_SUPPLY" in rx_arm


def test_exclusion_predicate():
    cfg = load_config()
    assert build_product_exclusion_sql(cfg) == "FINAL_PRODUCT_NAME <> 'FILGRASTIM'"


def test_product_names_are_quoted_safely():
    """A product name carrying an apostrophe must not break out of its literal."""
    cfg = load_config()
    cfg["products"]["O'BRIEN"] = {"grace": 5, "dos_px": None}
    assert "'O''BRIEN'" in build_grace_case_sql(cfg)


def test_validation_rejects_negative_grace():
    cfg = load_config()
    cfg["products"]["MYLOTARG"]["grace"] = -1
    _expect_config_error(cfg, "must be positive")


def test_validation_rejects_missing_key():
    cfg = load_config()
    del cfg["products"]["MYLOTARG"]["dos_px"]
    _expect_config_error(cfg, "missing `dos_px`")


def test_validation_rejects_unknown_key():
    cfg = load_config()
    cfg["products"]["MYLOTARG"]["grase"] = 7
    _expect_config_error(cfg, "unknown key")


def test_validation_rejects_non_null_grace_default():
    cfg = load_config()
    cfg["grace"]["default"] = 30
    _expect_config_error(cfg, "grace.default must be null")


def test_validation_rejects_excluded_product_with_values():
    cfg = load_config()
    cfg["product_exclusions"].append("MYLOTARG")
    _expect_config_error(cfg, "both excluded and assigned")


def test_validation_rejects_bad_product_name():
    cfg = load_config()
    cfg["products"]["bad name!"] = {"grace": 5, "dos_px": None}
    _expect_config_error(cfg, "must match")


def _expect_config_error(cfg, fragment):
    from dos_grace_config import _validate

    try:
        _validate(cfg)
    except ConfigError as exc:
        assert fragment in str(exc), "expected %r in:\n%s" % (fragment, exc)
        return
    raise AssertionError("expected ConfigError containing %r" % fragment)


# ---------------------------------------------------------------------------
# Standalone runner, so this works without pytest installed.
# ---------------------------------------------------------------------------


def _run():
    tests = sorted(
        (name, obj)
        for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    )
    failures = []
    for name, fn in tests:
        try:
            fn()
            print("PASS  %s" % name)
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures.append((name, exc))
            print("FAIL  %s -> %s" % (name, exc))

    print("\n%d passed, %d failed" % (len(tests) - len(failures), len(failures)))
    if failures:
        print(
            "\nIf a MIGRATION_BASELINE test failed and the change was intentional, "
            "update the baseline in this file in the same commit and say why."
        )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run())
