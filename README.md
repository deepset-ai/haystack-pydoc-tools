# haystack-pydoc-tools

[![PyPI - Version](https://img.shields.io/pypi/v/haystack-pydoc-tools.svg)](https://pypi.org/project/haystack-pydoc-tools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/haystack-pydoc-tools.svg)](https://pypi.org/project/haystack-pydoc-tools)

-----

Tool to generate Docusaurus-compatible Markdown API references from Python docstrings.
It uses [griffe](https://github.com/mkdocstrings/griffe) to parse source code and [griffe2md](https://github.com/mkdocstrings/griffe2md) to render the output.

## Installation

```console
pip install haystack-pydoc-tools
```

## Usage

The tool reads YAML configuration files and generates Markdown API docs.

**Process a single config file:**

```console
haystack-pydoc config.yml [output-directory]
```

**Process a directory of config files (in parallel):**

```console
haystack-pydoc pydoc/ output/
```

A `pydoc-markdown` alias is also available for backward compatibility.

### Output behavior

Each config must specify a `filename`.
By default, the file is written in the current working directory; if an output directory
is provided, the file is written there instead.

## Configuration

Each `.yml` file describes which modules to document and how to render the output.

### Minimal example

```yaml
loaders:
  - search_path: [src]
    modules:
      - haystack.components.generators.chat.openai
      - haystack.components.generators.chat.azure
renderer:
  title: Generators
  id: generators-api
  description: Enables text generation using LLMs.
  filename: generators_api.md
```

### Full example

```yaml
loaders:
  - search_path: [../src]
    modules:
      - haystack.components.generators.chat.openai
      - haystack.components.generators.chat.azure
processors:
  - type: filter
    documented_only: false    # include objects without docstrings
    skip_empty_modules: false  # keep modules even if they have no content
renderer:
  title: Generators API
  id: generators-api
  description: Enables text generation using LLMs.
  filename: generators_api.md
```

When the `processors` section is omitted, defaults apply: `documented_only: true`, `skip_empty_modules: true`.

### Legacy example

The tool also accepts the older `pydoc-markdown`-style configs. Most fields are ignored but don't cause errors.

```yaml
loaders:
  - type: haystack_pydoc_tools.loaders.CustomPythonLoader  # ignored
    search_path: [../src]
    modules:
      - haystack.components.generators.chat.openai
      - haystack.components.generators.chat.azure
    ignore_when_discovered: ["__init__"]  # ignored
processors:
  - type: filter
    expression:              # ignored
    documented_only: true
    do_not_filter_modules: false  # ignored
    skip_empty_modules: true
  - type: smart    # ignored
  - type: crossref  # ignored
renderer:
  type: haystack_pydoc_tools.renderers.DocusaurusRenderer  # ignored
  title: Generators API
  id: generators-api
  description: Enables text generation using LLMs.
  markdown:
    descriptive_class_title: false   # ignored
    classdef_code_block: false       # ignored
    descriptive_module_title: true   # ignored
    add_method_class_prefix: true    # ignored
    add_member_class_prefix: false   # ignored
    filename: generators_api.md
```

## License

`haystack-pydoc-tools` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

## Release process

To release version `x.y.z`:

1. Manually update the version in `src/haystack_pydoc_tools/__about__.py` (via a PR or a direct push to `main`).
2. From the `main` branch, create a tag locally: `git tag vx.y.z`.
3. Push the tag: `git push --tags`.
4. Wait for the CI to release the package on PyPI.
