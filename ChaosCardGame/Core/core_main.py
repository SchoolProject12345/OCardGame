from Core.convenience import *  # makes code cleaner, includes utility.py
from dataclasses import dataclass  # easier class declaration
from enum import IntEnum  # for clear, lightweight (int) elements/state.
from json import loads, dumps
from numpy import random as rng  # for shuffle function/rng effects
import numpy as np  # for gcd for Kratos card
import os
import re

class Constants:  # to change variables quickly, easily and buglessly.
    # Client settings (DEV() is through function)
    path = cwd_path
    progressbar_style = get_setting("progressbar_style", 1) # must clamp between 0-2 but needs cleaning first
    # Server settings
    default_max_energy = max(1, get_setting("default_max_energy", 4))
    default_energy_per_turn = max(1, get_setting("default_energy_per_turn", 3))
    default_hand_size = max(1, get_setting("hand_size", 5))
    default_deck_size = max(1, get_setting("deck_size", 15))
    strong_increase = max(0, get_setting("strong_percent_increase", 20)) // 10 # percent are overrated
    passive_heal = max(0, get_setting("passive_heal", 10)) # negative may cause crashes
    commander_heal = max(0, get_setting("passive_commander_heal", 20))
    commander_power = 65
    base_power = 3
    power_increase = 7

class Numeric:
    def eval(self, **_) -> int:
        return warn(f"Numeric value of type {type(self)} cannot be acessed.") and 0
    def from_json(json: dict | int):
        if type(json) == int:
            return RawNumeric(json)
        match json["type"].lower():
            case "raw": return RawNumeric(json["value"])
            case "hps": return HPList(TargetMode.from_str(json["target_mode"]))
            case "gcd": return GCDNumeric(Numeric.from_json(json["sample"]))
            case "sum": return NumericSum(Numeric.from_json(json["sample"]))
            case "count": return CountUnion(TargetMode.from_str(json["target_mode"]), (*json["tags"],), (*[Element.from_str(element) for element in json["elements"]],))
            case "energy": return EnergyCount(json["type"])
            case "mul": return MultNumeric(Numeric.from_json(json["times"]), json["num"], json["den"])
            case "add": return AddNumeric(Numeric.from_json(json["a"]), Numeric.from_json(json["b"]))
            case "func": return FuncNumeric.from_json(json)
            case "turn": return TurnNumeric()
            case "damagetaken": return DamageTaken()
            case _: return warn(f"Wrong Numeric type '{json['type']}' in json.") and RawNumeric(0)
    def __str__(self) -> str:
        return f"UNDEFINED ({type(self)})"

@dataclass
class TurnNumeric(Numeric):
    def eval(self, **kwargs):
        return kwargs["board"].turn
    def __str__(self):
        return "current turn"

@dataclass
class DamageTaken(Numeric):
    def eval(self, **kwargs):
        return getordef(kwargs, "damage_taken", 0)
    def __str__(self):
        return "damage taken"

@dataclass
class RawNumeric(Numeric):
    value: int
    def eval(self, **_) -> int:
        return self.value
    def __str__(self):
        return str(self.value)
    def __iadd__(self, value: int):
        self.value += value
        return self
    def __isub__(self, value: int):
        self.value -= value
        return self

class NumericList(Numeric):
    def eval(self, **_) -> list[int]:
        return warn(f"Numeric values of type {type(self)} cannot be acessed.") and [0]

@dataclass
# To get HP from a single target, use `NumericSum(HPList(TargetMode.target))`
class HPList(NumericList):
    target_mode: any  # slightly spagehtti but this will do for now
    def eval(self, **kwargs) -> list[int]:
        return [card.hp for card in AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", self.target_mode))]
    def __str__(self):
        return f"the HP from {self.target_mode.to_str()}"


@dataclass
class GCDNumeric(Numeric):
    "Return the GCD of all elements in the list returned by `eval`uation of the `NumericList`."
    sample: NumericList
    def eval(self, **kwargs) -> int:
        # please save me from Python
        return np.gcd.reduce(self.sample.eval(**kwargs))
    def __str__(self):
        return f"the greatest common divisor of {str(self.sample)}"

@dataclass
class NumericSum(Numeric):
    sample: NumericList
    def eval(self, **kwargs) -> int:
        return np.sum(self.sample.eval(**kwargs))
    def __str__(self):
        return f"the sum of {self.sample}"

@dataclass
class CountUnion(Numeric):
    "Return the number of creatures among the targets that match eithere by `tags` or by `elements`."
    target_mode: any
    tags: tuple[str]
    elements: list  # a list of element IntEnum or Integers.
    def eval(self, **kwargs) -> int:
        i = 0
        for creature in AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", self.target_mode)):
            if hasany(creature.card.tags, self.tags) or (creature.element in self.elements):
                i += 1
        return i

@dataclass
class EnergyCount(Numeric):
    """Return the energy of the user's owner (either "max", "current" or "perturn")"""
    type: str
    def eval(self, **kwargs) -> int:
        owner = kwargs["user"].owner
        match cleanstr(self.type):
            case "max": return owner.max_energy
            case "current": return owner.energy
            case "perturn": return owner.energy_per_turn
            case "turn": return owner.energy_per_turn # match "/turn"

@dataclass
class MultNumeric(Numeric):
    "Evaluate the product of a numeric with a rational."
    numeric: Numeric
    num: int
    den: int
    def eval(self, **kwargs) -> int:
        return self.numeric.eval(**kwargs) * self.num // self.den
    def __str__(self):
        # TODO: make more verbal
        return f"{self.num}({self.numeric})/{self.den}"
@dataclass
class AddNumeric(Numeric):
    "Evaluate the addition of two numerics."
    a: Numeric
    b: Numeric
    def eval(self, **kwargs) -> int:
        return self.a.eval(**kwargs) + self.b.eval(**kwargs)
    def __str__(self):
        return f"{self.a} + {self.b}"

@dataclass
class FuncNumeric(Numeric):
    f: any
    numeric: Numeric
    def eval(self, **kwargs) -> int:
        return int(self.f(self.numeric.eval(**kwargs)))
    def from_json(json: dict):
        match cleanstr(json["f"]):
            case "log2": f = np.log2
            case "exp": f = np.exp
            case "square": f = lambda x: x**2
        return FuncNumeric(
            f,
            Numeric.from_json(json["numeric"])
        )

def getCARDS(CARDS=[]) -> list:
    "Return the list of every card defined in `Data/cards.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(CARDS) != 0:
        return CARDS
    io = open(
        os.path.join(Constants.path, "Data/cards.json"),
    encoding="utf-8")
    json = loads(io.read())
    io.close()
    id = -1  # starts at -1 + 1 = 0
    for card in json:
        try:
            CARDS += [AbstractCard.from_json(card, (id := id + 1))]
        except:
            warn("Got an error with card named:", card["name"])
            id -= 1
    return CARDS

def getCOMMANDERS(COMMANDERS={}) -> dict:
    "Return a dict of every card defined `Data/commanders.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(COMMANDERS) != 0:
        return COMMANDERS
    io = open(
        os.path.join(Constants.path, "Data/commanders.json"),
    encoding="utf-8")
    json = loads(io.read())
    io.close()
    id = -1
    COMMANDERS.update({cleanstr(card["name"]): CreatureCard.from_json(
        card, (id := id + 1)) for card in json})
    return COMMANDERS

def format_name_ui(name: str, element: int = 0):
    "From an element and a name, give the formated name to allow easy asset access."
    match Element(element):
        case Element.elementless:
            pre = ""
        case Element.fire:
            pre = "fire_"
        case Element.water:
            pre = "wtr_"
        case Element.air:
            pre = "air_"
        case Element.chaos:
            pre = "cha_"
        case Element.earth:
            pre = "ert_"
    m = re.match("(The )?([^,]*)(,.*)?", name, re.RegexFlag.I)
    if m is None:
        warn(f'"{name}"\'s name is terribly wrong.')
        name = cleanstr(name)
    else:
        name = cleanstr(m[2])
    return pre + name

class Element(IntEnum):
    # used instead of None as a placeholder (for type-safeness) or for elementless card types for flexibility when using Element.effectiveness
    elementless = 0
    water = 1
    fire = 2
    air = 3
    earth = 4
    # Weak defense against all but chaos (x1,2 damage taken) but powerful attack against all but chaos (x1.2 damage output)
    chaos = 5
    def from_str(name: str):
        "Return an Element value from name string."
        match cleanstr(name):
            case "water": return Element.water
            case "fire": return Element.fire
            case "air": return Element.air
            case "earth": return Element.earth
            # keeping chaos as it is a more interesting alternative than elementless for cards with no obvious element
            case "chaos": return Element.chaos
            case _: return warn(f"Tried to form an Element from \"{name}\"; returned Element.elementless instead.") and Element.elementless
    def to_str(self) -> str:
        "Return self's name as a string such that `assert Element.from_str(self.to_str()) == self`."
        match self:
            case Element.water: return "water"
            case Element.fire: return "fire"
            case Element.air: return "air"
            case Element.earth: return "earth"
            case Element.chaos: return "chaos"
    def from_json(json: dict):
        if "element" not in json:
            return warn(f"Card with name {json['name']} has no element defined (don't do that intentionally please)") and Element.elementless
        return Element.from_str(json["element"])
    def effectiveness(self, other) -> bool:
        """
            Element.effectiveness(self, other: Element)

        Return True if self is effective on other/if other is weak to self, False otherwise.
        To get resistance, use `self.resist(other)` instead.

        # Examples
        ```py
        >>> Element.water.effectiveness(Element.fire)
        True
        >>> Element.fire.effectiveness(Element.fire) | Element.fire.effectiness(Element.earth)
        False
        ```
        """
        if self == Element.chaos and other == Element.chaos:
            return False  # changed chaos to resist chaos to avoid chaos being just a x1.2 in power and /1.2 in HP
        if self == Element.chaos or other == Element.chaos:
            return True

        if self == Element.water and other == Element.fire:
            return True
        if self == Element.fire and other == Element.air:
            return True
        if self == Element.air and other == Element.earth:
            return True
        if self == Element.earth and other == Element.water:
            return True

        return False
    def resist(self, other) -> bool:
        """
            Element.resist(self, other: Element)

        Return `True` if `self` resist `other`, `False` otherwise.

        # Examples
        ```py
        >>> Element.water.resist(Element.fire)
        True
        ```
        """
        if self == Element.chaos and other == Element.chaos:
            return True
        if self == Element.chaos or other == Element.chaos:
            return False
        return self.effectiveness(other)

class State(IntEnum):
    discarded = 127  # for GUI
    damageless = 5  # can't take direct damage
    blocked = 4  # can't attack
    cloudy = 3 # single targeted only, -20% dmg, random targeted.
    invisible = 2  # can't attack; can't be targeted
    monotonous = 1 # no SE multiplier
    unattacked = 0  # set target.attacked to False without affecting self.state
    default = -128  # placeholder
    def from_str(name: str):
        match cleanstr(name):
            case "default": return State.default
            case "blocked": return State.blocked
            case "block": return State.blocked
            case "invisible": return State.invisible
            case "damageless": return State.damageless
            case "unattacked": return State.unattacked
            case "cloudy": return State.cloudy
            case "monotonous": return State.monotonous
            case _: return (warn("Tried to form State from an non-recognized string; returing State.default instead.") and State.default)

class TargetMode(IntEnum):
    random_chaos = -1
    foes = 0
    target = 1
    allies = 2
    self = 3  # it can't possibly cause a bug, right? ( ͡° ͜ʖ ͡°)
    commander = 4
    allied_commander = 5
    all_commanders = 6
    massivedestruction = 7
    all = 8
    def from_str(name: str):
        match cleanstr(name):
            case "randomchaos": return TargetMode.random_chaos
            case "randomtargetmode": return TargetMode.random_chaos
            case "randomlyselectedrandomtargets": return TargetMode.random_chaos
            case "foes": return TargetMode.foes
            case "target": return TargetMode.target
            case "allies": return TargetMode.allies
            case "self": return TargetMode.self
            case "user": return TargetMode.self
            case "commander": return TargetMode.commander
            case "foecommander": return TargetMode.commander
            case "enemycommander": return TargetMode.commander
            case "alliedcommander": return TargetMode.allied_commander
            case "allcommanders": return TargetMode.all_commanders
            case "bothcommanders": return TargetMode.all_commanders
            case "commanders": return TargetMode.all_commanders
            case "all": return TargetMode.all,
            case "massivedestruction": return TargetMode.massivedestruction
            case "guaranteedchaos": return TargetMode.massivedestruction
            case "everycreaturethathaseversetfootinthisarena": return TargetMode.massivedestruction
    def to_str(self):
        match self:
            case TargetMode.foes: return "foes"
            case TargetMode.target: return "target"
            case TargetMode.allies: return "allies"
            case TargetMode.self: return "user"
            case TargetMode.commander: return "enemy Commander"
            case TargetMode.allied_commander: return "allied Commander"
            case TargetMode.all_commanders: return "both Commanders"
            case TargetMode.all: return "all"
            case TargetMode.massivedestruction: return "every creature that has ever set foot in this Arena"
            case TargetMode.random_chaos: return "randomly selected random targets"

class DamageMode(IntEnum):
    direct = 0
    indirect = 1
    ignore_resist = 2
    ignore_se = 3
    def from_str(name: str):
        match cleanstr(name):
            case "direct": return DamageMode.direct
            case "indirect": return DamageMode.indirect
            case "ignoreresist": return DamageMode.ignore_resist
            case "resistanceignoring": return DamageMode.ignore_resist
            case "ignorese": return DamageMode.ignore_se
            case _: return warn(f"Tried to form DamageMode from {name}, returning DamageMode.direct instead.") and DamageMode.direct
    def to_str(self) -> str:
        match self:
            case DamageMode.direct: return "direct"
            case DamageMode.indirect: return "indirect"
            case DamageMode.ignore_resist: return "resistance-ignoring"
    def can_strong(self) -> bool:
        return self not in [DamageMode.indirect, DamageMode.ignore_se]
    def can_weak(self) -> bool:
        return self in [DamageMode.direct, DamageMode.ignore_se]

class ReturnCode(IntEnum):
    ok = 200
    cant = 400
    no_energy = 401
    wrong_turn = 402
    charging = 403
    no_target = 404
    failed = 500

@dataclass
class EffectSurvey:
    "Contain all values returned by an attack."
    damage: int = 0
    heal: int = 0
    return_code: ReturnCode = ReturnCode.ok
    def __add__(self, other):
        return EffectSurvey(self.damage + other.damage, self.heal + other.heal, self.return_code)
    def __iadd__(self, other):
        self.damage += other.damage
        self.heal += other.heal
        return self

class AbstractEffect:
    def execute(self, **_) -> bool:
        "`kwargs` needed for execution: player, board, main_target, target_mode, user, survey"
        warn(
            f"AbstractEffect of type {type(self)} has no execute method defined.")
        return False
    def endturn(self, target) -> bool:
        "AbstractEffect.endturn is a method that is applied at the end of each turn to the creature affected by it, returning False if the effect ends on this turn."
        return warn(f"Creature with name {target.card.name} was affected by effect of type {type(self)} which doesn't support endturn method.") and False
    def targeted_objects(**kwargs):
        match kwargs["target_mode"]:
            case TargetMode.target: return [kwargs["main_target"]]
            case TargetMode.foes: return [*filter((lambda x: x != None), kwargs["board"].unactive_player.active)]
            case TargetMode.allies: return [*filter((lambda x: x != None), kwargs["board"].active_player.active)]
            case TargetMode.self: return [kwargs["user"]]
            case TargetMode.commander: return [kwargs["board"].unactive_player.commander]
            case TargetMode.allied_commander: return [kwargs["board"].active_player.commander]
            case TargetMode.all_commanders: return [kwargs["board"].unactive_player.commander, kwargs["board"].active_player.commander]
            case TargetMode.all:
                return [
                    *filter((lambda x: x != None),
                            kwargs["board"].unactive_player.active),
                    *filter((lambda x: x != None and x !=
                            kwargs["user"]), kwargs["board"].active_player.active),
                ]
            case TargetMode.massivedestruction:
                return [
                    *filter((lambda x: x != None),
                            kwargs["board"].unactive_player.active),
                    *filter((lambda x: x != None),
                            kwargs["board"].active_player.active),
                    kwargs["board"].unactive_player.commander,
                    kwargs["board"].active_player.commander
                ]
            case TargetMode.random_chaos: return AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", TargetMode(rng.randint(9))))
            case _: return []
    def get_tags(self):
        return warn(f"Tried to get tags from a {type(self)}") and ()
    def from_json(json: dict):
        type = cleanstr(getordef(json, "type", "undefined"))
        match type:
            case "union": return EffectUnion.from_json(json)
            case "effectunion": return EffectUnion.from_json(json)
            case "targetchange": return ChangeTarget.from_json(json)
            case "changetarget": return ChangeTarget.from_json(json)
            case "statechange": return ChangeState.from_json(json)
            case "changestate": return ChangeState.from_json(json)
            case "damage": return DamageEffect.from_json(json)
            case "heal": return HealEffect.from_json(json)
            case "drain": return DamageDrain.from_json(json)
            case "withprobability": return WithProbability.from_json(json)
            case "gainenergy": return EnergyEffect.from_json(json)
            case "addenergy": return EnergyEffect.from_json(json)
            case "energygain": return EnergyEffect.from_json(json)
            case "dot": return DOTEffect.from_json(json)
            case "damageovertime": return DOTEffect.from_json(json)
            case "delay": return DelayEffect.from_json(json)
            case "loop": return LoopEffect.from_json(json)
            case "randomtarget": return RandomTargets.from_json(json)
            case "randomtargets": return RandomTargets.from_json(json)
            case "repeat": return RepeatEffect.from_json(json)
            # .from_json is useless but it allows more flexibility if we want to add something
            case "hypnotize": return HypnotizeEffect.from_json(json)
            case "summon": return SummonEffect.from_json(json)
            case "changeforme": return FormeChange.from_json(json)
            case "changeform": return FormeChange.from_json(json)
            case "formechange": return FormeChange.from_json(json)
            case "formchange": return FormeChange.from_json(json)
            case "taunt": return TauntTargets.from_json(json)
            case "cleanse": return CleanseEffect.from_json(json)
            case "redirect": return DamageRedirect.from_json(json)
            case "boardresize": return BoardResize.from_json(json)
            case "if": return IfEffect.from_json(json)
            case "hardcoded": return HardCodedEffect(getordef(json, "desc", ""))
            case "null": return NullEffect()
            case "noeffect": return NullEffect()
            case None: return NullEffect()
            case _: return warn(f"Tried to parse an effect with type {type} in {json}. Returning NullEffect instead.") and NullEffect()

class NullEffect(AbstractEffect):
    "Does literally nothing except consumming way to much RAM thanks to this beautiful innovation that OOP is."
    def execute(self, **_) -> bool:
        return False
    def from_json():
        return NullEffect()
    def __str__(self) -> str:
        return "nothing"

@dataclass
class HardCodedEffect(AbstractEffect):
    desc: str
    def execute(self, **_) -> bool:
        return True
    def from_json(json):
        return HardCodedEffect(getordef(json, "desc", ""))
    def __str__(self):
        return self.desc

@dataclass
class IfEffect(AbstractEffect):
    "Evaluate `effect` only if `value` is greater or equal than `cond`, `other` otherwise."
    effect: AbstractEffect
    other: AbstractEffect
    value: Numeric
    cond: Numeric
    def execute(self, **kwargs) -> bool:
        if not self.value.eval(**kwargs) < self.cond.eval(**kwargs):
            return self.effect.execute(**kwargs)
        else:
            return self.other.execute(**kwargs)
    def from_json(json: dict):
        return IfEffect(AbstractEffect.from_json(json["effect"]), AbstractEffect.from_json(getordef(json, "else", {"type":"null"})), Numeric.from_json(json["value"]), Numeric.from_json(getordef(json, "cond", 0)))
    def __str__(self):
        return f"{self.effect} if {self.value} is greater or equal to {self.cond}"

@dataclass
class DamageRedirect(AbstractEffect):
    "Redirect `amount` damages from `from_` distribution to targets."
    from_: TargetMode
    amount: Numeric
    def execute(self, **kwargs) -> bool:
        amount = self.amount.eval(**kwargs)
        targets = AbstractEffect.targeted_objects(**kwargs)
        from_ = AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", self.from_))
        if amount == 0 or len(targets) == 0 or len(from_) == 0:
            return False
        while amount > 0 and len(targets) > 0 and len(from_) > 0:
            target = targets.pop()
            try_amount = min(amount // (len(targets) + 1), target.hp)
            sources = from_.copy()
            while len(sources) != 0:
                source = sources.pop()
                redirected = min(source.card.max_hp - source.hp, try_amount // (len(sources) + 1))
                source.heal(target.indirectdamage(redirected))
        return True
    def from_json(json: dict):
        return DamageRedirect(TargetMode.from_str(json["from"]), Numeric.from_json(json["amount"]))
    def __str__(self):
        return f"redirect {self.amount} damages from {self.from_.name} to the target(s)"

@dataclass
class EffectUnion(AbstractEffect):
    # use two field rather than a list so that length is known at interpretation time (would be useful if Python was LLVM-compiled)
    # I might change that later though, but for now use `Union(Union(effect1, effect2), effect3)` or similar for more than 2 effects.
    effect1: AbstractEffect
    effect2: AbstractEffect
    def execute(self, **kwargs) -> bool:
        return self.effect1.execute(**kwargs) | self.effect2.execute(**kwargs)
    def from_json(json: dict):
        return EffectUnion(AbstractEffect.from_json(json["effect1"]), AbstractEffect.from_json(json["effect2"]))
    def __str__(self) -> str:
        return f"{str(self.effect1)} and {str(self.effect2)}"

@dataclass
class ChangeTarget(AbstractEffect):
    "Change targetting mode of sub-effects."
    effect: AbstractEffect
    new_target: TargetMode
    def execute(self, **kwargs) -> bool:
        kwargs = kwargs.copy()
        if kwargs["user"].state == State.cloudy:
            if self.new_target in [TargetMode.allies, TargetMode.self, TargetMode.allied_commander]:
                kwargs["target_mode"] = TargetMode.self
            else:
                kwargs["target_mode"] = TargetMode.target
        else:
            kwargs["target_mode"] = self.new_target
        return self.effect.execute(**kwargs)
    def from_json(json: dict):
        return ChangeTarget(AbstractEffect.from_json(json["effect"]), TargetMode.from_str(json["new_target"]))
    def __str__(self) -> str:
        return f"{str(self.effect)} on {self.new_target.to_str()}"

@dataclass
class RandomTargets(AbstractEffect):
    "Pick `sample` random targets from target distribution."
    effect: AbstractEffect
    sample: Numeric
    def execute(self, **kwargs) -> bool:
        targets = AbstractEffect.targeted_objects(**kwargs)
        rng.shuffle(targets)  # maybe unefficient but it works.
        sample = self.sample.eval()
        while len(targets) > sample:
            targets.pop()
        kwargs = withfield(kwargs, "target_mode", TargetMode.target)
        return np.any([self.effect.execute(**withfield(kwargs, "main_target", target)) for target in targets])
    def from_json(json: dict):
        return RandomTargets(AbstractEffect.from_json(json["effect"]), Numeric.from_json(getordef(json, "sample", 1)))
    def __str__(self):
        return f"{str(self.effect)} on up to {self.sample} random units among the targets."

@dataclass
class ChangeState(AbstractEffect):
    "Change the target(s) state to `new_state`."
    new_state: State
    def execute(self, **kwargs) -> bool:
        has_worked: bool = False
        for card in AbstractEffect.targeted_objects(**kwargs):
            if self.new_state == State.unattacked:
                if card.attacked:
                    card.attacked = False
                    has_worked = True
                continue
            # stronger `State`s cannot be overriden by weaker `State`s
            if card.state.value < self.new_state.value or self.new_state == State.default:
                has_worked = True
                card.state = self.new_state
        return has_worked
    def from_json(json: dict):
        effect = ChangeState(State.from_str(json["new_state"]))
        if "for" in json:
            return EffectUnion(effect, DelayEffect(ChangeState(State.default), json["for"], {}, (*getordef(json, "tags", ("+-")),))) # feature not bug
        return effect
    def __str__(self) -> str:
        return f"a change of state of the target⋅s to {self.new_state.name}"

@dataclass
class DamageEffect(AbstractEffect):
    "Does damage to the target(s), depending on DamageMode."
    amount: Numeric
    damage_mode: DamageMode = DamageMode.direct
    def execute(self, **kwargs) -> bool:
        kwargs = kwargs.copy()
        if kwargs["user"].state != State.monotonous:
            kwargs["damage_mode"] = self.damage_mode
        for card in AbstractEffect.targeted_objects(**kwargs):
            # nobody answered so I'll consider it a feature.
            kwargs["survey"].damage += card.damage(
                self.amount.eval(**kwargs) * 10 // ifelse(kwargs["user"].state == State.cloudy, 12, 10),
            **kwargs)
        return False
    def from_json(json: dict):
        return DamageEffect(Numeric.from_json(json["amount"]), DamageMode.from_str(getordef(json, "damage_mode", "indirect")))
    def __str__(self) -> str:
        return f"{self.amount} {self.damage_mode.to_str()} damage"

@dataclass
class DOTEffect(AbstractEffect):
    "Affect the target(s) with Damage Over Time, dealing `self.damage` over the *total* duration of the effect."
    damage: Numeric  # evalued once.
    turn: Numeric  # evalued once.
    def pcopy(self, **kwargs):
        "Pseudo copy of self: evaluate fields with `kwargs` before copying."
        return DOTEffect(RawNumeric(self.damage.eval(**kwargs)), RawNumeric(self.turn.eval(**kwargs)))
    def from_json(json: dict):
        return DOTEffect(Numeric.from_json(json["damage"]), Numeric.from_json(json["time"]))
    def execute(self, **kwargs) -> bool:
        for target in AbstractEffect.targeted_objects(**kwargs):
            target.effects.append(self.pcopy())
        return True
    def endturn(self, target):
        amount = self.damage.value // self.turn.value
        self.damage.value -= amount
        self.turn.value -= 1
        target.indirectdamage(amount)
        return self.turn.value > 0
    def __str__(self) -> str:
        return f"{self.damage} damage over {self.turn} turns"
    def get_tags(self): return ("-")

@dataclass
class LoopEffect(AbstractEffect):
    "Apply the effect at the end of each turn while the one applying it is not defeated, unless `self.infinite` is set to `True`, then the effect is applied at the end of every turn."
    effect: AbstractEffect
    infinite: bool
    kwargs: dict
    tags: tuple
    def with_kwargs(self, kwargs: dict):
        return LoopEffect(self.effect, self.infinite, kwargs, self.tags)
    def from_json(json: dict):
        return LoopEffect(AbstractEffect.from_json(json["effect"]), getordef(json, "infinite", False), {}, getordef(json, "tags", ("+-")))
    def execute(self, **kwargs) -> bool:
        for target in AbstractEffect.targeted_objects(**kwargs):
            target.effects.append(self.with_kwargs(kwargs))
        return True
    def endturn(self, target) -> bool:
        if (not self.infinite) and (self.kwargs["user"].state == State.discarded):
            return False
        self.kwargs["main_target"] = target
        self.kwargs["target_mode"] = TargetMode.target
        self.effect.execute(**self.kwargs)
        return True
    def __str__(self):
        if self.infinite:
            return f"{str(self.effect)} at the end of each turn, until the target dies out"
        return f"{str(self.effect)} at the end of each turn, until the user dies out"
    def get_tags(self): return self.tags

@dataclass
class DelayEffect(AbstractEffect):
    effect: AbstractEffect
    time: int  # doesn't support Numeric as it would be kinda useless.
    kwargs: dict
    tags: tuple
    def with_kwargs(self, kwargs: dict):
        return DelayEffect(self.effect, self.time, kwargs, self.tags)
    def from_json(json: dict):
        return DelayEffect(AbstractEffect.from_json(json["effect"]), json["delay"], {}, getordef(json, "tags", ("+-")))
    def execute(self, **kwargs) -> bool:
        for target in AbstractEffect.targeted_objects(**kwargs):
            target.effects.append(self.with_kwargs(kwargs))
        return True
    def endturn(self, target) -> bool:
        if self.time > 0:
            self.time -= 1
            return True
        self.kwargs["main_target"] = target
        self.kwargs["target_mode"] = TargetMode.target
        self.effect.execute(**self.kwargs)
        return False
    def __str__(self):
        return f"{str(self.effect)} after {self.time} turns"

@dataclass
class CleanseEffect(AbstractEffect):
    by_tags: tuple
    def execute(self, **kwargs):
        for target in AbstractEffect.targeted_objects(**kwargs):
            if "+" in self.by_tags and target.state in [State.damageless]:
                target.state = State.default
            if "-" in self.by_tags and target.state in [State.blocked, State.cloudy, State.monotonous]:
                target.state = State.default
            if "+-" in self.by_tags and target.state in [State.invisible]:
                target.state = State.default
            target.effects = [effect for effect in target.effects if hasany(effect.get_tags(), self.by_tags)]
        return True
    def from_json(json: dict):
        return CleanseEffect(getordef(json, "by_tags", ("+", "-", "+-")))
    def __str__(self):
        return f"cleanse effects tagged {self.by_tags}"

@dataclass
class DamageDrain(AbstractEffect):
    "Heal for a ratio (rational) of total damage (indirect/direct) "
    numerator: int
    # doesn't support numeric as Rational are quite too complex to be worked with.
    denominator: int
    effect: AbstractEffect
    def execute(self, **kwargs) -> bool:
        alt_kwargs: dict = kwargs.copy()  # could Python work correctly sometimes?
        alt_kwargs["survey"] = EffectSurvey()
        has_worked = self.effect.execute(**alt_kwargs)
        alt_kwargs["survey"].heal += alt_kwargs["user"].heal(
            self.numerator * alt_kwargs["survey"].damage // self.denominator)
        kwargs["survey"] += alt_kwargs["survey"]
        return has_worked
    def from_json(json: dict):
        return DamageDrain(json["num"], json["den"], AbstractEffect.from_json(json["effect"]))
    def __str__(self):
        return f"heal {self.numerator}/{self.denominator} of damage dealt from {str(self.effect)}"

@dataclass
class HealEffect(AbstractEffect):
    "Heal target(s) by amount."
    amount: Numeric
    def execute(self, **kwargs) -> bool:
        amount = self.amount.eval(**kwargs)  # eval once for every target.
        for card in AbstractEffect.targeted_objects(**kwargs):
            kwargs["survey"].heal += card.heal(amount)
        return False  # will use check from survey.
    def from_json(json: dict):
        return HealEffect(Numeric.from_json(json["amount"]))
    def __str__(self):
        return f"a healing of {self.amount}"

@dataclass
class WithProbability(AbstractEffect):
    "Apply either `self.effect1` or `self.effect2` such that `self.effect1` has `self.probability` to happen."
    probability: float  # no Numeric as Int only.
    effect1: AbstractEffect
    effect2: AbstractEffect = NullEffect()
    def execute(self, **kwargs) -> bool:
        if rng.rand() < self.probability:
            return self.effect1.execute(**kwargs)
        return self.effect2.execute(**kwargs)
    def from_json(json: dict):
        return WithProbability(getordef(json, "probability", 0.5), AbstractEffect.from_json(json["effect1"]), AbstractEffect.from_json(getordef(json, "effect2", "null")))
    def __str__(self):
        return f"{str(self.effect1)} {int(100.0*self.probability)}% of the time, {self.effect2} otherwise"

@dataclass
class EnergyEffect(AbstractEffect):
    "Adds (or remove) to the user's Player, energy, max_energy and energy_per_turn."
    energy: Numeric
    max_energy: Numeric
    energy_per_turn: Numeric
    def execute(self, **kwargs) -> bool:
        Δmax_energy = self.max_energy.eval(**kwargs)
        kwargs["player"].max_energy += Δmax_energy
        Δenergy_per_turn = self.energy_per_turn.eval(**kwargs)
        kwargs["player"].energy_per_turn += Δenergy_per_turn
        return (kwargs["player"].add_energy(self.energy.eval(**kwargs)) > 0) | (Δenergy_per_turn > 0) | (Δmax_energy > 0)
    def from_json(json: dict):
        return EnergyEffect(
            Numeric.from_json(getordef(json, "gain", 0)),
            Numeric.from_json(getordef(json, "max", 0)),
            Numeric.from_json(getordef(json, "per_turn", 0))
        )
    def __str__(self):
        # TODO: find prettier way to write this.
        return f"an increase of {self.energy} energy, {self.max_energy} maximum energy & {self.energy_per_turn} per turn"

@dataclass
class SummonEffect(AbstractEffect):
    "Summon up to `count` Creatures on random spots of the board, if possible."
    count: int
    summon: any  # summon is CreatureCard, I cannot annotate because Python. Why on earth do you have to annote type with a function though? Who had this terrible idea?
    def execute(self, **kwargs) -> bool:
        valids = [i for i in range(
            len(kwargs["player"].active)) if kwargs["player"].active[i] is None]
        if len(valids) == 0:
            return False
        rng.shuffle(valids)
        while len(valids) > self.count:
            valids.pop()
        for i in valids:
            kwargs["player"].active[i] = ActiveCard(
                self.summon, kwargs["player"], kwargs["board"])
            kwargs["board"].logs.append(f"-summon|{kwargs['player'].active[i].namecode()}|{self.summon.name}|{self.summon.max_hp}|{self.summon.element.value}")
        return True
    def from_json(json: dict):
        return SummonEffect(getordef(json, "count", 1), CreatureCard.from_json(json["creature"], 1j))
    def __str__(self):
        return f"summoning of {ifelse(self.count == 1, 'a', str(self.count))} {self.summon.name}"

@dataclass
class BoardResize(AbstractEffect):
    'Add `self.delta` spot to the targeted player (either `"active"` or `"unactive"`), but never decrease below 1 nor delete a card to reduce boardsize.'
    delta: int
    target: str
    def execute(self, **kwargs):
        match self.target:
            case "active": player = kwargs["board"].active_player
            case "unactive": player = kwargs["board"].unactive_player
            case _: return warn(f'Invalid target in BoardResize: excepted "ative" or "unactive" got "{self.target}"') and False
        # TODO: boarddiscard first.
        boardsize = max(len(player.active) + self.delta, 1)
        if self.delta < 0:
            while boardsize < len(player.active) and None in player.active:
                player.active.remove(None)
        else:
            while len(player.active) < boardsize:
                player.active.append(None)
        # TODO: fix return, logging and update replay.py
        return True
    def from_json(json: dict):
        return BoardResize(json["delta"], getordef(json, "target", "unactive"))
    def __str__(self):
        return f"remove {-self.delta} from the {self.target} player's board"
    

@dataclass
class HypnotizeEffect(AbstractEffect):
    "Change the target∙s teams to the user's owner, if possible."
    def execute(self, **kwargs) -> bool:
        valids = [i for i in range(
            len(kwargs["user"].owner.active)) if kwargs["user"].owner.active[i] is None]
        if len(valids) == 0:
            return False
        rng.shuffle(valids)
        for target in AbstractEffect.targeted_objects(**kwargs):
            if len(valids) == 0:
                break
            i = -1
            for j in range(len(target.owner.active)):
                if target.owner.active[j] is target:
                    i = j
                    break
            if i == -1:
                return False and warn("Hypnotization couldn't find the index of the target.")
            ppos = target.namecode() # logging
            target.owner.active[j] = None
            # I could have just done kwargs["player"] but it seems safer this way.
            target.owner = kwargs["user"].owner
            kwargs["user"].owner.active[valids.pop()] = target
            kwargs["board"].logs.append(f"-hypno|{ppos}|{target.namecode()}")
        return True
    def from_json(_):
        return HypnotizeEffect()
    def __str__(self):
        return "hypnotizing target∙s"

@dataclass
class RepeatEffect(AbstractEffect):
    "Repeat the effect `n` times, on the same targets. Simply more convenient than HUGE chain of union, but may be deleted later."
    n: Numeric
    effect: AbstractEffect
    def execute(self, **kwargs) -> bool:
        return np.any([self.effect.execute(**kwargs) for _ in range(self.n.eval(**kwargs))])
    def from_json(json: dict):
        return RepeatEffect(Numeric.from_json(json["n"]), AbstractEffect.from_json(json["effect"]))
    def __str__(self):
        return str(self.effect) + f"{self.n} times"

@dataclass
class FormeChange(AbstractEffect):
    "Change the target(s)'s card to a new CreatureCard object." 
    new_forme: any
    def execute(self, **kwargs) -> bool:
        actives = AbstractEffect.targeted_objects(**kwargs)
        for active in actives:
            active.card = self.new_forme  # active.card shouldn't be mutated, so there is no need to copy.
            active.element = self.new_forme.element
            kwargs["board"].logs.append(f"-formechange|{active.namecode()}|{active.card.name}|{active.hp}/{active.card.max_hp}|{active.element.value}")
        return len(actives) != 0
    def from_json(json: dict):
        return FormeChange(CreatureCard.from_json(json["new_forme"], 1j))
    def __str__(self):
        return f"change the target(s) forme to {self.new_forme.name}"

@dataclass
class TauntTargets:
    "Force the target(s) to attack a random creature among the `new_targets` distribution during `duration` turns"
    new_targets: TargetMode
    duration: Numeric
    def execute(self, **kwargs) -> bool:
        new_targets = AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", self.new_targets))
        if len(new_targets) == 0:
            return False
        targets = AbstractEffect.targeted_objects(**kwargs)
        for target in targets:
            target.taunt = rng.choice(targets)
            target.taunt_dur = self.duration
        return True
    def from_json(json: dict):
        return TauntTargets(TargetMode.from_str(json["new_targets"]), json["duration"])
    def __str__(self):
        return f"taunt the targets for {self.duration} turns"

class PassiveTrigger(IntEnum):
    endofturn = 0    # main_target => self
    whenplaced = 1   # main_target => self
    whendefeated = 2 # main_target => attacker / only work when defeated by attack (feature not bug)
    whenattack = 3   # same kwargs as attack
    whenattacked = 4 # main_target => atatcker
    whendamaged = 5  # main_target => self
    never = 6        # to hardcode
    # Must improve code before implementing those:
    whendiscarded = 7  # main_target => allied_commander
    whendrawn = 8  # main_target => allied_commander
    def from_str(name: str):
        match cleanstr(name):
            case "endofturn": return PassiveTrigger.endofturn
            case "whenplaced": return PassiveTrigger.whenplaced
            case "whendefeated": return PassiveTrigger.whendefeated
            case "whenattack": return PassiveTrigger.whenattack
            case "whenattacking": return PassiveTrigger.whenattack
            case "never": return PassiveTrigger.never
    def to_str(self):
        match self:
            case PassiveTrigger.endofturn: return "the turn end"
            case PassiveTrigger.whenplaced: return "placed"
            case PassiveTrigger.whendefeated: return "defeated"
            case PassiveTrigger.whenattack: return "attacking"

@dataclass
class Passive:
    name: str
    trigger: PassiveTrigger
    effect: AbstractEffect
    def from_json(json: dict):
        if not isinstance(json, dict):
            warn(json)
        if not "trigger" in json:
            warn(f"Passive with name {json['name']} has no trigger.")
        return Passive(
                       getordef(json, "name", ""),
                       PassiveTrigger.from_str(json["trigger"]),
                       AbstractEffect.from_json(getordef(json, "effect", {"type": "null"}))
        )
    def execute(self, **kwargs): return self.effect.execute(**kwargs)
    def __str__(self):
        return f"{self.name} does {str(self.effect)} when {self.trigger.to_str()}."


@dataclass
class Attack:
    name: str
    power: int
    target_mode: TargetMode
    cost: int
    effect: AbstractEffect  # use EffectUnion for multiple Effects
    tags: tuple = ()
    def from_json(json: dict):
        if "target_mode" not in json:
            warn(f"{json['name']} has no target mode.")
        attack = Attack(
            getordef(json, "name", ""),
            int(json["power"]),  # no float in power
            TargetMode.from_str(json["target_mode"]),
            int(json["cost"]),
            AbstractEffect.from_json(getordef(json, "effect", "null")),
            (*getordef(json, "tags", ()),)
        )
        if "tag" in json:
            attack.tags = (*attack.tags, json["tag"])
        return attack
    def log(self, **kwargs):
        if "spell" in self.tags:
            log = f"spell|{kwargs['user'].card.name}|{kwargs['main_target'].namecode()}|{self.target_mode.value}|{kwargs['survey'].return_code.value}"
        else:
            log = f"attack|{kwargs['user'].namecode()}|{self.name}|{kwargs['main_target'].namecode()}|{self.target_mode.value}|{kwargs['survey'].return_code.value}"
        kwargs["board"].logs.append(log)
        return kwargs["survey"]
    def __str__(self) -> str:
        "Return a verbal representation of self."
        s = f"{self.name} (cost:{str(self.cost)}"
        for tag in self.tags:
            s += f" #{tag}"
        s += f") targets {self.target_mode.to_str()} "
        if self.power != 0:
            s += f"dealing {self.power} damages and "
        s += f"doing {str(self.effect)}"
        return s


@dataclass
class AbstractCard:
    name: str
    id: int
    # all card types until now have an element; if a new card type doesn't require an element, we'll force the element field to Element.elementless in the from_json constructor (which allows flexibility with Element.efective).
    element: Element
    def __init__(self, *args):
        warn("AbstractCard class serves only as a superclass; initialize object of more specific classes instead.")
    def from_json(json: dict, id: int):  # id from index in list
        "Dispatch the from_json method according to \"type\" field. The method hence doesn't return an AbstractCard object."
        type = json["type"]
        if type == "creature":
            return CreatureCard.from_json(json, id)
        if type == "spell":
            return SpellCard.from_json(json, id)
        warn(
            f"Card with name {json['name']} has type {type} which isn't handled.")
    # Method is inherited to every subclass.
    def copy(self):
        "Self explanatory."
        # a bit spaghetti coded but I can't really do better because Python. TODO: copy recursively to avoid sharing completely
        return type(self)(**vars(self))
    # in case we can't know if the card is a Creature or not, it avoids a crash.
    def iscommander(self) -> bool: return False
    @property # why does this even exist?
    def ui_id(self) -> str:
        "Formatted name of the card, used by the UI."
        return format_name_ui(self.name, self.element)
    def from_id(ui_id: str):
        "Return an AbstractCard object with the corresponding UI Id or None if it doesn't exist. Match commanders as well."
        for card in getCARDS() + list(getCOMMANDERS().values()):
            if card.ui_id == ui_id:
                return card

@dataclass
class CreatureCard(AbstractCard):
    max_hp: int
    attacks: list[Attack]  # list of Attack objects
    passives: list[Passive]
    cost: int
    tags: tuple[str]
    def from_json(json: dict, id: int):
        "Initialize either a CreatureCard object or a CommanderCard object depending on \"commander\" field with every field filled from the JSON (Python) dict passed in argument."
        args = [
            json["name"],
            id,
            Element.from_json(json),
            int(json["hp"]),
            [Attack("Default Attack", ifelse(getordef(json, "commander", False), Constants.commander_power, Constants.base_power + json["cost"]*Constants.power_increase),
                TargetMode.target, ifelse(
                 getordef(json, "commander", False), 1, 0), NullEffect(), ("default",)),
                *(Attack.from_json(attack) for attack in getordef(json, "attacks", []))],
            [Passive.from_json(passive)
             for passive in getordef(json, "passives", [])],
            json["cost"],
            (*getordef(json, "tags", ()),)
        ]
        if "tag" in json:
            args[7] = (*args[7], json["tag"])
        if cleanstr(json["name"]) == "bobtheblobfish":
            args[4][0] = Attack("Splish-Splosh", 0,
                                TargetMode.self, 0, NullEffect(), ("useless"))
        # so we don't need to define "commander":false for every card (might be changed later to "type":"commander" though).
        if getordef(json, "commander", False):
            return CommanderCard(*args)
        if len(args[4]) == 1:
            args[4].append(Attack("Prayer", 0, TargetMode.target,
                           1, HealEffect(30), tags=("heal")))
        return CreatureCard(*args)
    def __str__(self) -> str:
        "Return a 'beautiful' string reprensenting self instead of ugly mess defaulting from dataclasses."
        pretty = f"{self.name} (id:{self.id}): {self.element.to_str()}\nMax HP: {self.max_hp}\nCost: {self.cost}\nAttacks:"
        for attack in self.attacks:
            pretty += "\n- " + str(attack)
        pretty += "\nPassives:"
        for passive in self.passives:
            pretty += "\n- " + str(passive)
        return pretty
    def image_file(self) -> str:
        "Return the directory to self's image"
        fname: str = f"{self.element.name}-{cleanstr(self.name)}.png"
        if not fname in os.listdir("assets/cards/"):
            return "assets/cards/NOFILE.png"
        return "assets/cards/" + fname
    def get_cost(self) -> int:
        return self.cost

@dataclass
class CommanderCard(CreatureCard):
    def iscommander(self) -> bool: return True

class Player:
    pass  # necessary 'cause Python

class Board:
    pass

@dataclass
class ActiveCard:
    card: CreatureCard
    hp: int
    element: Element  # to change active element after a specific effect
    owner: Player
    board: Board
    effects: list[AbstractEffect]
    attacked: bool
    state: State
    taunt: None # or ActiveCard but I can't annotate thanks to Python
    taunt_dur: int
    def __init__(self, card: CreatureCard, owner: Player, board: Board):
        self.card = card
        self.hp = card.max_hp
        self.element = card.element
        self.owner = owner
        self.board = board
        self.effects = []
        self.attacked = False
        self.state = State.default
        self.taunt = None
        self.taunt_dur = 0
    def can_attack(self):
        if self.state in [State.blocked, State.invisible]:
            return False
        if self.iscommander() and np.any([card is not None for card in self.owner.active]):
            return False
        if self.board is None or self.owner != self.board.active_player:
            return False
        return not self.attacked
    def attack(self, attack: Attack, target, **kwargs) -> EffectSurvey:
        "Make `self` use `attack` on `other`, applying all of its effects, and return a EffectSurvey object (containing total damage and healing done)."
        getorset(kwargs, "survey", EffectSurvey())
        getorset(kwargs, "user", self)
        getorset(kwargs, "main_target", target)
        getorset(kwargs, "board", self.board)
        if self.board.active_player != self.owner:
            kwargs["survey"].return_code = ReturnCode.wrong_turn
            return kwargs["survey"] # doesn't act if it can't
        if (not self.can_attack() and not "ultimate" in attack.tags) or target.state in [State.invisible, State.damageless]:
            kwargs["survey"].return_code = ReturnCode.cant
            return kwargs["survey"]
        if "ultimate" in attack.tags and self.owner.commander_charges < attack.cost:
            kwargs["survey"].return_code = ReturnCode.charging
            return kwargs["survey"]
        elif "ultimate" not in attack.tags and self.owner.energy < attack.cost:
            kwargs["survey"].return_code = ReturnCode.no_energy
            return kwargs["survey"]
        getorset(kwargs, "player", self.owner)
        getorset(kwargs, "target_mode", attack.target_mode)
        getorset(kwargs, "damage_mode", ifelse(self.state == State.monotonous, DamageMode.ignore_se, DamageMode.direct))
        if self.taunt is not None:
            if self.taunt.hp <= 0 or self.taunt_dur <= 0:
                self.taunt = None
            else:
                # Note that AOE attack are mostly unchanged.
                kwargs["main_target"] = self.taunt
                self.taunt_dur -= 1
        if self.state == State.cloudy: # overrides taunt
            if len(AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", TargetMode.foes))) == 0:
                kwargs["target_mode"] = TargetMode.commander
                kwargs["main_target"] = kwargs["board"].unactive_player.commander
            else:
                kwargs["target_mode"] = TargetMode.target
                kwargs["main_target"] = rng.choice(AbstractEffect.targeted_objects(**withfield(kwargs, "target_mode", TargetMode.foes)))
        #= Gravitational Lensing - start =#
         # overrides everything
         # wait I just realized it redirects 65535-damage attacks.
         # "Feature not bug"
        if self.board.unactive_player.commander.card is getCOMMANDERS()["vafisorg"]:
            kwargs["main_target"] = self.board.unactive_player.commander
        #= Gravitational Lensing - end =#
        if len(AbstractEffect.targeted_objects(**kwargs)) == 0:
            kwargs["survey"].return_code = ReturnCode.no_target
            return kwargs["survey"]
        attack.log(**kwargs) # log before damages.
        for card in AbstractEffect.targeted_objects(**kwargs):
            kwargs["survey"].damage += card.damage(attack.power, **kwargs)
            for passive in card.card.passives:
                if passive.trigger != PassiveTrigger.whenattack:
                    continue
                passive.execute(**kwargs)
        if not attack.effect.execute(**kwargs) and (kwargs["survey"].damage == 0) and (kwargs["survey"].heal == 0):
            kwargs["survey"].return_code = ReturnCode.failed
            return kwargs["survey"]
        for passive in self.card.passives:
            if passive.trigger != PassiveTrigger.whenattack:
                continue
            passive.execute(**kwargs)
        if "ultimate" in attack.tags:
            self.owner.commander_charges -= attack.cost
        else:
            self.owner.add_energy(-attack.cost)
            self.owner.commander_charges += kwargs["survey"].damage
        # logged in both cases
        self.board.logs.append(f"-ccharge|{self.owner.namecode()}|{self.owner.commander_charges}")
        for card in self.board.unactive_player.boarddiscard() + self.board.active_player.boarddiscard():
            # must be improved to apply passive of card defeated by passives or other sources
            # nah actually that's a feature.
            card.defeatedby(self)
        self.attacked = True
        return kwargs["survey"]
    def defeatedby(self, killer):
        kwargs = {
            "player": self.owner,
            "board": self.board,
            "main_target": killer,
            "damage_mode": DamageMode.indirect,
            "target_mode": TargetMode.target,
            "user": self,
            "survey": EffectSurvey()
        }
        for passive in self.card.passives:
            if passive.trigger != PassiveTrigger.whendefeated:
                continue
            passive.execute(**kwargs)
    def iscommander(self):
        return self.card.iscommander()
    def namecode(self):
        if self.iscommander():
            return self.owner.namecode() + '@'
        for i in range(len(self.owner.active)):
            if i > 25:
                warn("Board size is unsupported, causing logging issues.")
                self.board.logs.append("raw|Warning: board size is unsupported, causing logging issues.")
                return self.owner.namecode() + '@' # may be fixed later.
            if self.owner.active[i] is self:
                return self.owner.namecode() + chr(97 + i)
    def damage(self, amount, **kwargs) -> int:
        "Does damage to self, modified by any modifiers. `kwargs` must contain damage_mode & user"
        mode = getordef(kwargs, "damage_mode", DamageMode.direct)
        if mode == DamageMode.indirect:
            amount = self.indirectdamage(amount)
            for passive in self.card.passives:
                if passive.trigger != PassiveTrigger.whendamaged:
                    continue
                passive.execute(**withfield(kwargs, "damage_taken", amount))
            return amount
        attacker = kwargs["user"]
        amount *= ifelse(mode.can_strong()
                         and attacker.element.effectiveness(self.element), 12, 10)
        amount //= ifelse(mode.can_weak()
                          and self.element.resist(attacker.element), 12, 10)
        if self.card.iscommander() and mode.can_weak():
            amount = amount * (100 - 8 * len(self.owner.get_actives())) // 100
        amount = self.indirectdamage(amount)
        for passive in self.card.passives:
            if passive.trigger != PassiveTrigger.whendamaged:
                continue
            passive.execute(**withfield(kwargs, "damage_taken", amount))
        return amount
    def indirectdamage(self, amount: int) -> int:
        "Reduce HP by amount but never goes into negative, then return damage dealt."
        if self.state == State.damageless:
            return 0
        if DEV() and type(amount) != int:
            warn(f"Card with name \"{self.card.name}\" took non integer damages; converting value to int. /!\\ PLEASE FIX: automatic type conversion is disabled when out of DEV mode /!\\")
            amount = int(amount)
        if amount > self.hp:
            amount = self.hp
        self.hp -= amount
        self.board.logs.append(f"-damage|{self.namecode()}|{self.hp}/{self.card.max_hp}")
        return amount
    def heal(self, amount: int) -> int:
        "Heal `self` from `amount` damage while never overhealing past max HP and return amount healed."
        if DEV() and type(amount) != int:
            warn(f"Card with name \"{self.name}\" healed from non integer damages; converting value to int. /!\\ PLEASE FIX: automatic type conversion is disabled when out of DEV mode /!\\")
            amount = int(amount)
        amount = min(self.card.max_hp - self.hp, amount)
        self.hp += amount
        self.board.logs.append(f"-heal|{self.namecode()}|{self.hp}/{self.card.max_hp}")
        return amount
    def endturn(self):
        "Apply all effects at the end of turn."
        self.effects = [
            effect for effect in self.effects if effect.endturn(self)]
        kwargs = {
            "player": self.owner,
            "board": self.board,
            "main_target": self,
            "damage_mode": DamageMode.indirect,
            "target_mode": TargetMode.self,
            "user": self,
            "survey": EffectSurvey()
        }
        for passive in self.card.passives:
            if passive.trigger != PassiveTrigger.endofturn:
                continue
            passive.execute(**kwargs)
        if not self.attacked:
            self.heal(ifelse(self.card.iscommander(), Constants.commander_heal, Constants.passive_heal))
        self.attacked = False

@dataclass
class SpellCard(AbstractCard):
    on_use: Attack
    def from_json(json: dict, id: int):
        on_use = Attack.from_json(json["on_use"])
        on_use.tags = (*on_use.tags, "spell")
        return SpellCard(json["name"], id, Element.from_str(json["element"]), on_use)
    def use(self, target: ActiveCard):
        board = target.board
        sim = ActiveCard(
            CreatureCard(name=self.name, id=self.id, element=self.element, max_hp=0, attacks=[
                         self.on_use], passives=[], cost=0, tags=("spell")),
            board.active_player, board
        )
        survey = sim.attack(self.on_use, target)
        if survey.return_code == ReturnCode.ok:
            board.active_player.iddiscard(self.id)
        return survey
    def __str__(self):
        return f"(Spell) {self.name} (id:{self.id}): {self.element.name}\nOn use: {str(self.on_use)}"
    def image_file(self) -> str:
        "Return the directory to self's image"
        fname: str = f"spell-{self.element.name}-{cleanstr(self.name)}.png"
        if not fname in os.listdir("assets/cards/"):
            return "assets/cards/NOFILE.png"
        return "assets/cards/" + fname
    def get_cost(self) -> int:
        return self.on_use.cost

class Arena(IntEnum):
    smigruv = 0
    himinnsokva = 1
    jordros = 2
    watorvarg = 3
    chaos = 4
    def image_file(self):
        match self:
            case Arena.chaos: return "assets/chaos-arena.jpg"
            case arena: return f"assets/{arena.name}-arena.png"
    def has_effect(self, other):
        "Return whether self has the same effect Arena effect as other."
        # hardcoded so that chaos always has the effects of all other arenas.
        return (self == other) or (self == Arena.chaos)

@dataclass # for display
class Player:
    name: str
    commander: ActiveCard
    deck: list[AbstractCard]
    discard: list[AbstractCard]
    hand: list[AbstractCard]
    energy: int
    max_energy: int
    energy_per_turn: int
    active: list[ActiveCard | None]
    commander_charges: int
    def __init__(self, name: str, commander: CommanderCard, deck: list[AbstractCard] = []):
        #if len(deck) != Constants.default_deck_size:
        #    warn("Tried to initialize a Player with an invalid deck; deck validity should be checked before initialization; deck remplaced by a default one.")
        #    deck = Player.get_deck()
        self.name = name
        self.commander = ActiveCard(commander, self, None)
        # avoid sharing, notably if deck is left to default in DEV() mode, as Python is a terrible language
        # this also helps to reset the deck in case of summon/forme change
        self.deck = deck.copy()
        rng.shuffle(self.deck)
        self.discard = []  # is not shared
        self.hand = []
        self.energy = Constants.default_energy_per_turn
        self.max_energy = Constants.default_max_energy
        self.energy_per_turn = Constants.default_energy_per_turn
        self.active = []
        self.commander_charges = 0
    def get_commander(*_) -> CommanderCard:
        # yes, it's ugly, it's Python
        return getCOMMANDERS()[rng.choice([*getCOMMANDERS()])]
    def get_deck(*_) -> list[AbstractCard]:
        return [*rng.choice(getCARDS(), Constants.default_deck_size)]
    def get_actives(self) -> list[ActiveCard]:
        return [card for card in self.active if card is not None]
    def get_actives_json(self) -> list[None | dict]:
        actives = []
        for card in self.active:
            if card is None:
                actives.append(None)
                continue
            actives.append({
                "name":card.card.name,
                "hp":card.hp,
                "element":card.element.value,
                "max_hp":card.card.max_hp
            })
        return actives
    def isai(self) -> bool: return False
    def card_id(name: str) -> int:
        for card in getCARDS():
            if cleanstr(card.name) == cleanstr(name):
                return card.id
        # I'm way to lazy to check whether the returned value is valid, so I just return a valid value in case the card doesn't exist.
        return np.sum([ord(c) for c in cleanstr(name)]) % len(getCARDS())
    def get_save_json(name: str) -> dict | None:
        "Try to fetch & return a player witht he same name from `Data/player.json` as a `dict`, returning None if it isn't found."
        fname = cleanstr(name)
        io = open(os.path.join(Constants.path, "Data/players.json"))
        players: dict = loads(io.read())
        io.close()
        if fname not in players:
            return None
        return players[fname]
    def from_json(name: str, json: dict):
        return Player(name, getCOMMANDERS()[json["commander"]], [getCARDS()[Player.card_id(i)] for i in json["deck"]])
    def from_save(name: str):
        "Try to fetch & return a player with the same name from `Data/players.json` as a `Player` object, returning a random player if it isn't found."
        player = Player.get_save_json(name)
        if player is None:
            warn(f"Player with name {name} was not found in `players.json`, returning default deck.")
            return Player(name, Player.get_commander(), Player.get_deck())
        return Player.from_json(name, player)
    def from_saves(name: str, saves: dict):
        return Player.from_json(name, saves[name])
    def save(self):
        self.reset()
        io = open(os.path.join(Constants.path, "Data/players.json"), "r+")
        players: dict = loads(io.read())
        userdata: dict = {cleanstr(self.name): {
            "commander": cleanstr(self.commander.card.name),
            "deck": [cleanstr(card.name) for card in self.deck],
        }}
        players.update(userdata)
        io.truncate(0)
        io.write(dumps(userdata, separators=(',', ':')))
        io.close()
        return players
    def singledraw(self) -> AbstractCard:
        if len(self.deck) == 0:
            # Seriously Python is it too hard to return the list after extending it so we can chain methods?
            self.deck.extend(self.discard)
            rng.shuffle(self.deck)
            self.commander.board.logs.append(f"shuffle|{self.namecode()}")
            self.discard.clear()
        card = self.deck.pop()
        self.commander.board.logs.append(f"draw|{self.namecode()}|{card.name}")
        return card
    def draw(self) -> list:
        # Please note that the top of the deck is the end of the self.deck list.
        new = [self.singledraw() for _ in range(Constants.default_hand_size + ifelse(
            self.commander.board.arena.has_effect(Arena.watorvarg), 1, 0) - len(self.hand))]
        self.hand.extend(new)
        return new  # to display drawing(s) on the GUI?
    def log_energy(self) -> str:
        "Append energy log to `self`'s board and return appended log."
        log = f"energy|{self.namecode()}|{self.energy}/{self.max_energy}|{self.energy_per_turn}"
        self.commander.board.logs.append(log)
        return log
    def add_energy(self, amount: int) -> int:
        "Add `amount` energy to self while never going above `self.max_energy` nor below 0."
        if amount < 0:
            amount = max(amount, -self.energy)
        else:
            amount = min(amount, self.max_energy - self.energy)
        self.energy += amount
        self.log_energy()
        return amount # used by effect survey
    def haslost(self) -> bool:
        "Return True is this Player's CommanderCard is defeated, False otherwise."
        if self.commander.hp <= 0:
            return True
        return False
    def handdiscard(self, i: int):
        "Discard the `i`th card in `self`'s `hand`, returning it."
        card = self.hand.pop(i)
        self.commander.board.logs.append(f"discard|{self.namecode()}|{card.name}")
        self.discard.append(card)
        return card
    def iddiscard(self, id: int):
        "Discard the first card in `self`'s `hand` with `id`, returning it."
        for i in range(len(self.hand)):
            if self.hand[i].id == id:
                return self.handdiscard(i)
    def namecode(self):
        "Return player code used for logging."
        if self.commander.board.player1 == self:
            return "p1"
        return "p2"
    def boarddiscard(self):
        "Discard every defeated cards, returning them."
        discards: list[ActiveCard] = []
        cards = self.active
        board = self.commander.board
        for i in range(len(cards)):
            if cards[i] is None:
                continue
            if cards[i].hp <= 0:
                cards[i].state = State.discarded
                discards.append(cards[i])
                self.discard.append(cards[i].card)
                board.logs.append(f"defeat|{cards[i].namecode()}")
                cards[i] = None
        return discards
    def place(self, i: int, j: int):
        board: Board = self.commander.board
        "Place the `i`th card of hand onto the `j`th tile of board, activing it. Return `True` if sucessful, `False` otherwise."
        if not 0 <= i < len(self.hand):
            return False
        if not 0 <= j < len(self.active):
            return False
        if self.active[j] is not None:
            return False
        if type(self.hand[i]) == SpellCard:
            return False
        if self.energy < self.hand[i].cost:
            return False
        self.add_energy(-self.hand[i].cost)
        self.active[j] = ActiveCard(self.hand.pop(i), self, board)
        kwargs = {
            "player": self,
            "board": board,
            "main_target": self.active[j],
            "damage_mode": DamageMode.indirect,
            "target_mode": TargetMode.self,
            "user": self.active[j],
            "survey": EffectSurvey()
        }
        # TODO: give important informations on card instead of just name.
        board.logs.append(f"place|{self.active[j].namecode()}|{self.active[j].card.name}|{self.active[j].card.max_hp}|{self.active[j].element.value}")
        for passive in self.active[j].card.passives:
            if passive.trigger != PassiveTrigger.whenplaced:
                continue
            passive.execute(**kwargs)
        return True
    def reset(self):
        self.deck.extend(self.hand)
        self.deck.exten(self.discard)
        self.hand.clear()
        self.discard.clear()
        self.commander = ActiveCard(
            self.commander.card, self, self.commander.board)

def rps2int(rpc: str):
    match rpc:
        case "rock": return 0
        case "r": return 0
        case "paper": return 1
        case "p": return 1
        case "scissor": return 2
        case "s": return 2
        case _: return rng.randint(0, 3)

@dataclass
class Board:
    player1: Player
    player2: Player
    # between 1 and 6 max active cards, chosen at random at the begining of every game.
    board_size: int
    active_player: Player
    unactive_player: Player
    turn: int
    arena: Arena
    autoplay: bool
    logs: list[str]
    def rps_win(player1: str, player2: str): # no idea why this is a method
        "Return `0` if player1 win Rock Paper Scissor against player2, `1` if player2 wins and `-1` if it's a draw."
        player1, player2 = rps2int(player1), rps2int(player2)
        if player1 == (player2 + 1) % 3:
            return 0
        if (player1 - 1) % 3 == player2:
            return 1
        return -1
    def __init__(self, player1: Player, player2: Player, autoplay: bool = True):
        self.logs = []
        self.active_player, self.unactive_player = player1, player2
        if DEV() and rng.random() < 0.5:  # Coinflip in DEV()-mode, must implement RPS in GUI- (and Omy-) mode
            self.active_player, self.unactive_player = self.unactive_player, self.active_player
        player1.commander.board = self
        player2.commander.board = self
        self.arena = Arena(rng.randint(5))
        if self.arena.has_effect(Arena.smigruv):
            player1.max_energy += 1
            player2.max_energy += 1
            player1.energy_per_turn += 1
            player2.energy_per_turn += 1
        self.player1 = player1
        self.player2 = player2
        self.board_size = rng.randint(
            1, 7) + ifelse(self.arena.has_effect(Arena.jordros), 1, 0)
        player1.active = [None for _ in range(self.board_size)]
        player2.active = self.player1.active.copy()
        self.unactive_player.energy += 1 # To compensate disadvantage
        self.turn = 0
        if len(player1.deck) != Constants.default_deck_size:
            warn(f"player1 ({player1.name})'s deck is not valid, giving random one instead.")
            player1.deck = Player.get_deck()
        if len(player2.deck) != Constants.default_deck_size:
            warn(f"player2 ({player2.name})'s deck is not valid, giving random one instead.")
            player2.deck = Player.get_deck()
        self.logs.append(f"player|p1|{self.player1.name}|{self.player1.commander.card.name}|{self.player1.commander.card.max_hp}|{self.player1.commander.element}")
        self.logs.append(f"player|p2|{self.player2.name}|{self.player2.commander.card.name}|{self.player2.commander.card.max_hp}|{self.player2.commander.element}")
        self.logs.append(f"boardsize|p1|{len(self.player1.active)}")
        self.logs.append(f"boardsize|p2|{len(self.player2.active)}")
        self.player1.add_energy(0) # to log energy
        self.player2.add_energy(0)
        player1.draw()
        player2.draw()
        self.autoplay = autoplay
        if autoplay and self.active_player.isai():
            self.active_player.auto_play(self)
    def getwinner(self) -> Player | None:
        if self.unactive_player.haslost():
            return self.active_player
        if self.active_player.haslost():
            return self.unactive_player
        return None
    def endturn(self) -> tuple[Player, int, list[AbstractCard], int, None | Player]:
        "End the turn returning (player_who_ends_turn: Player, energy_gained: int, card_drawn: list, current_turn: int, winner: None | Player)"
        winner = self.getwinner() # evaluate before healing
        for card in self.active_player.active:
            if card is None:
                continue
            card.endturn()
        self.active_player.commander.endturn()
        self.active_player, self.unactive_player = self.unactive_player, self.active_player
        self.turn += 1
        self.logs.append(f"turn|{self.turn}")
        ret = (self.unactive_player, self.unactive_player.add_energy(
            self.unactive_player.energy_per_turn), self.unactive_player.draw(), self.turn, winner)
        if ret[4] is not None:
            self.logs.append(f"win|{ret[4].namecode()}|{ret[4].name}")
        elif self.autoplay and self.active_player.isai():
            return self.active_player.auto_play(self) # can crash due to Python's stupid recursion limit
        return ret
    def get_replay(self):
        replay = ""
        for log in self.logs:
            replay += log + "\n"
        return replay.strip()
    def devprint(self):
        you = self.player1
        them = self.player2
        print(self.turn)
        print(f"{them.name}: {them.energy}/{them.max_energy} energies.")
        print(them.commander.card.name,
              f"({them.commander.hp}/{them.commander.card.max_hp})")
        for card in them.active:
            if card is None:
                print("none ", end="")
                continue
            print(cleanstr(card.card.name),
                  f"({card.hp}/{card.card.max_hp}) ", end="")
        print(f"\n\n{you.name}: {you.energy}/{you.max_energy} energies")
        print(you.commander.card.name,
              f"({you.commander.hp}/{you.commander.card.max_hp})")
        for card in you.active:
            if card is None:
                print("none ", end="")
                continue
            print(cleanstr(card.card.name),
                  f"({card.hp}/{card.card.max_hp}) ", end="")
        print()
        print([cleanstr(card.name) for card in you.hand])

class AIPlayer(Player): # I hate OOP
    def __init__(self):
        Player.__init__(self, self.get_name(),
                        self.get_commander(), self.get_deck())
    def get_name(*_) -> str: # allow self in argument
        return "You've probably made a mistake here cuz this AI isn't supposed to be used. Seriously fix this. NOW!"
    def auto_play(self, board: Board):
        warn(
            f"AI of type {type(self)} tried to play without algorithm; ending turn instead.")
        return board.endturn()
    def can_play(self):
        for active in self.get_actives():
            if not active.attacked:
                return True
        if not self.commander.attacked and self.energy >= 1 and len(self.get_actives()) == 0:
            return True
        if not np.any([card is None for card in self.active]):
            return False
        for card in self.hand:
            if card.get_cost() <= self.energy:
                return True
        return False
    def isai(self) -> bool: return True

class NaiveAI(AIPlayer):
    "Naive AI is an extremely simple AI that can barely play with some basic strategic thoughts, thinking as straigthforwardly & simply as possible."
    # goal is the energy NaiveAI will try to reach for next turn, allowing the AI to economize for more expensive cards.
    goal: int
    def __init__(self):
        AIPlayer.__init__(self)
        self.goal = 0
    def spendable(self) -> int:
        return self.energy + self.energy_per_turn - self.goal
    def naive_target_heal(self, board: Board):
        valids = [card for card in self.get_actives(
        ) if card.card.max_hp - card.hp > 29]
        if len(valids) == 0 or (rng.random() < 0.6 and self.commander.card.max_hp - self.commander.hp > 29):
            return self.commander
        return rng.choice(valids)
    def naive_target(self, board: Board, tags: tuple = ()) -> ActiveCard:
        if "heal" in tags:
            return self.naive_target_heal(board)
        valids = board.unactive_player.get_actives()
        if len(valids) == 0 or rng.random() < 0.5:
            return self.commander.board.unactive_player.commander
        return rng.choice(valids)
    def get_attackers(self) -> list[ActiveCard]:
        return [card for card in self.get_actives() if not card.attacked]
    def try_place(self, board: Board):
        valids = [i for i in range(
            len(self.hand)) if self.hand[i].get_cost() <= self.spendable()]
        if len(valids) == 0:
            return
        placeable = [j for j in range(
            len(self.active)) if self.active[j] is None]
        if len(placeable) == 0:
            return
        i: int = rng.choice(valids)
        if type(self.hand[i]) == SpellCard:
            return self.hand[i].use(self.naive_target(board, self.hand[i].on_use.tags))
        self.place(i, rng.choice(placeable))
    def try_attack(self):
        attackers = self.get_attackers()
        if len(attackers) == 0:
            return
        attacker: ActiveCard = rng.choice(attackers)
        attacks = [
            attack for attack in attacker.card.attacks if attack.cost <= self.spendable()]
        if len(attacks) == 0:
            return
        attack: Attack = rng.choice(attacks)
        target = self.naive_target(self.commander.board, attack.tags)
        attacker.attack(attack, target)
    def try_discard(self):
        valids = [card for card in self.hand if card.get_cost() >
                  self.max_energy]
        if len(valids) == 0:
            return
        self.iddiscard(rng.choice(valids).id)
    def auto_play(self, board: Board):
        self.goal = rng.randint(0, self.max_energy + 1)
        i: int = 0
        while self.can_play() and self.energy > self.goal:
            i += 1
            if i == 300:
                warn(
                    f"NaiveAI ({self.name}) couldn't find a way to end its turn. Force ending.")
                return board.endturn()
            (rng.random() < 1.0 - len(self.get_actives()) /
             len(self.active)) and self.try_place(board)
            self.try_attack()
        if len(self.hand) > 3 or rng.random() < 0.5:
            self.try_discard()
        for card in self.get_actives():
            valids: list[Attack] = [
                attack for attack in card.card.attacks if attack.cost == 0]
            if len(valids) == 0:
                continue
            attack: Attack = rng.choice(valids)
            card.attack(attack, board.unactive_player.commander)
        return board.endturn()
