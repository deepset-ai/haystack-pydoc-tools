# haystack-pydoc-tools

[![PyPI - Version](https://img.shields.io/pypi/v/haystack-pydoc-tools.svg)](https://pypi.org/project/haystack-pydoc-tools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/haystack-pydoc-tools.svg)](https://pypi.org/project/haystack-pydoc-tools)

-----

**Table of Contents**

- [haystack-pydoc-tools](#haystack-pydoc-tools)
  - [Installation](#installation)
  - [License](#license)

## Installation

```console
pip install haystack-pydoc-tools
```

## License

`haystack-pydoc-tools` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

## Release process
To release version `x.y.z`:

1. Manually update the version in `src/haystack_pydoc_tools/__about__.py` (via a PR or a direct push to `main`).
2. From the `main` branch, create a tag locally: `git tag vx.y.z`.
3. Push the tag: `git push --tags`.
4. Wait for the CI to release the package on PyPI.
