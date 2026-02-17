import re
from pathlib import Path

from griffe import Module
from griffe2md import render_object_docs

GRIFFE2MD_DEFAULT_CONFIG = {
    # Heading structure
    "heading_level": 2,
    "show_root_heading": True,
    "show_root_full_path": True,
    "show_root_members_full_path": False,
    "show_object_full_path": False,
    # Signatures
    "separate_signature": True,
    "show_signature": True,
    "show_signature_annotations": True,
    "signature_crossrefs": False,
    "line_length": 80,
    # Members
    "merge_init_into_class": False,
    "inherited_members": True,
    "filters": ["!^_", "^__init__$"],
    "members": None,
    "members_order": "source",
    "group_by_category": False,
    "show_submodules": False,
    "show_bases": True,
    "show_category_heading": False,
    # Docstring rendering
    "docstring_section_style": "list",
    "show_docstring_attributes": True,
    "show_docstring_description": True,
    "show_docstring_examples": True,
    "show_docstring_other_parameters": True,
    "show_docstring_parameters": True,
    "show_docstring_raises": True,
    "show_docstring_receives": True,
    "show_docstring_returns": True,
    "show_docstring_warns": True,
    "show_docstring_yields": True,
    "show_docstring_classes": True,
    "show_docstring_functions": True,
    "show_docstring_modules": True,
    # Display
    "show_if_no_docstring": False,
    "summary": False,
    "annotations_path": "brief",
}

DOCUSAURUS_FRONTMATTER = """---
title: "{title}"
id: {id}
description: "{description}"
slug: "/{id}"
---

"""

ANCHOR_LINK_RE = re.compile(r"\[([^\]]+)\]\(#[^)]+\)")


def render_docusaurus(  # noqa: PLR0913
    modules: list[Module],
    *,
    title: str,
    doc_id: str,
    description: str,
    filename: str,
    show_if_no_docstring: bool = False,
    skip_empty_modules: bool = True,
) -> None:
    """Render griffe modules to Docusaurus-compatible Markdown and write to file."""
    config = {**GRIFFE2MD_DEFAULT_CONFIG, "show_if_no_docstring": show_if_no_docstring}

    parts = [DOCUSAURUS_FRONTMATTER.format(title=title, id=doc_id, description=description)]

    for module in modules:
        rendered = render_object_docs(module, config, format_md=True)
        if rendered.strip() or not skip_empty_modules:
            parts.append(rendered)

    output = "\n".join(parts)

    # Remove anchor-only markdown links (not proper URLs)
    output = ANCHOR_LINK_RE.sub(r"\1", output)

    Path(filename).write_text(output, encoding="utf-8")
