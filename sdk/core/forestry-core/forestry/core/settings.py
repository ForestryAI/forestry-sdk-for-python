from typing import Any, Tuple, TypeVar, Optional, Callable, Union, Generic, List, Mapping
from enum import Enum
import os
from collections import namedtuple
import logging


# https://www.python.org/dev/peps/pep-0484/#support-for-singleton-types-in-unions
class _Nothing(Enum):
    token = 0

_nothing = _Nothing.token


def to_bool(value: Union[str, bool]) -> bool:
    """Maps strings to either True or False.

    If a boolean is passed in, it is returned as-is. Otherwise the function
    maps the following strings, ignoring case:

    * "yes", "1", "on" -> True
    " "no", "0", "off" -> False

    :param value: the value to map
    :type value: str or bool
    :returns: A boolean value matching the intent of the input
    :rtype: bool
    :raises ValueError: When mapping to bool fails

    """
    if isinstance(value, bool):
        return value
    val = value.lower()
    if val in ["yes", "1", "on", "true", "True"]:
        return True
    if val in ["no", "0", "off", "false", "False"]:
        return False
    raise ValueError("Unable to map {} as boolean value".format(value))


_logging_named_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}

def to_logging_level(value: Union[str, int]) -> int:
    if isinstance(value, int):
        # Fast return of level because customs are allowed:
        # https://docs.python.org/3/library/logging.html#levels
        return value
    val = value.upper()
    level = _logging_named_levels.get(val)
    if not level:
        raise ValueError("Unable to map {} to log named level, from: {}".format(value, ", ".join(_logging_named_levels)))
    return level


FromType = TypeVar("FromType")
ToType = TypeVar("ToType")

class FallbackSetting(Generic[FromType, ToType]):
    """Setting with fallback precedence:

    1. value when calling
    2. value when explicitly set
    3. environment variable
    4. getter
    5. default value

    Each fallback value is mapped either with an optional mapper or an identity mapper.

    :param str name: the name of the setting.
    :param str env_var: the name of an environment variable.
    :param callable getter: getter delegate.
    :param default: default value.
    :param callable mapper: mapping function from FromType to ToType.
    """
    def __init__(
        self,
        name: str,
        env_var: Optional[str] = None,
        getter: Optional[Callable[[], FromType]] = None,
        default: Union[FromType, _Nothing] = _nothing,
        mapper: Optional[Callable[[Union[FromType, str]], ToType]] = None,
    ):
        self_mapper: Callable[[Any], Any] = lambda x: x

        self._name = name
        self._env_var = env_var
        self._getter = getter
        self._default = default        
        self._mapper: Callable[[Union[FromType, str]], ToType] = mapper if mapper else self_mapper
        self._set_value: Union[FromType, _Nothing] = _nothing

    def __repr__(self) -> str:
        return "FallbackSetting(%r)" % self._name

    def __call__(self, value: Optional[FromType] = None) -> ToType:
        """Return the setting by fallback precedence.

        :param value: value
        :type value: str or int or float or None
        :returns: the value of the setting
        :rtype: str or int or float
        :raises RuntimeError: if no value can be determined
        """

        # 1. when calling value
        if value is not None:
            return self._mapper(value)

        # 2. when set value
        if not isinstance(self._set_value, _Nothing):
            return self._mapper(self._set_value)

        # 3. environment variable
        if self._env_var and self._env_var in os.environ:
            return self._mapper(os.environ[self._env_var])

        # 4. getter
        if self._getter:
            return self._mapper(self._getter())

        # 5. default
        if not isinstance(self._default, _Nothing):
            return self._mapper(self._default)

        raise RuntimeError("Unable to get setting %r" % self._name)

    def __get__(self, instance: Any, owner: Optional[Any] = None) -> 'FallbackSetting[FromType, ToType]':
        return self

    def __set__(self, instance: Any, value: FromType) -> None:
        self.set_value(value)

    def set_value(self, value: FromType) -> None:
        """Explicitly set value

        :param value: explicit set value
        :type value: str or int or float
        """
        self._set_value = value

    def unset_value(self) -> None:
        """Unset explicitly set value."""
        self._set_value = _nothing

    @property
    def env_var(self) -> Optional[str]:
        return self._env_var

    @property
    def default(self) -> Union[FromType, _Nothing]:
        return self._default
    

class Settings:
    """Settings used by Forestry configurations.
    
    ... code-block:: python
    
        from Forestry.core.settings import settings
        
        settings.log_level = "DEBUG"

        Settings precedence:

        1. value when calling
        2. value when explicitly set
        3. environment variable
        4. getter
        5. default value
    """

    def __init__(self) -> None:
        """Sets defaults only as False"""
        self._defaults_only: bool = False

    @property
    def defaults_only(self) -> bool:
        """Returns defaults only flag"""
        return self._defaults_only

    @property
    def current(self) -> Tuple[Any, ...]:
        """Returns only default settings or all settings with defaults as an immutable Tuple with settings as attributes"""
        if self.defaults_only:
            return self.defaults
        return self.config()
    
    @defaults_only.setter
    def defaults_only(self, value: bool) -> None:
        """Effects current property to only return default settings."""
        self._defaults_only = value

    @property
    def defaults(self) -> Tuple[Any, ...]:
        """Returns from default settings as an immutable Tuple with settings as attributes"""
        props = {k: v.default for (k, v) in self.__class__.__dict__.items() if isinstance(v, FallbackSetting)}
        return self._config(props)
    
    def config(self, **kwargs: Any) -> Tuple[Any, ...]:
        """Returns from default settings with passed dictionary as an immutable Tuple with settings as attributes"""
        props = {k: v() for (k, v) in self.__class__.__dict__.items() if isinstance(v, FallbackSetting)}
        props.update(kwargs)
        return self._config(props)    

    def _config(self, props: Mapping[str, Any]) -> Tuple[Any, ...]:
        """Returns an immutable Tuple with settings as attributes"""
        keys: List[str] = list(props.keys())

        Config = namedtuple("Config", keys)  # type: ignore
        return Config(**props)
    
    log_level: FallbackSetting[Union[str, int], int] = FallbackSetting(
        "log_level",
        env_var="Forestry_LOG_LEVEL",
        mapper=to_logging_level,
        default=logging.INFO,
    )


shared: Settings = Settings()
"""Shared singleton Settings.

:type shared: Settings
"""


__all__ = ("shared", "Settings")
