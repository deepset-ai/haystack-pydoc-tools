import os
import subprocess

import pytest


@pytest.fixture
def cleanup_files():
    yield

    if os.path.exists("generators_api.md"):
        os.remove("generators_api.md")


def test_can_build_preprocessors_api(cleanup_files):
    subprocess.run(["pydoc-markdown", "tests/test_files/generators_api.yml"], check=True)

    assert os.path.exists("generators_api.md")

    with open("generators_api.md", "r") as f:
        content = f.read()

    with open("tests/test_files/expected_generators_api.md", "r") as f:
        expected_content = f.read()

    assert content == expected_content
