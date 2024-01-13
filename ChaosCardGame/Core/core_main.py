from convenience import *  # makes code cleaner
from dataclasses import dataclass  # easier class declaration
from enum import IntEnum  # for clear, lightweight (int) elements/state.
from json import loads, dumps
from numpy import random as rng  # for shuffle function/rng effects
import numpy as np  # for gcd for Kratos card
import os

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
            case _: return warn("Wrong Numeric type in json.") and RawNumeric(0)

    def __str__(self) -> str:
        return f"UNDEFINED ({type(self)})"


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


class Constants:  # to change variables quickly, easily and buglessly.
    default_max_energy = 4
    default_energy_per_turn = 3
    default_hand_size = 5
    default_deck_size = 30


def getCARDS(CARDS=[]) -> list:
    "Return the list of every card defined in `./data/cards.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(CARDS) != 0:
        return CARDS
    io = open("data/cards.json", encoding="utf-8")
    json = loads(io.read())
    io.close()
    id = -1  # starts at -1 + 1 = 0
    CARDS += [AbstractCard.from_json(card, (id := id + 1)) for card in json]
    return CARDS


def getCOMMANDERS(COMMANDERS={}) -> dict:
    "Return a dict of every card defined `./data/commanders.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(COMMANDERS) != 0:
        return COMMANDERS
    io = open("data/commanders.json", encoding="utf-8")
    json = loads(io.read())
    io.close()
    id = -1
    COMMANDERS.update({cleanstr(card["name"]): CreatureCard.from_json(
        card, (id := id + 1)) for card in json})
    return COMMANDERS


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
    default = 0  # placeholder
    blocked = 1  # can't attack
    invisible = 2  # can't attack; can't be targeted
    discarded = 3  # for GUI
    damageless = 4  # can't take direct damage
    unattacked = 5  # set target.attacked to False without affecting self.state

    def from_str(name: str):
        match cleanstr(name):
            case "default": return State.default
            case "blocked": return State.blocked
            case "block": return State.blocked
            case "invisible": return State.invisible
            case "damageless": return State.damageless
            case "unattacked": return State.unattacked
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

    def from_str(name: str):
        match cleanstr(name):
            case "direct": return DamageMode.direct
            case "indirect": return DamageMode.indirect
            case "ignoreresist": return DamageMode.ignore_resist
            case "resistanceignoring": return DamageMode.ignore_resist
            case _: return warn(f"Tried to form DamageMode from {name}, returning DamageMode.direct instead.") and DamageMode.direct

    def to_str(self) -> str:
        match self:
            case DamageMode.direct: return "direct"
            case DamageMode.indirect: return "indirect"
            case DamageMode.ignore_resist: return "resistance-ignoring"

    def can_strong(self) -> bool:
        return self != DamageMode.indirect

    def can_weak(self) -> bool:
        return self == DamageMode.direct


class ReturnCode(IntEnum):
    ok = 200
    cant = 400
    no_energy = 401
    wrong_turn = 402
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
        # please save me from this language; the more I discover the more I ask myself why python is used.
        return self


class AbstractEffect:
    def __init__(self):
        warn("AbstractEffect class serves only as a superclass; initialize object of more specific classes instead.")

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
            case "repeat": return warn("RepeatEffect may be deprecated soon.") and RepeatEffect.from_json(json)
            # .from_json is useless but it allows more flexibility if we want to add something
            case "hypnotize": return HypnotizeEffect.from_json(json)
            case "summon": return SummonEffect.from_json(json)
            case "null": return NullEffect()
            case "noeffect": return NullEffect()
            case None: return NullEffect()
            case _: return warn(f"Tried to parse an effect with type {type}. Returning NullEffect instead.") and NullEffect()


class NullEffect(AbstractEffect):
    "Does literally nothing except consumming way to much RAM thanks to this beautiful innovation that OOP is."

    def __init__(self): return

    def execute(self, **kwargs) -> bool:
        return False

    def from_json():
        return NullEffect()

    def __str__(self) -> str:
        return "nothing"


@dataclass
class EffectUnion(AbstractEffect):
    # use two field rather than a list so that length is now at interpretation time (would be useful if Python was LLVM-compiled)
    effect1: AbstractEffect
    # I might change that later though, but for now use `Union(Union(effect1, effect2), effect3)` or similar for more than 2 effects.`
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
            if card.state != self.new_state:
                has_worked = True
            card.state = self.new_state
        return has_worked

    def from_json(json: dict):
        effect = ChangeState(State.from_str(json["new_state"]))
        if "for" in json:
            return EffectUnion(effect, DelayEffect(ChangeState(State.default), json["for"], {}))
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
        kwargs["damage_mode"] = self.damage_mode
        for card in AbstractEffect.targeted_objects(**kwargs):
            # nobody answered so I'll consider it a feature.
            kwargs["survey"].damage += card.damage(
                self.amount.eval(**kwargs), **kwargs)
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
        "Pseudo copy of self: evaluated fields with `kwargs` before copying."
        return DOTEffect(RawNumeric(self.damage.eval(**kwargs)), RawNumeric(self.turn.eval(**kwargs)))

    def from_json(json: dict):
        return DOTEffect(int(json["damage"]), json["time"])

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


@dataclass
class LoopEffect(AbstractEffect):
    "Apply the effect at the end of each turn while the one applying it is not defeated, unless `self.infinite` is set to `True`, then the effect is applied at the end of every turn."
    effect: AbstractEffect
    infinite: bool
    kwargs: dict

    def with_kwargs(self, kwargs: dict):
        return LoopEffect(self.effect, self.infinite, kwargs)

    def from_json(json: dict):
        return LoopEffect(AbstractEffect.from_json(json["effect"]), getordef(json, "infinite", False), {})

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


@dataclass
class DelayEffect(AbstractEffect):
    effect: AbstractEffect
    time: int  # doesn't support Numeric as it would be kinda useless.
    kwargs: dict

    def with_kwargs(self, kwargs: dict):
        return DelayEffect(self.effect, self.time, kwargs)

    def from_json(json: dict):
        return DelayEffect(AbstractEffect.from_json(json["effect"]), json["delay"], {})

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
        amount = amount.eval(**kwargs)  # eval once for every target.
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
        Δmax_energy = max.max_energy.eval(**kwargs)
        kwargs["player"].max_energy += Δmax_energy
        Δenergy_per_turn = max.energy_per_turn.eval(**kwargs)
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
    summon: any  # summon is creature card, I cannot annotate because Python. Why on earth do you have to annote type with a function though? Who had this terrible idea?

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
        return True

    def from_json(json: dict):
        return SummonEffect(getordef(json, "count", 1), CreatureCard.from_json(json["creature"], 1j))

    def __str__(self):
        return f"summoning of a {self.summon.name}"


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
            target.owner.active[j] = None
            # I could have just done kwargs["player"] but it seems safer this way.
            target.owner = kwargs["user"].owner
            kwargs["user"].owner.active[valids.pop()] = target
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
        match self.n:
            case 1: verbal = " once"
            case 2: verbal = " twice"
            case 3: verbal = " thrice"
            case n: verbal = f" {n} times"
        return str(self.effect) + verbal


class PassiveTrigger(IntEnum):
    endofturn = 0  # main_target => self
    whenplaced = 1  # main_target => self
    whendefeated = 2  # main_target => attacker (must improve code first)
    whenattack = 3  # same kwargs as attack
    # main_target => atatcker / only work when defeated by attack (feature not bug)
    whenattacked = 4
    # Must improve code before implementing those:
    whendiscarded = 5  # main_target => allied_commander
    whendrawn = 6  # main_target => allied_commander

    def from_str(name: str):
        match cleanstr(name):
            case "endofturn": return PassiveTrigger.endofturn
            case "whenplaced": return PassiveTrigger.whenplaced
            case "whendefeated": return PassiveTrigger.whendefeated
            case "whenattack": return PassiveTrigger.whenattack
            case "whenattacking": return PassiveTrigger.whenattack

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
        return Passive(getordef(json, "name", ""), PassiveTrigger.from_str(json["trigger"]), AbstractEffect.from_json(getordef(json, "effect", {"type": "null"})))

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
        return Attack(
            getordef(json, "name", ""),
            int(json["power"]),  # no float in power
            TargetMode.from_str(json["target_mode"]),
            int(json["cost"]),
            AbstractEffect.from_json(getordef(json, "effect", "null")),
            (*getordef(json, "tags", ()),)
        )

    def __str__(self) -> str:
        "Return a verbal representation of self."
        s = f"{self.name} (cost:{str(self.cost)}) targets {self.target_mode.to_str()} "
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

    # Method is inherited to every subclass. Will be needed as otherwise every card with the same id have shared HP.
    def copy(self):
        "Self explanatory."
        # a bit spaghetti coded but I can't really do better because Python. TODO: copy recursively to avoid sharing completely
        return type(self)(**vars(self))

    # in case we can't know if the card is a Creature or not, it avoids a crash.
    def iscommander(self) -> bool: return False


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
            [Attack("Default Attack", ifelse(getordef(json, "commander", False), 65, 3 + json["cost"]*7), TargetMode.target, ifelse(
                getordef(json, "commander", False), 1, 0), NullEffect()), *(Attack.from_json(attack) for attack in getordef(json, "attacks", []))],
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
        pretty = f"{self.name} (id:{self.id}): {self.element.to_str()}\nMax HP: {self.max_hp}\nCost: {self.cost}\nAttacks: ["
        for attack in self.attacks:
            pretty += "\n " + str(attack)
        pretty += "\n]\nPassives: ["
        for passive in self.passives:
            pretty += "\n " + str(passive)
        return pretty + "\n]"

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
    pass  # necessary cause Python


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
    attacked: bool = False
    state: State = State.default

    def __init__(self, card: CreatureCard, owner: Player, board: Board):
        self.card = card
        self.hp = card.max_hp
        self.element = card.element
        self.owner = owner
        self.board = board
        self.effects = []
        self.attacked = False
        self.state = State.default

    def can_attack(self):
        if self.state in [State.blocked, State.invisible]:
            return False
        if self.card.iscommander() and np.any([card is not None for card in self.owner.active]):
            return False
        if self.board is None or self.owner != self.board.active_player:
            return False
        return not self.attacked

    def attack(self, attack: Attack, target, **kwargs) -> EffectSurvey:
        "Make `self` use `attack` on `other`, applying all of its effects, and return a EffectSurvey object (containing total damage and healing done)."
        getorset(kwargs, "survey", EffectSurvey())
        if self.board.active_player != self.owner:
            kwargs["survey"].return_code = ReturnCode.wrong_turn
            return kwargs["survey"]  # doesn't act if it can't
        if (not self.can_attack()) or target.state in [State.invisible, State.damageless]:
            kwargs["survey"].return_code = ReturnCode.cant
            return kwargs["survey"]
        if self.owner.energy < attack.cost:
            kwargs["survey"].return_code = ReturnCode.no_energy
            return kwargs["survey"]
        getorset(kwargs, "player", self.owner)
        getorset(kwargs, "board", self.board)
        getorset(kwargs, "main_target", target)
        getorset(kwargs, "target_mode", attack.target_mode)
        getorset(kwargs, "damage_mode", DamageMode.direct)
        getorset(kwargs, "user", self)
        if len(AbstractEffect.targeted_objects(**kwargs)) == 0:
            kwargs["survey"].return_code = ReturnCode.no_target
            return kwargs["survey"]
        for card in AbstractEffect.targeted_objects(**kwargs):
            kwargs["survey"].damage += card.damage(attack.power, **kwargs)
        if not attack.effect.execute(**kwargs) and (kwargs["survey"].damage == 0) and (kwargs["survey"].heal == 0):
            kwargs["survey"].return_code = ReturnCode.failed
            if cleanstr(attack.name) != "splishsplosh":
                return kwargs["survey"]
        for passive in self.card.passives:
            if passive.trigger != PassiveTrigger.whenattack:
                continue
            passive.execute(**kwargs)
        self.owner.energy -= attack.cost
        for card in self.board.unactive_player.boarddiscard() + self.board.active_player.boarddiscard():
            # must be improved to apply passive of card defeated by passives or other sources
            card.defeatedby(self)
        self.attacked = True
        if DEV() and not self.owner.isai():
            self.board.devprint()
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

    def damage(self, amount, **kwargs) -> int:
        "Does damage to self, modified by any modifiers. `kwargs` must contain damage_mode & user"
        mode = getordef(kwargs, "damage_mode", DamageMode.direct)
        if mode == DamageMode.indirect:
            return self.indirectdamage(amount)
        attacker = kwargs["user"]
        amount *= ifelse(mode.can_strong()
                         and attacker.element.effectiveness(self.element), 12, 10)
        amount //= ifelse(mode.can_weak()
                          and self.element.resist(attacker.element), 12, 10)
        if self.card.iscommander() and mode.can_weak():
            amount = amount * (100 - 8 * len(self.owner.get_actives())) // 100
        return self.indirectdamage(amount)

    def indirectdamage(self, amount: int) -> int:
        "Reduce HP by amount but never goes into negative, then return damage dealt."
        if self.state == State.damageless:
            return 0
        if DEV() and type(amount) != int:
            warn(f"Card with name \"{self.card.name}\" took non integer damages; converting value to int. /!\\ PLEASE FIX: automatic type conversion is disabled when out of DEV mode /!\\")
            amount = int(amount)
        if amount > self.hp:
            amount = self.hp
            self.hp = 0
            return amount
        self.hp -= amount
        return amount

    def heal(self, amount: int) -> int:
        "Heal `self` from `amount` damage while never overhealing past max HP and return amount healed."
        if DEV() and type(amount) != int:
            warn(f"Card with name \"{self.name}\" healed from non integer damages; converting value to int. /!\\ PLEASE FIX: automatic type conversion is disabled when out of DEV mode /!\\")
            amount = int(amount)
        amount = min(self.card.max_hp - self.hp, amount)
        self.hp += amount
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
            self.heal(ifelse(self.card.iscommander(), 30, 10))
        self.attacked = False


@dataclass
class SpellCard(AbstractCard):
    on_use: Attack

    def from_json(json: dict, id: int):
        return SpellCard(json["name"], id, Element.from_str(json["element"]), Attack.from_json(json["on_use"]))

    def use(self, target: ActiveCard, board: Board):
        sim = ActiveCard(
            CreatureCard(name=self.name, id=self.id, element=self.element, max_hp=0, attacks=[
                         self.on_use], passives=[], cost=0, tags=("spell")),
            board.active_player,
            board
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


@dataclass  # for display
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

    def __init__(self, name: str, commander: CommanderCard, deck: list[AbstractCard] = []):
        if len(deck) != Constants.default_deck_size:
            warn("Tried to initialize a Player with an invalid deck; deck validity should be checked before initialization; deck remplaced by a default one.")
            deck = Player.get_deck()
        self.name = name
        self.commander = ActiveCard(commander, self, None)
        # avoid sharing, notably if deck is left to default in DEV() mode, as Python is a terrible language
        self.deck = deck.copy()
        rng.shuffle(self.deck)
        self.discard = []  # is not shared
        self.hand = []
        # self.draw()
        self.energy = Constants.default_energy_per_turn
        self.max_energy = Constants.default_max_energy
        self.energy_per_turn = Constants.default_energy_per_turn
        self.active = []

    def get_commander(*_) -> CommanderCard:
        # yes, it's ugly, it's Python
        return getCOMMANDERS()[rng.choice([*getCOMMANDERS()])]

    def get_deck(*_) -> list[AbstractCard]:
        return [*rng.choice(getCARDS(), Constants.default_deck_size)]

    def get_actives(self) -> list[ActiveCard]:
        return [card for card in self.active if card is not None]

    def isai(self) -> bool: return False

    def card_id(name: str) -> int:
        for card in getCARDS():
            if cleanstr(card.name) == cleanstr(name):
                return card.id
        # I'm way to lazy to check whether the returned value is valid, so I just return a valid value in case the card doesn't exist.
        return np.sum([ord(c) for c in cleanstr(name)]) % len(getCARDS())

    def from_save(name: str):
        fname = cleanstr(name)
        io = open("data/players.json")
        players: dict = loads(io.read())
        if fname not in players:
            return None
        player = players[fname]
        io.close()
        return Player(name, getCOMMANDERS()[player["commander"]], [getCARDS()[Player.card_id(i)] for i in player["deck"]])

    def from_saves(name: str, saves: dict):
        return Player(name, getCOMMANDERS()[saves[name]["commander"]], [getCARDS()[Player.card_id(i)] for i in saves[name]["deck"]])

    def save(self):
        self.reset()
        io = open("data/players.json", "r+")
        players: dict = loads(io.read())
        userdata: dict = {cleanstr(self.name): {"commander": cleanstr(
            self.commander.card.name), "deck": [cleanstr(card.name) for card in self.deck]}}
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
            self.discard.clear()
        return self.deck.pop()

    def draw(self) -> list:
        # Please note that the top of the deck is the end of the self.deck list.
        new = [self.singledraw() for _ in range(Constants.default_hand_size + ifelse(
            self.commander.board.arena.has_effect(Arena.watorvarg), 1, 0) - len(self.hand))]
        self.hand.extend(new)
        return new  # to display drawing(s) on the GUI?

    def add_energy(self, amount: int) -> int:
        amount = min(amount, self.max_energy - self.energy)
        self.energy += amount
        return amount  # for displaying

    def haslost(self) -> bool:
        "Return True is this Player's CommanderCard is defeated, False otherwise."
        if self.commander.hp <= 0:
            return True
        return False

    def handdiscard(self, i: int):
        "Discard the `i`th card in `self`'s `hand`, returning it."
        card = self.hand.pop(i)
        self.discard.append(card)
        return card

    def iddiscard(self, id: int):
        "Discard the first card in `self`'s `hand` with `id`, returning it."
        for i in range(len(self.hand)):
            if self.hand[i].id == id:
                return self.handdiscard(i)

    def boarddiscard(self):
        "Discard every defeated cards, returning them."
        discards: list[ActiveCard] = []
        cards = self.active
        for i in range(len(cards)):
            if cards[i] is None:
                continue
            if cards[i].hp <= 0:
                cards[i].state = State.discarded
                discards.append(cards[i])
                self.discard.append(cards[i].card)
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
        self.energy -= self.hand[i].cost
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

    def rps_win(player1: str, player2: str):  # no idea why this is a method
        "Return `0` if player1 win Rock Paper Scissor against player2, `1` if player2 wins and `-1` if it's a draw."
        player1, player2 = rps2int(player1), rps2int(player2)
        if player1 == (player2 + 1) % 3:
            return 0
        if (player1 - 1) % 3 == player2:
            return 1
        return -1

    def __init__(self, player1: Player, player2: Player, autoplay: bool = True):
        if DEV() and rng.random() < 0.5:  # Coinflip in DEV()-mode, must implement RPS in GUI- (and Omy-) mode
            player1, player2 = player2, player1
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
        self.active_player = player1  # player1 start
        self.unactive_player = player2
        self.unactive_player.energy += 1  # To compensate disadvantage
        self.turn = 0
        player1.draw()
        player2.draw()
        self.autoplay = autoplay
        DEV() and not self.active_player.isai() and self.devprint()
        if autoplay and self.active_player.isai():
            self.active_player.auto_play(self)

    def getwinner(self) -> Player | None:
        if self.unactive_player.haslost():
            return self.active_player
        if self.active_player.haslost():
            return self.unactive_player
        return None

    def endturn(self) -> tuple:
        "End the turn returning (player_who_ends_turn: Player, energy_gained: int, card_drawn: list, current_turn: int, winner: None | Player)"
        for card in self.active_player.active:
            if card is None:
                continue
            card.endturn()
        self.active_player.commander.endturn()
        self.active_player, self.unactive_player = self.unactive_player, self.active_player
        self.turn += 1
        ret = (self.unactive_player, self.unactive_player.add_energy(
            self.unactive_player.energy_per_turn), self.unactive_player.draw(), self.turn, self.getwinner())
        if DEV():
            if ret[4] is not None:
                print(f"The winner is {ret[4].name}")
                return ret
            # print(ret)
            not self.active_player.isai() and self.devprint()
        if self.autoplay and self.active_player.isai() and ret[4] is None:
            return self.active_player.auto_play(self)
        return ret

    def devprint(self):
        you = self.active_player
        them = self.unactive_player
        print(self.turn)
        print(f"Them: {them.energy}/{them.max_energy} energies.")
        print(them.commander.card.name,
              f"({them.commander.hp}/{them.commander.card.max_hp})")
        for card in them.active:
            if card is None:
                print("none ", end="")
                continue
            print(cleanstr(card.card.name),
                  f"({card.hp}/{card.card.max_hp}) ", end="")
        print(f"\n\nYou : {you.energy}/{you.max_energy} energies")
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


class AIPlayer(Player):  # I hate OOP
    def __init__(self):
        Player.__init__(self, self.get_name(),
                        self.get_commander(), self.get_deck())

    def get_name(*_) -> str:  # allow self in argument
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
            return self.hand[i].use(self.naive_target(board, self.hand[i].on_use.tags), board)
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


#a mettre dans une classe?, je sais pas faire
# a changer pour envoyer de linformation au lieu de "1"
    
def main(client_socket: socket.socket):
    """
    main represents the thread on which the game is running.
    """
    try:
        while True:
            x = str(input("Enter 1 to send smth: \n"))
            if x == "1":
                send(client_socket, "append", "Player0/deck/1", "1010101010") ## example 1 of append
                send(client_socket, "append", "Player0/deck", json.dumps({"2": "202020202"})) ## example 2 of append
                # tested 'replace' method, 100% functionality
                # tested 'append' method, 100% functionality
                # tested 'remove' method, 100% functionality
            try:
                # check if socket is closed
                # this method will not work with the POC input(), but will work in the game
                client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            except:
                break
    except Exception as e:
        print(e)
        print("main thread error/closing")
    finally:
        client_socket.close()


if __name__ == "__main__":
    """
    The idea is we set up the listening function on thread 1, 

    then return the socket on thread 0 (this is thread 0),

    then start the game loop using the socket,
    """
    action = "join"
    target_ip = ""
    if input("Start party or join a party? ").lower() == "start":
        action = "start"
    else:
        target_ip = input("Enter the target peer's IP address (or 'exit' to quit): ")
    
    client_socket = net.start_peer_to_peer(action, target_ip)

    if client_socket:
        main(client_socket)
#        mainThread = threading.Thread(target=main, args=(client_socket,))
#        mainThread.start()
    else:
        print("Error with connection (Most likely timed out)")
