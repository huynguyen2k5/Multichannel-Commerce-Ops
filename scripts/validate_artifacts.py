#!/usr/bin/env python3
"""Validate non-code artifacts that must remain importable/editable."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / "n8n" / "workflows"
DRAWIO_FILE = ROOT / "docs" / "architecture" / "MCO_Architecture_Specification.drawio"


def validate_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: invalid JSON: {exc}"]

    nodes = payload.get("nodes")
    connections = payload.get("connections")
    if not isinstance(nodes, list) or not nodes:
        return [f"{path.relative_to(ROOT)}: nodes must be a non-empty list"]
    if not isinstance(connections, dict):
        return [f"{path.relative_to(ROOT)}: connections must be an object"]

    names = [node.get("name") for node in nodes if isinstance(node, dict)]
    valid_names = {name for name in names if isinstance(name, str) and name}
    if len(valid_names) != len(names):
        errors.append(f"{path.relative_to(ROOT)}: every node needs a unique non-empty name")

    for source_name, outputs in connections.items():
        if source_name not in valid_names:
            errors.append(
                f"{path.relative_to(ROOT)}: connection source '{source_name}' is not a node"
            )
            continue
        if not isinstance(outputs, dict):
            errors.append(
                f"{path.relative_to(ROOT)}: connection '{source_name}' must be an object"
            )
            continue
        for output_groups in outputs.values():
            if not isinstance(output_groups, list):
                continue
            for group in output_groups:
                if not isinstance(group, list):
                    continue
                for edge in group:
                    target = edge.get("node") if isinstance(edge, dict) else None
                    if target not in valid_names:
                        errors.append(
                            f"{path.relative_to(ROOT)}: '{source_name}' targets unknown node "
                            f"'{target}'"
                        )

    return errors


def validate_drawio(path: Path) -> list[str]:
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError) as exc:
        return [f"{path.relative_to(ROOT)}: invalid draw.io XML: {exc}"]

    diagrams = tree.getroot().findall("diagram")
    if not diagrams:
        return [f"{path.relative_to(ROOT)}: no diagram pages found"]
    page_names = [diagram.attrib.get("name", "") for diagram in diagrams]
    if any(not name for name in page_names):
        return [f"{path.relative_to(ROOT)}: every diagram page must have a name"]
    if len(page_names) != len(set(page_names)):
        return [f"{path.relative_to(ROOT)}: diagram page names must be unique"]
    return []


def main() -> int:
    errors: list[str] = []
    workflows = sorted(WORKFLOW_DIR.glob("*.json"))
    if not workflows:
        errors.append("n8n/workflows: no workflow JSON files found")
    for workflow in workflows:
        errors.extend(validate_workflow(workflow))
    errors.extend(validate_drawio(DRAWIO_FILE))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(workflows)} n8n workflows and draw.io architecture package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
