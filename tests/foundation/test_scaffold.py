from importlib import import_module
from sys import version_info

PROJECT_PACKAGES = (
    "src",
    "src.accounting",
    "src.api",
    "src.backtest",
    "src.config",
    "src.data",
    "src.domain",
    "src.execution",
    "src.features",
    "src.monitoring",
    "src.portfolio",
    "src.risk",
    "src.runtime",
    "src.strategies",
    "scripts",
)


def test_python_runtime_is_312() -> None:
    assert version_info >= (3, 12)
    assert version_info < (3, 13)


def test_project_package_scaffold_imports() -> None:
    for package in PROJECT_PACKAGES:
        import_module(package)
