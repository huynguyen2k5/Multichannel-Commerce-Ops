import sys
from pathlib import Path

# Add scripts directory to path to import boundary checker
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root / "scripts"))

from check_module_boundaries import (  # noqa: E402  # pyright: ignore [reportMissingImports]
    check_module_boundaries,
)


def test_actual_codebase_has_zero_boundary_violations() -> None:
    violations = check_module_boundaries(repo_root)
    assert violations == [], f"Expected 0 architectural violations, but got: {violations}"


def test_boundary_checker_flags_cross_module_repository_import(tmp_path: Path) -> None:
    modules_dir = tmp_path / "app" / "modules"
    orders_dir = modules_dir / "orders"
    orders_dir.mkdir(parents=True)

    illegal_code = "from app.modules.inventory.repository import InventoryRepository\n"
    (orders_dir / "service.py").write_text(illegal_code, encoding="utf-8")

    violations = check_module_boundaries(tmp_path)
    assert len(violations) == 1
    assert "Rule 1" in violations[0].rule
    assert "directly imports repository module" in violations[0].message


def test_boundary_checker_flags_cross_module_repository_symbol_import(tmp_path: Path) -> None:
    modules_dir = tmp_path / "app" / "modules"
    orders_dir = modules_dir / "orders"
    orders_dir.mkdir(parents=True)

    illegal_code = "from app.modules.channels import ChannelRepository\n"
    (orders_dir / "service.py").write_text(illegal_code, encoding="utf-8")

    violations = check_module_boundaries(tmp_path)
    assert len(violations) == 1
    assert "Rule 2" in violations[0].rule
    assert "ChannelRepository" in violations[0].imported_target


def test_boundary_checker_allows_reports_aggregation_exception(tmp_path: Path) -> None:
    modules_dir = tmp_path / "app" / "modules"
    reports_dir = modules_dir / "reports"
    reports_dir.mkdir(parents=True)

    allowed_exception_code = (
        "from app.modules.orders.models import Order\n"
        "from app.modules.channels.models import Channel\n"
        "from app.modules.ledger.repository import LedgerRepository\n"
    )
    (reports_dir / "repository.py").write_text(allowed_exception_code, encoding="utf-8")

    violations = check_module_boundaries(tmp_path)
    assert violations == []


def test_boundary_checker_flags_forbidden_submodule(tmp_path: Path) -> None:
    modules_dir = tmp_path / "app" / "modules"
    orders_dir = modules_dir / "orders"
    orders_dir.mkdir(parents=True)

    illegal_submodule = "from app.modules.inventory.internal_impl import SecretHelper\n"
    (orders_dir / "service.py").write_text(illegal_submodule, encoding="utf-8")

    violations = check_module_boundaries(tmp_path)
    assert len(violations) == 1
    assert "Rule 3" in violations[0].rule
    assert "internal submodule" in violations[0].message
