from pathlib import Path
from typing import Any

from griffe import DataclassesExtension, Extension, Extensions, Module, visit


class DataclassesVisitorExtension(Extension):
    """
    Synthesize __init__ for dataclasses when using visit().

    griffe's built-in DataclassesExtension only hooks on_package (loader), so it doesn't run with visit().
    This extension hooks on_module_members (called by the visitor) and delegates to the same logic.
    """

    def __init__(self) -> None:
        self._inner = DataclassesExtension()

    def on_module_members(self, *, mod: Module, **kwargs: Any) -> None:  # noqa: ARG002, D102
        self._inner.on_package(pkg=mod)


def load_modules(search_path: str, modules: list[str]) -> list[Module]:
    """
    Load Python modules using griffe.

    Uses griffe.visit() to parse source files directly, which also works with namespace packages
    (such as Haystack Core Integrations).

    :param search_path: Filesystem path to the source root (e.g. "../src").
    :param modules: Fully-qualified dotted module names.
    :returns: Loaded griffe Module objects, in alphabetical order.
    """
    root = Path(search_path).resolve()
    extensions = Extensions(DataclassesVisitorExtension())

    results: list[Module] = []
    for module_name in sorted(modules):
        filepath = root / module_name.replace(".", "/")
        if (filepath / "__init__.py").is_file():
            filepath = filepath / "__init__.py"
        else:
            filepath = filepath.with_suffix(".py")
        mod = visit(
            module_name, filepath=filepath, code=filepath.read_text(), docstring_parser="sphinx", extensions=extensions
        )
        results.append(mod)

    return results
