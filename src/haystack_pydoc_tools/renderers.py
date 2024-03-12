import base64
import dataclasses
import os
import subprocess
import sys
import typing as t
import warnings
from pathlib import Path
from typing import List, Optional

import docspec
import requests
from packaging.version import Version
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer

README_FRONTMATTER = """---
title: {title}
excerpt: {excerpt}
category: {category}
slug: {slug}
parentDoc: {parent_doc}
order: {order}
hidden: false
---

"""


def create_headers(version: str):
    # Utility function to create Readme.io headers.
    # We assume the README_API_KEY env var is set since we check outside
    # to show clearer error messages.
    api_key = os.getenv("README_API_KEY")
    token = base64.b64encode(f"{api_key}:".encode()).decode()
    return {"authorization": f"Basic {token}", "x-readme-version": version}


@dataclasses.dataclass
class ReadmeRenderer(Renderer):
    """
    This custom Renderer is heavily based on the `MarkdownRenderer`,
    it just prepends a front matter so that the output can be published
    directly to readme.io.
    """

    # These settings will be used in the front matter output
    title: str
    category_slug: str
    excerpt: str
    slug: str
    order: int
    parent_doc_slug: str = ""
    # Docs categories fetched from Readme.io
    categories: t.Dict[str, str] = dataclasses.field(init=False)
    # This exposes a special `markdown` settings value that can be used to pass
    # parameters to the underlying `MarkdownRenderer`
    markdown: MarkdownRenderer = dataclasses.field(default_factory=MarkdownRenderer)

    def init(self, context: Context) -> None:
        self.markdown.init(context)
        self.version = self._doc_version()
        self.categories = self._readme_categories(self.version)

    def _doc_version(self) -> str:
        """
        Returns the docs version.
        """
        root = Path(__file__).absolute().parent.parent.parent
        full_version = (root / "VERSION.txt").read_text()
        major, minor = full_version.split(".")[:2]
        if "rc0" in full_version:
            return f"v{major}.{minor}-unstable"
        return f"v{major}.{minor}"

    def _readme_categories(self, version: str) -> t.Dict[str, str]:
        """
        Fetch the categories of the given version from Readme.io.
        README_API_KEY env var must be set to correctly get the categories.
        Returns dictionary containing all the categories slugs and their ids.
        """
        api_key = os.getenv("README_API_KEY")
        if not api_key:
            warnings.warn("README_API_KEY env var is not set, using a placeholder category ID", stacklevel=2)
            return {}

        headers = create_headers(version)

        res = requests.get("https://dash.readme.com/api/v1/categories?perPage=100", headers=headers, timeout=60)

        if not res.ok:
            sys.exit(f"Error requesting {version} categories")

        return {c["slug"]: c["id"] for c in res.json()}

    def _doc_id(self, doc_slug: str, version: str) -> str:
        """
        Fetch the doc id of the given doc slug and version from Readme.io.
        README_API_KEY env var must be set to correctly get the id.
        If doc_slug is an empty string return an empty string.
        """
        if not doc_slug:
            # Not all docs have a parent doc, in case we get no slug
            # we just return an empty string.
            return ""

        api_key = os.getenv("README_API_KEY")
        if not api_key:
            warnings.warn("README_API_KEY env var is not set, using a placeholder doc ID", stacklevel=2)
            return "fake-doc-id"

        headers = create_headers(version)
        res = requests.get(f"https://dash.readme.com/api/v1/docs/{doc_slug}", headers=headers, timeout=60)
        if not res.ok:
            sys.exit(f"Error requesting {doc_slug} doc for version {version}")

        return res.json()["id"]

    def render(self, modules: t.List[docspec.Module]) -> None:
        if self.markdown.filename is None:
            sys.stdout.write(self._frontmatter())
            self.markdown.render_single_page(sys.stdout, modules)
        else:
            with open(self.markdown.filename, "w", encoding=self.markdown.encoding) as fp:
                fp.write(self._frontmatter())
                self.markdown.render_single_page(t.cast(t.TextIO, fp), modules)

    def _frontmatter(self) -> str:
        return README_FRONTMATTER.format(
            title=self.title,
            category=self.categories.get(self.category_slug, f"placeholder-{self.category_slug}"),
            parent_doc=self._doc_id(self.parent_doc_slug, self.version),
            excerpt=self.excerpt,
            slug=self.slug,
            order=self.order,
        )


@dataclasses.dataclass
class ReadmePreviewRenderer(ReadmeRenderer):
    """
    This custom Renderer behaves just like the ReadmeRenderer but renders docs with the hardcoded
    version 2.0 to generate correct category ids.
    """

    def _doc_version(self) -> str:
        """
        Returns the hardcoded docs version 2.0.
        """
        return "v2.0"


@dataclasses.dataclass
class ReadmeCoreRenderer(ReadmeRenderer):
    """
    This custom Renderer behaves just like the ReadmeRenderer but gets the version from `hatch`.
    This is meant to be used by the Haystack core repository.
    """

    def _doc_version(self) -> str:
        """
        Returns the docs version.
        """
        # We're assuming hatch is installed and working
        res = subprocess.run(["hatch", "version"], capture_output=True, check=True)
        res.check_returncode()
        full_version = res.stdout.decode().strip()
        major, minor = full_version.split(".")[:2]
        if "rc0" in full_version:
            return f"v{major}.{minor}-unstable"
        return f"v{major}.{minor}"


@dataclasses.dataclass
class ReadmeIntegrationRenderer(ReadmeRenderer):
    """
    This custom Renderer behaves just like the ReadmeRenderer but get the latest stable Haystack version released.
    This is meant to be used by the Haystack integration repository.
    """

    def _get_latest_stable_version(self, versions: List[Version]) -> Optional[Version]:
        latest_version = None
        for version in versions:
            if version.pre or version.dev:
                # Skip pre-releases, we only want stable ones
                continue
            if latest_version is None or version > latest_version:
                latest_version = version
        return latest_version

    def _doc_version(self) -> str:
        """
        Returns the docs version.
        """
        # Get the Haystack data from PyPI
        res = requests.get(
            "https://pypi.org/simple/haystack-ai",
            headers={"Accept": "application/vnd.pypi.simple.v1+json"},
            timeout=30,
        )
        res.raise_for_status()

        data = res.json()
        versions = [Version(v) for v in data["versions"]]

        latest_version = self._get_latest_stable_version(versions)
        if latest_version is None:
            msg = "No stable version found"
            raise ValueError(msg)

        major, minor = latest_version.major, latest_version.minor
        return f"v{major}.{minor}"
