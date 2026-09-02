"""
OBJECTIVE:
  Build the GRACE_VALUE and DOS_FINAL CASE expressions for AML line-of-therapy
  validation from configuration instead of hardcoded SQL.

USER INPUTS:
  None. Values come from configuration/aml_dos_grace.yaml.

SOURCE TABLES:
  None. This module reads configuration only; it issues no queries.

OUTPUT:
  SQL fragments consumed by AML_LOT_VAL.ipynb.

To change a value, use the /update-dos-grace skill, or edit the YAML and run
validate_dos_grace.py. Do not hardcode values here.
"""

import os
import re

import yaml

# Default config location, resolved relative to this file so the notebook works
# regardless of the directory it is launched from. Override with the
# AML_DOS_GRACE_CONFIG environment variable.
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir,
    "configuration",
    "aml_dos_grace.yaml",
)

# Product names become SQL string literals, so constrain them to the shape the
# source data actually uses rather than trusting the file.
VALID_PRODUCT_NAME = re.compile(r"^[A-Z0-9_\-]+$")

SUPPORTED_SCHEMA_VERSIONS = (1,)


class ConfigError(Exception):
    """Raised when the configuration is missing, malformed or internally inconsistent."""


# ---------------------------------------------------------------------------
# Loading and validation
# ---------------------------------------------------------------------------


def load_config(path=None):
    """Load and validate the DOS/GRACE configuration.

    Fails loudly rather than silently substituting defaults: a typo that
    silently drops a product would change reported lines of therapy.
    """
    path = path or os.environ.get("AML_DOS_GRACE_CONFIG") or DEFAULT_CONFIG_PATH
    path = os.path.abspath(path)

    if not os.path.exists(path):
        raise ConfigError("configuration not found: %s" % path)

    with open(path, encoding="utf-8") as handle:
        try:
            cfg = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ConfigError("could not parse %s: %s" % (path, exc))

    if not isinstance(cfg, dict):
        raise ConfigError("%s did not parse to a mapping" % path)

    cfg["_path"] = path
    _validate(cfg)
    return cfg


def _validate(cfg):
    version = cfg.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ConfigError(
            "unsupported schema_version %r (supported: %s)"
            % (version, ", ".join(str(v) for v in SUPPORTED_SCHEMA_VERSIONS))
        )

    products = cfg.get("products")
    if not isinstance(products, dict) or not products:
        raise ConfigError("`products` must be a non-empty mapping")

    problems = []

    for name, entry in products.items():
        if not isinstance(name, str) or not VALID_PRODUCT_NAME.match(name):
            problems.append(
                "product name %r must match %s" % (name, VALID_PRODUCT_NAME.pattern)
            )
            continue
        if not isinstance(entry, dict):
            problems.append("%s: entry must be a mapping" % name)
            continue

        unknown = set(entry) - {"grace", "dos_px", "notes"}
        if unknown:
            problems.append(
                "%s: unknown key(s) %s — expected grace, dos_px, notes"
                % (name, ", ".join(sorted(unknown)))
            )

        if "grace" not in entry:
            problems.append("%s: missing `grace` (use null for NULL)" % name)
        if "dos_px" not in entry:
            problems.append("%s: missing `dos_px` (use null for NULL)" % name)

        for key in ("grace", "dos_px"):
            value = entry.get(key)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                problems.append("%s: %s must be a whole number of days or null, got %r"
                                % (name, key, value))
            elif value <= 0:
                problems.append("%s: %s must be positive, got %r" % (name, key, value))

    dos = cfg.get("dos") or {}
    fallback = dos.get("rx_fallback_days_supply")
    if isinstance(fallback, bool) or not isinstance(fallback, int) or fallback <= 0:
        problems.append(
            "dos.rx_fallback_days_supply must be a positive whole number, got %r" % fallback
        )

    grace_block = cfg.get("grace") or {}
    if grace_block.get("default") is not None:
        problems.append(
            "grace.default must be null — a non-null default would assign a grace "
            "period to products nobody has reviewed"
        )

    exclusions = cfg.get("product_exclusions")
    if exclusions is None:
        exclusions = []
    if not isinstance(exclusions, list):
        problems.append("`product_exclusions` must be a list")
    else:
        for item in exclusions:
            if not isinstance(item, str) or not VALID_PRODUCT_NAME.match(item):
                problems.append(
                    "product_exclusions entry %r must match %s"
                    % (item, VALID_PRODUCT_NAME.pattern)
                )

    overlap = set(products) & set(exclusions if isinstance(exclusions, list) else [])
    if overlap:
        problems.append(
            "product(s) both excluded and assigned values: %s — remove from one place"
            % ", ".join(sorted(overlap))
        )

    if problems:
        raise ConfigError(
            "%d problem(s) in %s:\n  - %s"
            % (len(problems), cfg.get("_path", "<config>"), "\n  - ".join(problems))
        )


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------


def grace_map(cfg):
    """{product: grace_days} for products with a non-null grace."""
    return {
        name: entry["grace"]
        for name, entry in cfg["products"].items()
        if entry.get("grace") is not None
    }


def dos_px_map(cfg):
    """{product: dos_days} for products with a non-null PX days-of-supply."""
    return {
        name: entry["dos_px"]
        for name, entry in cfg["products"].items()
        if entry.get("dos_px") is not None
    }


# ---------------------------------------------------------------------------
# SQL generation
# ---------------------------------------------------------------------------


def _quote(value):
    return "'%s'" % value.replace("'", "''")


def _group_by_value(mapping):
    """{product: value} -> [(value, [products])], descending by value.

    Grouping keeps the emitted SQL compact and close to the shape it had when the
    values were hardcoded, which makes review of the generated query easier.
    """
    grouped = {}
    for product, value in mapping.items():
        grouped.setdefault(value, []).append(product)
    return [(value, sorted(grouped[value])) for value in sorted(grouped, reverse=True)]


def _in_list(products, continuation_indent, per_line=6):
    """Render a quoted IN list, wrapping long lists and aligning continuations.

    continuation_indent is the column wrapped lines start at, so a wrapped list
    inside a deeply nested CASE still reads as one branch.
    """
    quoted = [_quote(p) for p in products]
    if len(quoted) <= per_line:
        return ", ".join(quoted)
    chunks = [
        ", ".join(quoted[i:i + per_line])
        for i in range(0, len(quoted), per_line)
    ]
    return (",\n" + " " * continuation_indent).join(chunks)


def build_grace_case_sql(cfg, column="FINAL_PRODUCT_NAME", indent=8):
    """CASE expression assigning GRACE_VALUE. Unlisted products yield NULL."""
    pad = " " * indent
    inner = pad + "    "

    lines = ["CASE"]
    for value, products in _group_by_value(grace_map(cfg)):
        if len(products) == 1:
            lines.append("%sWHEN %s = %s THEN %d" % (inner, column, _quote(products[0]), value))
        else:
            lines.append(
                "%sWHEN %s IN (%s) THEN %d"
                % (inner, column, _in_list(products, len(inner) + 4), value)
            )
    lines.append("%sELSE NULL" % inner)
    lines.append("%sEND" % pad)
    return "\n".join(lines)


def build_dos_case_sql(
    cfg,
    column="FINAL_PRODUCT_NAME",
    native_type_column="NATIVE_TYPE",
    days_supply_column="PRODUCT_DAYS_SUPPLY",
    indent=12,
):
    """CASE expression assigning DOS_FINAL.

    RX claims use the claim's own days supply, falling back to a configured value
    when it is missing or non-positive. PX claims use the per-product value; a
    product with no PX value yields NULL, as in the original SQL.
    """
    pad = " " * indent
    lvl1 = pad + "    "
    lvl2 = lvl1 + "    "
    lvl3 = lvl2 + "    "

    fallback = cfg["dos"]["rx_fallback_days_supply"]

    out = ["CASE"]
    out.append("%sWHEN %s = 'RX' THEN" % (lvl1, native_type_column))
    out.append("%sCASE" % lvl2)
    out.append(
        "%sWHEN (%s IS NULL OR %s <= 0) THEN %d"
        % (lvl3, days_supply_column, days_supply_column, fallback)
    )
    out.append("%sELSE %s" % (lvl3, days_supply_column))
    out.append("%sEND" % lvl2)
    out.append("%sWHEN %s = 'PX' THEN" % (lvl1, native_type_column))
    out.append("%sCASE" % lvl2)
    for value, products in _group_by_value(dos_px_map(cfg)):
        if len(products) == 1:
            out.append(
                "%sWHEN %s = %s THEN %d" % (lvl3, column, _quote(products[0]), value)
            )
        else:
            out.append(
                "%sWHEN %s IN (%s) THEN %d"
                % (lvl3, column, _in_list(products, len(lvl3) + 4), value)
            )
    # No ELSE: products without a PX value yield NULL, matching the original.
    out.append("%sEND" % lvl2)
    out.append("%sEND" % pad)
    return "\n".join(out)


def build_product_exclusion_sql(cfg, column="FINAL_PRODUCT_NAME"):
    """WHERE-clause predicate excluding configured products. `1=1` when none."""
    exclusions = sorted(cfg.get("product_exclusions") or [])
    if not exclusions:
        return "1 = 1"
    if len(exclusions) == 1:
        return "%s <> %s" % (column, _quote(exclusions[0]))
    return "%s NOT IN (%s)" % (column, ", ".join(_quote(p) for p in exclusions))


# ---------------------------------------------------------------------------
# Summary — used by the notebook and by validate_dos_grace.py
# ---------------------------------------------------------------------------


def summarise(cfg):
    """Human-readable summary of what the configuration will apply."""
    products = cfg["products"]
    grace = grace_map(cfg)
    dos_px = dos_px_map(cfg)
    no_grace = sorted(set(products) - set(grace))
    no_dos = sorted(set(products) - set(dos_px))

    lines = [
        "config:            %s" % cfg["_path"],
        "products:          %d" % len(products),
        "with grace:        %d" % len(grace),
        "with PX dos:       %d" % len(dos_px),
        "RX fallback DOS:   %d days (when PRODUCT_DAYS_SUPPLY missing or <= 0)"
        % cfg["dos"]["rx_fallback_days_supply"],
        "exclusions:        %s" % (", ".join(sorted(cfg.get("product_exclusions") or [])) or "none"),
    ]
    if no_grace:
        lines.append("grace NULL for:    %s" % ", ".join(no_grace))
    if no_dos:
        lines.append("PX dos NULL for:   %s" % ", ".join(no_dos))

    lines.append("")
    lines.append("grace groups:")
    for value, items in _group_by_value(grace):
        lines.append("  %3d days  %s" % (value, ", ".join(items)))
    lines.append("PX dos groups:")
    for value, items in _group_by_value(dos_px):
        lines.append("  %3d days  %s" % (value, ", ".join(items)))

    return "\n".join(lines)
