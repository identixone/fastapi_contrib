def test_settings_from_env_and_defaults():
    from fastapi_contrib.conf import settings
    assert settings.fastapi_app == "tests.conftest.app"
    assert settings.now_function is None
    assert settings.Config.secrets_dir == "/tmp/secrets"
    assert settings.jaeger_sampler_rate == 0.1
