import os
import pytest
import logging

import Forestry.core.settings as settings

class TestFallbackSetting(object):
    def test_has_env_var_property(self):
        setting = settings.FallbackSetting("monty", env_var="Forestry_MONTY")
        assert setting.env_var == "Forestry_MONTY"

    def test_has_env_var(self):
        os.environ["Forestry_MONTY"] = "30"
        setting = settings.FallbackSetting("monty", env_var="Forestry_MONTY")
        assert setting() == "30"
        del os.environ["Forestry_MONTY"] # cleanup

    def test_throwing_when_has_nothing(self):
        setting = settings.FallbackSetting("monty")
        with pytest.raises(RuntimeError):
            setting()

    def test_has_default(self):
        setting = settings.FallbackSetting("monty", default=10)
        assert setting() == 10

    def test_has_default_mapping(self):
        setting = settings.FallbackSetting("monty", mapper=int, default="10")
        assert setting() == 10

    def test_has_getter(self):
        setting = settings.FallbackSetting("monty", getter=lambda: 20)
        assert setting() == 20

    def test_has_getter_mapping(self):
        setting = settings.FallbackSetting("monty", mapper=int, getter=lambda: "20")
        assert setting() == 20

    def test_set(self):
        setting = settings.FallbackSetting("monty")
        setting.set_value(40)
        assert setting() == 40

    def test_unset(self):
        setting = settings.FallbackSetting("monty", default=2)
        setting.set_value(40)
        assert setting() == 40
        setting.unset_value()
        assert setting() == 2

    def test_calling_mapping(self):
        setting = settings.FallbackSetting("monty", mapper=int)
        assert setting("50") == 50

    def test_fallback(self):
        # Default
        setting = settings.FallbackSetting("monty", env_var="Forestry_MONTY", mapper=int, default=10)
        assert setting() == 10

        # Getter
        setting = settings.FallbackSetting("monty", env_var="Forestry_MONTY", mapper=int, default=10, getter=lambda: 20)
        assert setting() == 20

        # Environment variable
        os.environ["Forestry_MONTY"] = "30"
        assert setting() == 30

        # Explicitly set value
        setting.set_value(40)
        assert setting() == 40

        # Calling value
        assert setting(50) == 50

        del os.environ["Forestry_MONTY"]


class TestSettings(object):
    def test_set_single_config(self):
        values = settings.shared.config(monty=10)
        assert values.monty == 10

    def test_set_multiple_config(self):
        values = settings.shared.config(monty=10, python="gary")
        assert values.monty == 10
        assert values.python == "gary"
        assert len(values._fields) == 3  # with log_level

    def test_immutable_config(self):
        values = settings.shared.config(monty=10)
        with pytest.raises(AttributeError):
            values.monty = 20

    def test_environment_fallback(self):
        os.environ["Forestry_LOG_LEVEL"] = "DEBUG"
        values = settings.shared.config()
        assert values.log_level == logging.DEBUG
        del os.environ["Forestry_LOG_LEVEL"]

    def test_defaults(self):
        values = settings.shared.defaults
        assert values.log_level == logging.INFO
        

class TestMappers(object):
    @pytest.mark.parametrize("value", ["Yes", "YES", "yes", "1", "ON", "on", "true", "True", True])
    def test_to_positive_bool(self, value):
        assert settings.to_bool(value)

    @pytest.mark.parametrize("value", ["No", "NO", "no", "0", "OFF", "off", "false", "False", False])
    def test_to_negative_bool(self, value):
        assert not settings.to_bool(value)

    @pytest.mark.parametrize("value", [True, False])
    def test_to_literal_bool_(self, value):
        assert settings.to_bool(value) == value

    def test_to_throwing_bool(self):
        with pytest.raises(ValueError):
            settings.to_bool("junk")