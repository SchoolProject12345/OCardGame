from utility import *

if get_setting("dev_mode", False):
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
    return "".join(filter(str.isalnum, s.lower().translate(str.maketrans({
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
        'þ': "th",
        '@': "at",
    }))))  # fix bugs with Fyyrönir


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

def clamp(x, min, max):
    if x < min:
        return min
    if x > max:
        return max
    return x

def nth(x: int) -> str:
    x = str(x)
    if len(x) > 1 and x[-2] == "1":
        return x + "th"
    if x[-1] == "1":
        return x + "st"
    if x[-1] == "2":
        return x + "nd"
    if x[-1] == "3":
        return x + "rd"
    return x + "th"
