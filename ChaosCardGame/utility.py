import os
import pygame
from functools import wraps

cwd_path = os.path.dirname(os.path.abspath(__file__))


def value_parser(value: str) -> int | float | bool | str | None:
    if len(value) == 0:
        return None
    if value[0] == value[-1] == '"':
        return value[1:-1]  # no strip after as spaces may be intentional
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "none":
        return None
    if isintstr(value):
        # Note: doesn't support negative numbers (should be fixed)
        return int(value)
    if isfloatstr(value):
        return float(value)
    # technically valid string option even without "": they are only needed for numeric values (e.g. "1", "true") or to have unstriped strings (e.g. "foo ")
    return value


def search_event(events: list, event_type: list[pygame.event.Event]) -> pygame.event.Event | None:
    """
    Search for a specific events in the list of events.
    """
    if type(event_type) != list:
        event_type = [event_type]
    filtered_events = []
    for event in events:
        if event.type in event_type:
            filtered_events.append(event)
    return filtered_events


def get_settings(settings: dict = {}) -> dict:
    """
    Mutate dict passed in argument (defaults to singleton `{}`) to hold settings defined in `options.txt`.
    A new dict may be given as argument to receive settings unique to a scope, avoiding to modify or to be modified by other part of the program.
    """
    if len(settings) != 0:
        return settings  # settings shouldn't be changed from file at runtime
    # feel free to add new default options if needed
    default: dict[str, str | int | float | bool | None] = {
        "version": "0.0.3",
        "default_max_energy": 4,
        "default_energy_per_turn": 3,
        "hand_size": 5,
        "deck_size": 15,
        "progressbar_style": 1,
        "strong_percent_increase": 20,  # can be negative to revert type matchup
        "passive_heal": 10,
        "passive_commander_heal": 20,
        "dev_mode": True,
        "mute": False,
        "mute_sfx": False,
        "volume": 100,
        "min_board_size": 2,
        "max_board_size": 6,
        # % decrease of commander damage per minion on its side.
        "per_minion_reduction": 8,
        "username": "",
        "default_power": 3,
        "power_increase": 7,
        "commanders_default_power": 65,
        "automatically_save_replay": True,
        # download from the host's computer in when playing as the client (TODO)
        "automatically_ask_for_replay": False
    }
    if "options.txt" not in os.listdir(cwd_path):
        write_settings(default)
    with open(os.path.join(cwd_path, "options.txt"), "r") as io:
        content = io.read()
        io.close()
    # possible bugs on windows due to \r\n but should work with str.strip
    for line in content.split("\n"):
        line = line.strip()
        # Ideally there shouldn't be empty lines, but it's better to check anyway
        if len(line) == 0:
            continue
        # please don't put two semicolons in a line though
        key, value, *_ = line.split(":")
        value = value_parser(value.strip())
        settings[key.strip()] = value  # value is already stripped/parsed
    if "version" not in settings or ltsemver(settings["version"], default["version"]):
        # Relevant to non-dev users, so printing is fine
        print("Detected outdated options, updating settings.")
        version = default["version"]
        default.update(settings)
        default["version"] = version
        settings.update(default)  # it works
        write_settings(default)
    return settings


def setting_str(key: str, value: bool | int | float | str | None) -> str:
    if isinstance(value, bool):
        if value:
            value = "true"
        else:
            value = "false"
    elif value is None:
        value = "none"
    elif isinstance(value, str):
        if len(value) == 0 or isfloatstr(value) or value in ["none", "false", "true"]:
            value = '"' + value + '"'
    else:
        value = str(value)
    if ':' in key or ':' in value:
        raise ValueError("Semicolon in setting values/keys are not permitted.")
    return key + ':' + value


def ltsemver(ver1: str, ver2: str):
    """
    Return `True` if `ver1` correspond to older semantic versioning than `ver2`.
    Note₁: returns `True` if `ver1` is invalid semantic versioning and throws a ValueError if `ver2` is invalid.
    Note₂: doesn't support build & prereleases.
    """
    error = ValueError(f'Excepted a version string "x.y.z", got: {ver2}')

    ver2 = ver2.split(".")
    if len(ver2) != 3:
        raise error
    try:
        ver2 = (*(int(n) for n in ver2),)
    except ValueError:
        raise error

    ver1 = ver1.split(".")
    if len(ver1) != 3:
        return True
    try:
        ver1 = (*(int(n) for n in ver1),)
    except ValueError:
        return True

    for i in range(3):
        if ver1[i] < ver2[i]:
            return True
        elif ver1[i] > ver2[i]:
            return False
    return False


def parse_semver(ver: str) -> tuple[int, int, int]:
    """
    Parse semantic version of format "x.y.z".
    Doesn't support prereleases/build flags.
    """
    error = ValueError(f'Excepted a version string "x.y.z", got: {ver}')
    ver = ver.split(".")
    # write explicit zeros
    if len(ver) != 3:
        raise error
    for n in ver:
        if not n.isdigit():
            raise error
    return (*(int(n) for n in ver),)


def toggle_mute():
    "Toggle sound mute in settings singleton."
    settings = get_settings()
    settings["mute"] = not settings["mute"]


def isfloatstr(arg: str) -> bool:
    "Return `True` if `arg` represent a int or a float (a decimal number)."
    for c in arg:
        if not (c.isdigit() or c == '.' or c == '-'):
            return False
    return True


def isintstr(arg: str) -> bool:
    "Return `True` if `arg` represent a int."
    for c in arg:
        if not (c.isdigit() or c == '-'):
            return False
    return True


def safe_static(f):
    """
    Use as a decorator. Eleminate duck typing by allowing the given function to enforce static typing on arguments.

    - Unannotated arguments may be of any type.
    - Supports return value.
    - Might terribly slow down the code due to Python being Python: do not use on Performance critical function, unless debugging.
    - Supports parametric types for: dict, tuple & iterators. (Python being Python, there is no parametric type for empty tuples).
    - Splatted arguments must be left at the end, might throw otherwise.
    - Splatted arguments annotation are for the arguments themself.
      - I.e. `*args: int` assert that each values of `args` are integers, not that `args` itself is an integer (fot it is a tuple).
    - For methods: `self` cannot be annotated.
    - `None` is not a valid type annotation: no argument is necessary is there is only one valid value. Nonetheless, `None | T` is valid.
    - The best way to make this work is to uninstall Python and download a language with a working type system.

    # Examples
    ```py
    >>> @static
    ... def f(a: int, b, c: str): pass
    >>> f(1, 1.0, "foo")
    >>> f(1, 1.0, 3)
    >>> f(1, 1, 3)
    Traceback (most recent call last):
      [...]
    >>> @static
    ... def i(x) -> str: return x
    >>> i("Correct return type.")
    "Correct return type."
    >>> i(b"Wrong return type.")
    Traceback (most recent call last):
      [...]
    ```
    """
    argcount: int = f.__code__.co_argcount
    # doesn't count splatting.
    all_args: tuple = f.__code__.co_varnames[:argcount]
    types: dict[str, type] = f.__annotations__
    # args is always before kwargs.
    splatted: tuple = (
        *(arg for arg in types if not arg in all_args and arg != "return"),)
    hasargsorkwargs: bool = len(splatted) != 0

    @wraps(f)
    def staticf(*args, **kwargs):
        for i in range(len(args)):
            if i < argcount:
                arg = all_args[i]
            elif hasargsorkwargs:
                arg = splatted[0]
            else:
                break  # doesn't check unannotated *args.
            if arg in types and not isinstancepar(args[i], types[arg]):
                raise TypeError(
                    f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types[arg])} for argument {arg}, got {type(args[i]).__name__}.")
        for arg in kwargs:
            if arg in types:
                if not isinstancepar(kwargs[arg], types[arg]):
                    raise TypeError(
                        f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types[arg])} for argument {arg}, got {type(kwargs[arg]).__name__}.")
            elif hasargsorkwargs and not arg in all_args:
                if not isinstancepar(kwargs[arg], types[splatted[-1]]):
                    raise TypeError(
                        f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types[splatted[-1]])} for argument {arg}, got {type(kwargs[arg]).__name__}.")
        ret = f(*args, **kwargs)
        if "return" in types and not isinstancepar(ret, types["return"]):
            raise TypeError(
                f"Invalid return value in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types['return'])} got {ret} of type {type(ret).__name__}")
        return ret
    staticf.__name__ = "static_" + f.__name__
    return staticf


@safe_static
def write_settings(settings: dict[str, bool | int | float | str | None]) -> dict:
    "Write settings in `./options.txt` overriding everything."
    settings_str = ""
    for setting in settings:
        settings_str += setting_str(setting, settings[setting]) + "\n"
    settings_str = settings_str[:-1]  # remove trailing newline
    with open(os.path.join(cwd_path, "options.txt"), "w") as io:
        try:
            io.write(settings_str)
        finally:
            io.close()
    return settings


@safe_static
def write_setting(key: str, value: str | bool | int | float | None) -> None:
    "Append a single setting in `./options.txt` and in `get_settings()`, returning it."
    setting = "\n" + setting_str(key, value)
    get_settings()[key] = value
    with open(os.path.join(cwd_path, "options.txt"), "a") as io:
        try:
            io.write(setting)
        finally:
            io.close()


def soft_static(f):
    "Same as `static` but throws warnings instead of errors."
    if not get_setting("dev_mode", False):
        return f
    argcount: int = f.__code__.co_argcount
    # doesn't count splatting.
    all_args: tuple = f.__code__.co_varnames[:argcount]
    types: dict[str, type] = f.__annotations__
    # args is always before kwargs.
    splatted: tuple = (
        *(arg for arg in types if not arg in all_args and arg != "return"),)
    hasargsorkwargs: bool = len(splatted) != 0

    @wraps(f)
    def staticf(*args, **kwargs):
        for i in range(len(args)):
            if i < argcount:
                arg = all_args[i]
            elif hasargsorkwargs:
                arg = splatted[0]
            else:
                break  # doesn't check unannotated *args.
            if arg in types and not isinstancepar(args[i], types[arg]):
                warn(
                    f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types[arg])} for argument {arg}, got {typename(type(args[i]))}.")
        for arg in kwargs:
            if arg in types:
                if not isinstancepar(kwargs[arg], types[arg]):
                    warn(
                        f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types[arg])} for argument {arg}, got {typename(type(kwargs[arg]))}.")
            elif hasargsorkwargs and not arg in all_args:
                if not isinstancepar(kwargs[arg], types[splatted[-1]]):
                    warn(
                        f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types[splatted[-1]])} for argument {arg}, got {typename(type(kwargs[arg]))}.")
        ret = f(*args, **kwargs)
        if "return" in types and not isinstancepar(ret, types["return"]):
            warn(
                f"Invalid return value in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {typename(types['return'])} got {ret} of type {typename(type(ret))}")
        return ret
    staticf.__name__ = "static_" + f.__name__
    return staticf


def typename(cls: type):
    if hasattr(cls, "__name__"):
        # Python supports so poorly unions that they don't work like the rest
        return cls.__name__
    return str(cls)


def isinstancepar(val: object, cls: type):
    """
    Return `True` if `val` is of parametric type `cls`. If `cls` is unvalid parametric type, it throws.

    Valid parametric types:
    - `tuple[type1, type2, ...]` for tuple with first element: type1, second: type2, ...: ...
      - E.g. `("foo", 314)` & `("bar", 2.718)` are `tuple[str, int | float]`, but `(3, "foo")` is not. 
    - `dict[keys_type, values_type]` for dict with keys of type `keys_type` and values of type `values_type`
    - `iterator[type]` for other iterators whose elements are *all* instances of `type`.
      - E.g. `["foo", "bar", 3.0]` is a `list[str | float]` but `[3]` is not.
      - E.g. `set[int]`, `list[str]`, ...
    """
    if cls is None:
        return val is None
    if isinstance(cls, str):
        return any(_cls.__name__ == cls for _cls in type(val).__mro__)
    if not hasattr(cls, "__args__"):
        # Non-paramatric
        return isinstance(val, cls)
    if not hasattr(cls, "__origin__"):
        # Unions
        # Or something else that shouldn't be used.
        for type_ in cls.__args__:
            if isinstancepar(val, type_):
                return True
        return False
    origin = cls.__origin__
    # origin is not parametrized
    if not isinstance(val, origin):
        return False
    if origin is dict:
        keyt, valt = cls.__args__
        for key in val:
            if not isinstancepar(key, keyt):
                return False
            if not isinstancepar(val[key], valt):
                return False
        return True
    elif origin is tuple:
        types = cls.__args__
        if len(val) != len(types):
            return False
        for i in range(len(val)):
            if not isinstancepar(val[i], types[i]):
                return False
        return True
    elif hasattr(cls, "__iter__"):
        par, *_ = cls.__args__
        for i in val:
            if not isinstancepar(i, par):
                return False
        return True
    return True  # isinstance of origin but parameters cannot be inferred


# Functions that need static must be left at the end as they need to be defined after static

def static(f):
    """
    Use instead of `static` on performance critical functions: it only enforces static typing during DEV()-mode,
    giving all the advantage of Static Typing basically permanently while not having its defaults.
    """
    settings = get_settings()
    # Used by get_setting so it cannot be used here (I hate python)
    if "dev_mode" in settings and settings["dev_mode"]:
        return safe_static(f)
    return f


@static  # no need for safe as called functions are safe
def get_setting(key: str, default: bool | int | float | str | None) -> bool | int | float | str | None:
    """
    Safely retrieve a single setting from `get_settings()`.
    Write the `default`ing value to `options.txt` if necessary, returning `default`.
    This is great for backward compatibility/update as an `options.txt` from a previous version may not contain newer keys.
    """
    settings = get_settings()
    if key in settings:
        return settings[key]

    warn(f"Setting {key} is not defined in `options.txt`, appending default.")
    write_setting(key, default)
    settings[key] = default

    return default


def warn(*args, dev: bool = get_setting("dev_mode", False), **kwargs) -> bool:
    """
    Print arguments in warning-style (if in DEV mode) and returns `True` to allow chaining.

    # Examples
    ```py
    >>> warn("foobarbaz") and print("do something here")
    ┌ Warning:
    └  foobarbaz
    do something here
    ```
    """
    if dev:  # hard check to avoid mistakes
        # might not work in every terminal, but should in VS Code
        print("\x1b[1;33m┌ Warning:\n└\x1b[0m ", *args, **kwargs)
    return True  # this is definitevely not spaghetti code.
