from pathlib import Path

from griffe import Module, visit


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

    results: list[Module] = []
    for module_name in sorted(modules):
        filepath = root / module_name.replace(".", "/")
        if (filepath / "__init__.py").is_file():
            filepath = filepath / "__init__.py"
        else:
            filepath = filepath.with_suffix(".py")
        mod = visit(module_name, filepath=filepath, code=filepath.read_text(), docstring_parser="sphinx")
        results.append(mod)

    return results
