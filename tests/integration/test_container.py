"""Container smoke tests are exercised by the CI Docker job."""

from pathlib import Path


def test_container_files_exist():
    """Keep the container deployment files present in the repository."""
    root = Path(__file__).parents[2]
    assert (root / "Dockerfile").is_file()
    assert (root / "docker-compose.yml").is_file()
