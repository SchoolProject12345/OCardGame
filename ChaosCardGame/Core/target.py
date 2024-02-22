from typing import Union
from utility import static

def deep_or(var, *args):
    for arg in args:
        var = var | arg
    return var

class TargetMode:
    """
    Wrapper around `int` which implements `__or__` & `__and__`.
    Has multiple class variables, each representing an elementary target mode or a flag.
    A complex TargetMode is formed taking bitwise `or` of all its compounds,
    e.g. TargetMode(TargetMode.target, TargetMode.self, TargetMode.nocommander)
    target both `self` and `target` but cannot set a commander as its main target.
    The first 16 bits are targets (e.g. FOES), and the last 16 bits are flags (e.g. NOCOMMANDER).
    """
    # TARGETS:
    TARGET: int           = 1 << 0
    FOES: int             = 1 << 1
    ALLIES: int           = 1 << 2
    USER: int             = 1 << 3
    COMMANDER: int        = 1 << 4
    ALLIED_COMMANDER: int = 1 << 5
    # FLAGS - used to construct complex targets:
    RANDOM: int           = 1 << 29 # unimplemented
    CAN_SELF: int         = 1 << 30
    NOCOMMANDER: int      = 1 << 31
    def __init__(self, arg: Union["TargetMode", int], *args: Union["TargetMode", int]):
        if isinstance(arg, TargetMode):
            arg = arg.target_string
        self.target_string: int = arg
        for target in args:
            self.target_string = int(self.target_string | target)
    def copy(self) -> "TargetMode":
        return TargetMode(self.target_string)
    @static # you probably don't want to compare with other types.
    def __eq__(self, target: Union["TargetMode", int]):
        if isinstance(target, TargetMode):
            target = target.target_string
        return self.target_string == target
    def __int__(self) -> int:
        return self.target_string
    def __bool__(self) -> bool:
        return bool(self.target_string)
    def __or__(self, target: Union["TargetMode", int]) -> "TargetMode":
        return TargetMode(self.target_string | target)
    def __ror__(self, target: Union["TargetMode", int]) -> "TargetMode":
        return TargetMode(self.target_string | target)
    def __and__(self, target: Union["TargetMode", int]) -> "TargetMode":
        return TargetMode(self.target_string & target)
    def __rand__(self, target: Union["TargetMode", int]) -> "TargetMode":
        return TargetMode(self.target_string & target)
    @static
    def has_target(self, target: int) -> bool:
        return bool(self.target_string & target)
    def cancommander(self) -> bool:
        return not self & 1 << 31
    def canself(self) -> bool:
        return (self & 1 << 3) or (self & 1 << 2)  or (self & 1 << 30)
    # useful for debugging:
    def __repr__(self):
        return ("TargetMode(" +
            " | ".join(
                "TargetMode." + target
                for target in self.__annotations__
                if getattr(self, target) & self.target_string
            ) + ")"
        )
    @classmethod
    def from_str(self, name: str | list[str]) -> "TargetMode":
        if isinstance(name, list):
            return deep_or(*(TargetMode.from_str(target) for target in name))
        name_ = name.lower().strip()
        if not name_ in self.__dict__:
            raise NameError(f"{name} is not a valid TargetMode name.")
        return self.__dict__[name_]
    def to_str(self) -> str:
        return ", ".join(
                target.lower().replace('_', ' ')
                for target in self.__annotations__
                if getattr(self, target) & self.target_string & ((1 << 16) - 1) # no flag
        )
    def __str__(self) -> str:
        return self.target_string.__str__()
    def __format__(self, format_spec: str):
        return self.target_string.__format__(format_spec)

TargetMode.target             = TargetMode(TargetMode.TARGET)
TargetMode.foes               = TargetMode(TargetMode.FOES)
TargetMode.allies             = TargetMode(TargetMode.ALLIES)
TargetMode.user               = TargetMode(TargetMode.USER)
TargetMode.commander          = TargetMode(TargetMode.COMMANDER)
TargetMode.allied_commander   = TargetMode(TargetMode.ALLIED_COMMANDER)
TargetMode.random             = TargetMode(TargetMode.RANDOM)
TargetMode.can_self           = TargetMode(TargetMode.CAN_SELF)
TargetMode.nocommander        = TargetMode(TargetMode.NOCOMMANDER)
TargetMode.all                = TargetMode(TargetMode.foes, TargetMode.allies)
TargetMode.massivedestruction = TargetMode(TargetMode.all, TargetMode.allied_commander, TargetMode.commander)

#print(repr(TargetMode.allies))
#print(repr(TargetMode.massivedestruction))
#print(repr(TargetMode.from_str(["foes", "allies", "nocommander"])))