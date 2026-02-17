from pathlib import Path

import griffe

from haystack_pydoc_tools.loaders import load_modules

TEST_COMPONENTS = str(Path(__file__).parent / "test_files" / "components" / "generators")


def test_load_single_module():
    modules = load_modules(TEST_COMPONENTS, ["chat/openai"])
    assert len(modules) == 1
    assert isinstance(modules[0], griffe.Module)


def test_load_multiple_modules():
    modules = load_modules(TEST_COMPONENTS, ["chat/azure", "chat/openai"])
    assert len(modules) == 2  # noqa: PLR2004


def test_load_sorts_alphabetically():
    modules = load_modules(TEST_COMPONENTS, ["chat/openai", "chat/azure"])
    assert "azure" in modules[0].name
    assert "openai" in modules[1].name


def test_loaded_module_has_members_and_sections():
    modules = load_modules(TEST_COMPONENTS, ["chat/openai"])
    member_names = [m.name for m in modules[0].members.values()]
    assert "OpenAIChatGenerator" in member_names

    module = modules[0].members["OpenAIChatGenerator"]
    init = module.members["__init__"]
    section_kinds = [s.kind.value for s in init.docstring.parsed]
    assert "parameters" in section_kinds
