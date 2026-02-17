import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import yaml

from haystack_pydoc_tools.loaders import load_modules
from haystack_pydoc_tools.renderers import render_docusaurus


def process_config(config_path: str, output_dir: str | None = None) -> None:
    """Process a single YAML config file and generate Markdown API references."""
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Resolve search_path relative to the config file's directory
    config_dir = Path(config_path).resolve().parent
    loader_config = config["loaders"][0]
    search_path = str((config_dir / loader_config["search_path"][0]).resolve())

    modules = load_modules(search_path, loader_config["modules"])

    # Extract renderer config
    renderer_config = config["renderer"]
    filename = renderer_config.get("filename") or renderer_config["markdown"]["filename"]

    if output_dir:
        filename = str(Path(output_dir) / Path(filename).name)

    # Extract processor settings
    show_if_no_docstring = False
    skip_empty_modules = True
    for proc in config.get("processors", []):
        if proc.get("type", "filter") == "filter":
            if "documented_only" in proc:
                show_if_no_docstring = not proc["documented_only"]
            if "skip_empty_modules" in proc:
                skip_empty_modules = proc["skip_empty_modules"]

    render_docusaurus(
        modules,
        title=renderer_config["title"],
        doc_id=renderer_config["id"],
        description=renderer_config["description"],
        filename=filename,
        show_if_no_docstring=show_if_no_docstring,
        skip_empty_modules=skip_empty_modules,
    )


def main() -> None:
    """CLI entry point: reads a YAML config (or directory of configs) and generates Markdown API docs."""

    if len(sys.argv) < 2:  # noqa: PLR2004
        print("Usage: haystack-pydoc <config.yml | config-directory> [output-directory]", file=sys.stderr)
        sys.exit(1)

    target = Path(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None  # noqa: PLR2004

    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    if target.is_dir():
        configs = sorted(target.glob("*.yml"))
        if not configs:
            print(f"No .yml files found in {target}", file=sys.stderr)
            sys.exit(1)

        errors: list[tuple[str, Exception]] = []
        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(process_config, str(cfg), output_dir): cfg for cfg in configs}
            for future in as_completed(futures):
                cfg = futures[future]
                try:
                    future.result()
                    print(f"  OK: {cfg.name}")
                except Exception as exc:  # noqa: BLE001
                    errors.append((cfg.name, exc))
                    print(f"  FAIL: {cfg.name}: {exc}", file=sys.stderr)

        if errors:
            print(f"\n{len(errors)} config(s) failed.", file=sys.stderr)
            sys.exit(1)
    else:
        process_config(str(target), output_dir)


if __name__ == "__main__":
    main()
