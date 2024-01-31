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
    default = f'version:"{version}"\ndefault_max_energy:4\ndefault_energy_per_turn:3\nhand_size:5\ndeck_size:30\nprogressbar_sytle:1\nstrong_percent_increase:20\npassive_heal:10\npassive_commander_heal:20\ndev_mode:true'
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
