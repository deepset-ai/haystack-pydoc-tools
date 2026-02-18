import re
from pathlib import Path

import pytest

from haystack_pydoc_tools.loaders import load_modules
from haystack_pydoc_tools.renderers import render_docusaurus

TEST_COMPONENTS = str(Path(__file__).parent / "test_files" / "components" / "generators")


@pytest.fixture
def modules():
    return load_modules(TEST_COMPONENTS, ["chat/azure", "chat/openai"])


def test_render_to_file(tmp_path, modules):
    out = tmp_path / "out.md"
    render_docusaurus(modules, title="Generators", doc_id="gen-api", description="Desc", filename=str(out))
    content = out.read_text()
    assert content.startswith("---")
    assert 'title: "Generators"' in content
    assert "id: gen-api" in content


def test_adds_docusaurus_frontmatter(tmp_path, modules):
    out = tmp_path / "out.md"
    render_docusaurus(modules, title="Title", doc_id="my-id", description="My desc", filename=str(out))
    content = out.read_text()
    assert content.startswith("""---
title: "Title"
id: my-id
description: "My desc"
slug: "/my-id"
---
""")


def test_contains_class_docs(tmp_path, modules):
    out = tmp_path / "out.md"
    render_docusaurus(modules, title="T", doc_id="t", description="D", filename=str(out))
    content = out.read_text()
    assert "AzureOpenAIChatGenerator" in content
    assert "OpenAIChatGenerator" in content


def test_anchor_links_removed(tmp_path, modules):
    """Anchor-only links like [Foo](#bar) should be replaced with plain text."""
    out = tmp_path / "out.md"
    render_docusaurus(modules, title="T", doc_id="t", description="D", filename=str(out))
    content = out.read_text()
    # There should be no markdown links pointing to anchors
    assert not re.search(r"\[([^\]]+)\]\(#[^)]+\)", content)
