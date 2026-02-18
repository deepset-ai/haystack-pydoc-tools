from pathlib import Path

import griffe

from haystack_pydoc_tools.loaders import load_modules

TEST_FILES = Path(__file__).parent / "test_files"
TEST_COMPONENTS = str(TEST_FILES / "components" / "generators")
TEST_DATACLASSES = str(TEST_FILES)


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


def test_load_namespace_package():
    # here dataclasses folder is a namespace package because it doesn't have an __init__.py
    modules = load_modules(TEST_DATACLASSES, ["dataclasses.byte_stream"])
    assert len(modules) == 1
    assert isinstance(modules[0], griffe.Module)
    assert "ByteStream" in [m.name for m in modules[0].members.values()]


def test_dataclass_init_synthesized():
    modules = load_modules(TEST_DATACLASSES, ["dataclasses.byte_stream"])
    cls = modules[0].members["ByteStream"]

    assert "__init__" in cls.members
    init = cls.members["__init__"]
    param_names = [p.name for p in init.parameters]
    assert param_names == ["self", "data", "meta", "mime_type"]
