import subprocess
from pathlib import Path

import pytest

TEST_CONFIG = str(Path(__file__).parent / "test_files" / "generators_api.yml")


def test_directory_mode(tmp_path):
    config_dir = Path(__file__).parent / "test_files"
    subprocess.run(["haystack-pydoc", str(config_dir), str(tmp_path)], check=True)
    files = list(tmp_path.glob("*.md"))
    assert len(files) >= 1


def test_missing_arg():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(["haystack-pydoc"], capture_output=True, check=True)


def test_pydoc_markdown_alias(tmp_path):
    subprocess.run(["pydoc-markdown", TEST_CONFIG, str(tmp_path)], check=True)
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1


@pytest.mark.parametrize(
    "config", [TEST_CONFIG, str(Path(__file__).parent / "test_files" / "simpler_generators_api.yml")]
)
def test_output_matches_expected(tmp_path, config):
    subprocess.run(["haystack-pydoc", config, str(tmp_path)], check=True)
    content = (tmp_path / "generators_api.md").read_text()
    expected = (Path(__file__).parent / "test_files" / "expected_generators_api.md").read_text()
    assert content == expected
