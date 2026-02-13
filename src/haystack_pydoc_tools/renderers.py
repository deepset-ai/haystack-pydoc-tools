import dataclasses
import sys
import typing as t

import docspec
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer

DOCUSAURUS_FRONTMATTER = """---
title: "{title}"
id: {id}
description: "{description}"
slug: "/{id}"
---

"""


@dataclasses.dataclass
class DocusaurusRenderer(Renderer):
    """
    This custom Renderer is heavily based on the `MarkdownRenderer`.

    It just prepends a front matter so that the output can be published
    directly to docusaurus.
    """

    # These settings will be used in the front matter output
    title: str
    id: str
    description: str

    # This exposes a special `markdown` settings value that can be used to pass
    # parameters to the underlying `MarkdownRenderer`
    markdown: MarkdownRenderer = dataclasses.field(default_factory=MarkdownRenderer)

    def init(self, context: Context) -> None:  # noqa: D102
        # Set fixed header levels for Docusaurus (downgrade all headings by +1)
        # This ensures Module starts at h2, Class at h3, Method/Function at h4
        self.markdown.use_fixed_header_levels = True
        self.markdown.header_level_by_type = {"Module": 2, "Class": 3, "Method": 4, "Function": 4, "Data": 4}
        self.markdown.init(context)

    def render(self, modules: t.List[docspec.Module]) -> None:  # noqa: D102
        if self.markdown.filename is None:
            sys.stdout.write(self._frontmatter())
            self.markdown.render_single_page(sys.stdout, modules)
        else:
            with open(self.markdown.filename, "w", encoding=self.markdown.encoding) as fp:
                fp.write(self._frontmatter())
                self.markdown.render_single_page(t.cast(t.TextIO, fp), modules)

    def _frontmatter(self) -> str:
        return DOCUSAURUS_FRONTMATTER.format(title=self.title, id=self.id, description=self.description)
