from pathlib import Path

from griffe import Module, load


def load_modules(search_path: str, modules: list[str]) -> list[Module]:
    """
    Load Python modules using griffe.

    :param search_path: Filesystem path to a subpackage directory (e.g. ".../haystack/components/generators").
    :param modules: Module names as slash-separated paths relative to search_path (e.g. "chat/azure").
    :returns: Loaded griffe Module objects, in alphabetical order.
    """
    # griffe.load() needs a fully-qualified dotted name and a search path to the top-level package.
    # Walk up through __init__.py parents to find the package root.
    resolved = Path(search_path).resolve()
    package_root = resolved
    while (package_root.parent / "__init__.py").exists():
        package_root = package_root.parent
    package_root = package_root.parent
    base_package = ".".join(resolved.relative_to(package_root).parts)

    results: list[Module] = []
    for module_name in sorted(modules):
        dotted_name = module_name.replace("/", ".")
        full_module = f"{base_package}.{dotted_name}"
        mod = load(full_module, search_paths=[str(package_root)], docstring_parser="sphinx")
        results.append(mod)

    return results
