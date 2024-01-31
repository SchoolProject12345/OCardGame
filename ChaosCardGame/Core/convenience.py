from utility import *

if get_setting("dev", True):
    def DEV() -> bool: return True
else:
    def DEV() -> bool: return False

def getordef(d: dict, key, default):
    """    
    Get value at `key` from `dict` if it exists, returns `default` otherwise.

    # Examples
    ```py
    >>> getordef({"foo":"bar"}, "foo", 3)
    "bar"
    >>> getordef({"foo":"bar"}, "baz", 3)
    3
    ```
    """
    if key not in d:
        return default
    return d.get(key)


def getorset(d: dict, key, default):
    """
    Get value at `key` from `duct` if it exists, set `key` to `default` before returning it otherwise.

    # Examples
    ```py
    >>> x = {"foo":"bar"},
    >>> getorset(x, "foo", 3)
    'bar'
    >>> getorset(x, "bar", 3)
    3
    >>> x
    {'foo':'bar', 'bar':3}
    ```
    """
    if key not in d:
        d[key] = default
        return default
    return d.get(key)


def warn(*args, dev=DEV(), **kwargs) -> bool:
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
        print("\x1b[1;33m┌ Warning:\n└ ", *args, "\x1b[0m", **kwargs)
    return True  # this is definitevely not spaghetti code.


def ifelse(cond: bool, a, b):
    "Return `a` if `cond` is `True`, return `b` otherwise. Used to replace the lack of expression in Python."
    if cond:
        return a
    return b


def cleanstr(s: str) -> str:
    """
    Format the string passed in argument to a lowercase alphanumeric string.

    # Examples
    ```py
    >>> cleanstr("Foo-bar-73$\_{baz}$🐈‍⬛")
    "foobar73baz"
    ```
    """
    return "".join(filter(str.isalnum, s)).lower().translate(str.maketrans({
        'ø': 'o',
        'ö': 'o',
        'ó': 'o',
        'ä': 'a',
        'å': 'a',
        'ÿ': 'y',
        'ý': 'y',
        'í': 'i',
        "ü": 'u',
        'ú': 'u',
        'æ': "ae",
        'þ': "th"
    }))  # fix bugs with Fyyrönir


def withfield(d: dict, key, value):
    """
    Return d with value at key instead.

    # Examples
    ```py
    >>> a = {"foo":"bar","baz":3}
    >>> b = withfield(a, "foo", 5); b
    {"foo":5,"baz":3}
    >>> b["baz"] = "bar"; a # a is not mutated
    {"foo":"bar","baz":3}
    ```
    """
    d = d.copy()
    d[key] = value
    return d


def hasany(A: list, B: list) -> bool:
    """
    Returns `True` if `B` contains any element of `A`, `False` otherwise.

    # Examples
    ```py
    >>> hasany([1,2,3], [3,4,5])
    True
    >>> hasany([1,2,3], [4,5,6])
    False
    ```
    """
    for a in A:
        if a in B: return True
    return False

def show(arg):
    "Debug function returning its argument after printing it on the terminal."
    print(arg)
    return arg

def clamp(x, a, b):
    if x < a:
        return a
    if x > b:
        return b
    return x
