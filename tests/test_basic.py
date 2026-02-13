import os
import subprocess

import pytest


@pytest.fixture
def cleanup_files():
    yield

    if os.path.exists("preprocessors_api.md"):
        os.remove("preprocessors_api.md")


def test_can_build_preprocessors_api(cleanup_files):
    subprocess.run(["pydoc-markdown", "tests/test_files/preprocessors_api.yml"], check=True)

    assert os.path.exists("preprocessors_api.md")

    with open("preprocessors_api.md", "r") as f:
        content = f.read()

    with open("tests/test_files/preprocessors_api_output.md", "r") as f:
        expected_content = f.read()

    assert content == expected_content
