import os

cwd_path = os.path.dirname(os.path.abspath(__file__))

def get_settings(settings: dict = {}) -> dict:
    """
    Mutate dict passed in argument (defaults to singleton `{}`) to hold settings defined in `options.txt`.
    A new dict may be given as argument to receive settings unique to a scope, avoiding to modify or to be modified by other part of the program.
    """
    if len(settings) != 0:
        return settings # settings shouldn't be changed from file at runtime
    version = "0.0.0"
    default = f'version:"{version}"\ndefault_max_energy:4\ndefault_energy_per_turn:3\nhand_size:5\ndeck_size:30\nprogressbar_sytle:1\nstrong_percent_increase:20\npassive_heal:10\npassive_commander_heal:20\ndev_mode:true\nmute:false\nmute_sfx:false'
    if "options.txt" not in os.listdir(cwd_path):
        with open(os.path.join(cwd_path, "options.txt"), "x") as io:
            # feel free to add new default options if needed
            content = default
            io.write(content)
            io.close()
    else: # no need to read what was just written
        with open(os.path.join(cwd_path, "options.txt"), "r") as io:
            content = io.read()
            io.close()
    for line in content.split("\n"): # possible bugs on windows due to \r\n but should work with str.strip
        line = line.strip()
        # Ideally there shouldn't be empty lines, but it's better to check anyway
        if len(line) == 0:
            continue
        key, value, *_ = line.split(":") # please don't put two semicolons in a line though
        value = value.strip()
        if len(value) == 0:
            # I'd rather not immport the whole conveniance module just for a warn,
            # but anyway I think we can assume nobody will leave a key unasigned in options.txt,
            # you've been warned here so don't complain if you do 👀
            continue
        # would unecessary pollute the namespace if defined outside
        def isfloat(arg: str):
            for c in arg:
                if not (c.isdigit() or c == '.'):
                    return False
            return True
        if value[0] == value[-1] == '"':
            value = value[1:-1] # no strip after as spaces may be intentional
        elif value == "true":
            value = True
        elif value == "false":
            value = False
        elif value.isdigit():
            # Note: doesn't support negative numbers (should be fixed)
            value = int(value)
        elif isfloat(value):
            value = float(value)
        # technically valid string option even without "", they are only needed for numeric values (e.g. "1", "true")
        settings[key.strip()] = value # value is already stripped/parsed
    if "version" not in settings or ltsemver(settings["version"], version):
        # relevant even to non-dev users, so a print is fine.
        print("Detected outdated options, updating to new defaults. \033[1;31mNote\033[0m: this overrides all previous options.")
        with open(os.path.join(cwd_path, "options.txt"), "w") as io:
            io.write(default)
            io.close()
        settings.clear() # I admit this is really spaghetti and another solution should be done.
        # Nonetheless it shouldn't break anything
        return get_settings(settings)
    return settings

def ltsemver(ver1: str, ver2: str):
    """
    Return `True` if `ver1` correspond to older semantic versioning than `ver2`.
    Note₁: returns `True` if `ver1` is invalid semantic versioning and throws a ValueError if `ver2` is invalid.
    Note₂: doesn't support build & prereleases.
    """
    error = ValueError(f'Excepted a version string "x.y.z", got: {ver2}')

    ver2 = ver2.split('.')
    if len(ver2) != 3:
        raise error
    try:
        ver2 = (*(int(n) for n in ver2),)
    except ValueError:
        raise error
    
    ver1 = ver1.split('.')
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
    ver = ver.split('.')
    # write explicit zeros
    if len(ver) != 3:
        raise error
    for n in ver:
        if not n.isdigit():
            raise error
    return (*(int(n) for n in ver),)

def get_setting(key: str, default: bool | int | str):
    """
    Safely retrieve a single setting from `get_settings()`.
    Write the `default`ing value to `options.txt` if necessary, returning `default`.
    This is great for backward compatibility/update as an `options.txt` from a previous version may not contain newer keys.
    """
    settings = get_settings()
    if key in settings:
        return settings[key]
    # Look at what Python forces to do to simulate a strong typing system:
    if not any(isinstance(default, type) for type in (bool, int, str)):
        # It should be at the beginning for safety, but that'd impact performances, so please just don't use invalid types fpr default.
        raise ValueError("`get_setting`'s default excepted either a `bool`, `int` or `str`")
    settings[key] = default
    if isinstance(default, bool):
        if default:
            default = "true"
        else:
            default = "false"
    with open(os.path.join(cwd_path, "options.txt"), "a") as io:
        io.write(f"\n{key}:{default}")
        io.close()
    return default

def toggle_mute():
    "Toggle sound mute in settings singleton."
    settings = get_settings()
    settings["mute"] = not settings["mute"]

# Use extensively across code.
# Do not hesitate to use.
# I didn't spend 3 hours to make this for nothing.
# Use it. Seriously do.
# Stand against Duck Typing's tyranny.
# Just one @fast_static before your function, and Duck Typing is gone.
# It's that simple.
def fast_static(f):
    """
    Use instead of `static` on performance critical functions: it only enforces static typing during DEV()-mode,
    giving all the advantage of Static Typing basically permanently while not having its defaults.
    """
    if get_setting("dev_mode", False):
        return static(f)
    return f

def static(f):
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
    all_args: tuple = f.__code__.co_varnames[:argcount] # doesn't count splatting.
    types: dict[str, type] = f.__annotations__
    splatted: tuple = (*(arg for arg in types if not arg in all_args and arg != "return"),) # args is always before kwargs.
    hasargsorkwargs: bool = len(splatted) != 0
    def staticf(*args, **kwargs):
        for i in range(len(args)):
            if i < argcount:
                arg = all_args[i]
            elif hasargsorkwargs:
                arg = splatted[0]
            else:
                break # doesn't check unannotated *args.
            if arg in types and not isinstancepar(args[i], types[arg]):
                raise TypeError(f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {types[arg].__name__} for argument {arg}, got {type(args[i]).__name__}.")
        for arg in kwargs:
            if arg in types:
                if not isinstancepar(kwargs[arg], types[arg]):
                    raise TypeError(f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {types[arg].__name__} for argument {arg}, got {type(kwargs[arg]).__name__}.")
            elif hasargsorkwargs and not arg in all_args:
                if not isinstancepar(kwargs[arg], types[splatted[-1]]):
                    raise TypeError(f"Wrong argument type in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {types[splatted[-1]].__name__} for argument {arg}, got {type(kwargs[arg]).__name__}.")
        ret = f(*args, **kwargs)
        if "return" in types and not isinstancepar(ret, types["return"]):
            raise TypeError(f"Invalid return value in {f.__name__} (line {f.__code__.co_firstlineno}): excepted {types['return'].__name__} got {ret} of type {type(ret).__name__}")
        return ret
    staticf.__name__ = "static_" + f.__name__
    return staticf

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
    if not hasattr(cls, "__args__"):
        return isinstance(val, cls)
    # assuming all parametric types implement origin (Python can't be that bad right?)
    origin = cls.__origin__
    if not isinstance(val, origin):
        return False
    if origin is dict:
        keyt, valt = cls.__args__
        for key in val:
            if not isinstance(key, keyt):
                return False
            if not isinstance(val[key], valt):
                return False
        return True
    elif origin is tuple:
        types = cls.__args__
        if len(val) != len(types):
            return False
        for i in range(len(val)):
            if not isinstance(val[i], types[i]):
                return False
        return True
    elif hasattr(cls, "__iter__"):
        par, *_ = cls.__args__
        for i in val:
            if not isinstance(i, par):
                return False
        return True
    return True # isinstance of origin but parameters cannot be inferred

# Aliases
# Yes, they are global variables as Python doesn't have constants,
# But they should be used outside of annotations, which are evaluated only once,
# so this is fine.
Real: type = int | float | bool # Booleans supports real operations.
Number: type = Real | complex
Any: type = object
