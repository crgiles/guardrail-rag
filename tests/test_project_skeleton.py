from guardrail_rag import __version__
from guardrail_rag.settings import Settings


def test_package_version_and_default_settings():
    assert __version__ == "0.1.0"
    settings = Settings.from_env()
    assert settings.provider == "fake"
    assert settings.database_url.startswith("sqlite:")
