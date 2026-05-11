"""
fix_sqlacodegen_models.py — Enhanced v2 for Mobility App
=========================================================
Fixes output from sqlacodegen to be compatible with:
  - SQLAlchemy 2.0 Mapped[] syntax
  - UUID primary keys
  - PostgreSQL ARRAY[] columns
  - Proper Optional typing
  - relationship() with back_populates
  - Removes duplicate Base inheritance
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# ─── Helpers ──────────────────────────────────────────────────────────────────

def camel_to_snake(name: str) -> str:
    """CamelCase → snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """snake_case → CamelCase (for class name lookup)."""
    return "".join(part.capitalize() for part in name.split("_"))


# ─── Fix Functions ─────────────────────────────────────────────────────────────

def fix_imports(text: str) -> str:
    """
    Ensure 'from __future__ import annotations' is ALWAYS the first line.
    sqlacodegen sometimes generates it mid-file — move it to top.
    """
    future_import = "from __future__ import annotations"

    # Remove all occurrences (wherever they appear)
    lines = [ln for ln in text.splitlines() if ln.strip() != future_import]

    # Re-insert at position 0, followed by blank line
    lines = [future_import, ""] + lines

    return "\n".join(lines)


def fix_indented_constraints(text: str) -> str:
    """Fix sqlacodegen bug: ForeignKeyConstraint wrongly indented."""
    text = re.sub(r"\n\s{8,}(ForeignKeyConstraint)", r"\n    \1", text)
    text = re.sub(r"\n\s{8,}(UniqueConstraint)", r"\n    \1", text)
    text = re.sub(r"\n\s{8,}(CheckConstraint)", r"\n    \1", text)
    return text


def fix_inheritance(text: str) -> str:
    """Replace wrong parent class with Base (except class Base itself)."""
    pattern = re.compile(r"class\s+(\w+)\((\w+)\):")
    for child, parent in pattern.findall(text):
        if parent.lower() == "base" or child.lower() == "base":
            continue
        text = re.sub(
            rf"class {child}\({parent}\):",
            f"class {child}(Base):",
            text,
        )
    return text


def fix_uuid_columns(text: str) -> str:
    """
    sqlacodegen may generate UUID columns as String(32).
    Convert to proper UUID type for PostgreSQL.
    """
    # Replace String(32) in UUID-named columns
    text = re.sub(
        r"(Mapped\[Optional\[)str(\]\] = mapped_column\(String\(32\))",
        r"\1UUID\2",
        text,
    )
    # Ensure uuid_generate_v4 server_default uses text()
    text = re.sub(
        r"server_default='uuid_generate_v4\(\)'",
        "server_default=text('uuid_generate_v4()')",
        text,
    )
    return text


def fix_array_columns(text: str) -> str:
    """Fix ARRAY column type annotation."""
    # ARRAY(Enum(...)) → keep as-is but fix Mapped type
    text = re.sub(
        r"Mapped\[Optional\[list\]\](\s*=\s*mapped_column\(ARRAY)",
        r"Mapped[Optional[list]]\1",
        text,
    )
    return text


def fix_jsonb_columns(text: str) -> str:
    """Ensure JSONB columns have dict type hint."""
    text = re.sub(
        r"Mapped\[Optional\[Any\]\](\s*=\s*mapped_column\(JSONB)",
        r"Mapped[Optional[dict]]\1",
        text,
    )
    return text


def get_all_class_names(text: str) -> list[str]:
    """Extract all class names that inherit Base."""
    return re.findall(r"class\s+(\w+)\(Base\):", text)


def find_class_block(text: str, class_name: str) -> str | None:
    """Extract the full text block of a class."""
    m = re.search(
        rf"(class {class_name}\(Base\):[\s\S]+?)(?=\nclass |\Z)",
        text,
        re.MULTILINE,
    )
    return m.group(1) if m else None


def extract_fk_relationships(text: str) -> list[tuple[str, str, str]]:
    """
    Scan for ForeignKey('table.col') to infer relationships.
    Returns list of (child_class, parent_table, fk_col_name).
    """
    results = []
    # Find: col_name: Mapped[...] = mapped_column(ForeignKey('table.id'))
    fk_pattern = re.compile(
        r"(\w+)\s*:\s*Mapped\[.*?\]\s*=\s*mapped_column\([^)]*ForeignKey\('(\w+)\.(\w+)'\)",
        re.MULTILINE,
    )
    # Get class → fields mapping
    class_blocks = re.findall(
        r"class\s+(\w+)\(Base\):([\s\S]+?)(?=\nclass |\Z)",
        text,
        re.MULTILINE,
    )
    for class_name, block in class_blocks:
        for fk_col, ref_table, ref_col in fk_pattern.findall(block):
            results.append((class_name, ref_table, fk_col))
    return results


def table_to_class(text: str) -> dict[str, str]:
    """Build mapping: __tablename__ value → class name."""
    mapping = {}
    pattern = re.compile(
        r"class\s+(\w+)\(Base\):[\s\S]*?__tablename__\s*=\s*['\"](\w+)['\"]",
        re.MULTILINE,
    )
    for class_name, table_name in pattern.findall(text):
        mapping[table_name] = class_name
    return mapping


def inject_relationships(text: str) -> str:
    """
    Auto-inject SQLAlchemy relationship() based on ForeignKey analysis.
    - child → parent: many-to-one (uselist=False)
    - parent → child: one-to-many (uselist=True for plural)
    Skips if relationship already exists.
    """
    tbl2cls = table_to_class(text)
    fk_rels = extract_fk_relationships(text)

    added: set[tuple[str, str]] = set()

    for child_class, parent_table, fk_col in fk_rels:
        parent_class = tbl2cls.get(parent_table)
        if not parent_class or parent_class == child_class:
            continue

        pair = (child_class, parent_class)
        if pair in added:
            continue
        added.add(pair)

        child_field_name = camel_to_snake(child_class)       # e.g. driver_profile
        parent_field_name = camel_to_snake(parent_class)     # e.g. user

        # ── 1. child → parent (many-to-one) ──
        child_block = find_class_block(text, child_class)
        marker_c = f"# rel: {child_class} → {parent_class}"
        if child_block and marker_c not in child_block and parent_field_name not in child_block:
            rel_c = (
                f"\n    {marker_c}\n"
                f"    {parent_field_name}: Mapped['{parent_class}'] = relationship(\n"
                f"        '{parent_class}', foreign_keys=[{fk_col}], back_populates='{child_field_name}')\n"
            )
            new_block = child_block.rstrip() + rel_c + "\n"
            text = text.replace(child_block, new_block)

        # ── 2. parent → child (one-to-many) ──
        parent_block = find_class_block(text, parent_class)
        marker_p = f"# rel: {parent_class} → {child_class}"
        if parent_block and marker_p not in parent_block and child_field_name not in parent_block:
            rel_p = (
                f"\n    {marker_p}\n"
                f"    {child_field_name}: Mapped[list['{child_class}']] = relationship(\n"
                f"        '{child_class}', back_populates='{parent_field_name}')\n"
            )
            new_block = parent_block.rstrip() + rel_p + "\n"
            text = text.replace(parent_block, new_block)

    return text


def add_summary_comment(text: str) -> str:
    marker = "# === AUTO FIX SUMMARY ==="
    if marker in text:
        return text
    summary = (
        "\n\n# === AUTO FIX SUMMARY ===\n"
        "# Generated by fix_sqlacodegen_models.py v2\n"
        "# • Fixed class inheritance → Base\n"
        "# • Fixed indented ForeignKeyConstraint\n"
        "# • Injected relationship() with back_populates\n"
        "# • Fixed UUID / ARRAY / JSONB type hints\n"
        "# • Added necessary imports\n"
        "# ==========================\n"
    )
    return text + summary


# ─── Main Entry ───────────────────────────────────────────────────────────────

def fix_sqlacodegen_file(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    print(f"🔧 Processing: {filepath}")
    text = path.read_text(encoding="utf-8")

    steps = [
        ("Fixing imports",              fix_imports),
        ("Fixing indented constraints", fix_indented_constraints),
        ("Fixing class inheritance",    fix_inheritance),
        ("Fixing UUID columns",         fix_uuid_columns),
        ("Fixing ARRAY columns",        fix_array_columns),
        ("Fixing JSONB columns",        fix_jsonb_columns),
        ("Injecting relationships",     inject_relationships),
        ("Adding summary comment",      add_summary_comment),
    ]

    for step_name, fn in steps:
        print(f"  ⚙️  {step_name}...")
        text = fn(text)

    path.write_text(text, encoding="utf-8")
    print(f"✅ Done → {filepath}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "app/db/models/database.py"
    fix_sqlacodegen_file(target)
