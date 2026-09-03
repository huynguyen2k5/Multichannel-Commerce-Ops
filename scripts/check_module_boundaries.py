#!/usr/bin/env python3
"""AST-based architectural module boundary enforcer for MCO Modular Monolith.

Enforces boundary rules across app/modules/*:
1. Cross-module repository imports are forbidden (Rule 1).
   EXCEPTION: 'reports' read-model aggregation repository may perform cross-domain queries (ADR-001).
2. Services cannot reach into another module's repository (Rule 2).
3. Cross-module imports must only target public module facades or allowed submodules (Rule 3).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple


class BoundaryViolation(NamedTuple):
    file_path: Path
    line: int
    imported_target: str
    rule: str
    message: str
    allowed: str


ALLOWED_CROSS_MODULE_SUBMODULES = {"schemas", "service", "models", "router"}


def check_module_boundaries(root_dir: Path) -> list[BoundaryViolation]:
    modules_dir = root_dir / "backend" / "app" / "modules"
    if not modules_dir.is_dir():
        # Fallback if run from backend directory
        modules_dir = root_dir / "app" / "modules"
    if not modules_dir.is_dir():
        raise FileNotFoundError(f"Could not locate modules directory from {root_dir}")

    violations: list[BoundaryViolation] = []

    for file_path in sorted(modules_dir.rglob("*.py")):
        rel_path = file_path.relative_to(modules_dir)
        if len(rel_path.parts) < 2:
            # Root file like app/modules/__init__.py
            continue

        source_module = rel_path.parts[0]

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        except SyntaxError as e:
            violations.append(
                BoundaryViolation(
                    file_path=file_path,
                    line=e.lineno or 1,
                    imported_target="",
                    rule="SyntaxError",
                    message=f"Failed to parse syntax: {e}",
                    allowed="Valid Python code",
                )
            )
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if not node.module or not node.module.startswith("app.modules."):
                    continue

                parts = node.module.split(".")
                # ['app', 'modules', '<target_module>', ...]
                if len(parts) < 3:
                    continue
                target_module = parts[2]

                if source_module == target_module:
                    # Intra-module import is always allowed
                    continue

                # EXCEPTION: ADR-001 reporting read-model aggregation exception
                if source_module == "reports":
                    continue

                # Rule 1 & Rule 2: No cross-module repository imports
                if "repository" in parts:
                    violations.append(
                        BoundaryViolation(
                            file_path=file_path,
                            line=node.lineno,
                            imported_target=node.module,
                            rule="Rule 1: Cross-Module Repository Forbidden",
                            message=(
                                f"Module '{source_module}' directly imports repository "
                                f"module '{node.module}' from module '{target_module}'."
                            ),
                            allowed=(
                                f"Import from public facade 'app.modules.{target_module}' "
                                f"or public service 'app.modules.{target_module}.service'"
                            ),
                        )
                    )
                    continue

                for alias in node.names:
                    if alias.name.endswith("Repository"):
                        violations.append(
                            BoundaryViolation(
                                file_path=file_path,
                                line=node.lineno,
                                imported_target=f"{node.module}.{alias.name}",
                                rule="Rule 2: Cross-Module Repository Access Forbidden",
                                message=(
                                    f"Module '{source_module}' imports repository symbol "
                                    f"'{alias.name}' from module '{target_module}'."
                                ),
                                allowed=(
                                    f"Consume public service '{target_module.capitalize()}Service' "
                                    f"instead of repository."
                                ),
                            )
                        )

                # Rule 3: Enforce public module boundary
                if len(parts) > 3:
                    submodule = parts[3]
                    if submodule not in ALLOWED_CROSS_MODULE_SUBMODULES:
                        violations.append(
                            BoundaryViolation(
                                file_path=file_path,
                                line=node.lineno,
                                imported_target=node.module,
                                rule="Rule 3: Internal Submodule Import Forbidden",
                                message=(
                                    f"Module '{source_module}' imports non-public internal submodule "
                                    f"'{node.module}'."
                                ),
                                allowed=(
                                    f"Import from public facade 'app.modules.{target_module}' or "
                                    f"allowed submodules: {', '.join(sorted(ALLOWED_CROSS_MODULE_SUBMODULES))}"
                                ),
                            )
                        )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if not alias.name.startswith("app.modules."):
                        continue
                    parts = alias.name.split(".")
                    if len(parts) >= 3:
                        target_module = parts[2]
                        if source_module != target_module and "repository" in parts:
                            if source_module == "reports":
                                continue
                            violations.append(
                                BoundaryViolation(
                                    file_path=file_path,
                                    line=node.lineno,
                                    imported_target=alias.name,
                                    rule="Rule 1: Cross-Module Repository Forbidden",
                                    message=(
                                        f"Module '{source_module}' imports repository "
                                        f"'{alias.name}'."
                                    ),
                                    allowed=f"Import from public facade 'app.modules.{target_module}'",
                                )
                            )

    return violations


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_module_boundaries(repo_root)

    if not violations:
        print("[PASS] Architectural module boundaries verified: 0 violations found.")
        print("       - No cross-module repository imports (ADR-001 reporting exception respected).")
        print("       - All inter-module imports consume public facades or allowed submodules.")
        return 0

    print(f"[FAIL] Architectural module boundary check failed: {len(violations)} violation(s) found:\n")
    for v in violations:
        try:
            rel = v.file_path.relative_to(repo_root)
        except ValueError:
            rel = v.file_path
        print(f"File: {rel}:{v.line}")
        print(f"  Rule:     {v.rule}")
        print(f"  Target:   {v.imported_target}")
        print(f"  Violation:{v.message}")
        print(f"  Allowed:  {v.allowed}\n")

    return 1


if __name__ == "__main__":
    sys.exit(main())
