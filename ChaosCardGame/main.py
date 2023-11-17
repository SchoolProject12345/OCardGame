# The Card Game

from dataclasses import dataclass # easier class declaration
from enum import IntEnum # for clear, lightweight (int) elements/state.
from numpy import random as rng # for shuffle function/rng effects
import numpy as np # for gcd for Kratos card
from json import loads
import os
os.chdir("ENTER DIR HERE")
from convenience import * # make code cleaner

def getCARDS(CARDS = []) -> list:
    "Return the list of every card defined in `./data/cards.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(CARDS) != 0:
        return CARDS
    io = open("data/cards.json");
    json = loads(io.read()); # assuming people aren't stupid enough to write invalid JSON in cards.json. Don't forgot commas. And don't add to much.
    io.close();
    id = -1; # starts at -1 + 1 = 0
    CARDS += [AbstractCard.from_json(card, (id := id + 1)) for card in json]
    return CARDS
def getCOMMANDERS(COMMANDERS = {}) -> dict:
    "Return a dict of every card defined `./data/commanders.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(COMMANDERS) != 0:
        return COMMANDERS
    io = open("data/commanders.json");
    json = loads(io.read());
    io.close();
    id = -1;
    COMMANDERS.update({cleanstr(card["name"]):CreatureCard.from_json(card, (id := id + 1)) for card in json});
    return COMMANDERS
def DEV() -> bool: return True; # enable debugging; function to avoid taking from global scope

class Element(IntEnum):
    elementless = 0 # used instead of None as a placeholder (for type-safeness) or for elementless card types for flexibility when using Element.effective
    water = 1
    fire = 2
    air = 3
    earth = 4
    chaos = 5 # Weak defense against all but chaos (x1,2 damage taken) but powerful attack against all but chaos (x1.2 damage output)
    def from_str(name: str):
        "Return an Element value from name string."
        match cleanstr(name):
            case "water": return Element.water
            case "fire": return Element.fire
            case "air": return Element.air
            case "earth": return Element.earth
            case "chaos": return Element.chaos # keeping chaos as it is a more interesting alternative than elementless for cards with no obvious element
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
            return False # changed chaos to resist chaos to avoid chaos being just a x1.2 in power and /1.2 in HP
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
    default = 0 # placeholder
    blocked = 1 # can't attack
    invisble = 2 # can't attack; can't be targeted
    discarded = 3 # for GUI
    def from_str(name: str):
        match cleanstr(name):
            case "default": return State.default
            case "blocked": return State.blocked
            case "block": return State.block
            case "invisible": return State.invisible
            case _: return warn("Tried to form State from an non-recognized string; returing State.default instead.") and State.default

class TargetMode(IntEnum):
    foes = 0
    target = 1
    allies = 2
    self = 3 # it can't possibly cause a bug, right? ( ͡° ͜ʖ ͡°)
    commander = 4
    allied_commander = 5
    all_commanders = 6
    massivedestruction = 7
    all = 8
    def from_str(name: str):
        match cleanstr(name):
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
            case "all": return TargetMode.all
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
class DamageMode(IntEnum):
    direct = 0
    indirect = 1
    ignore_resist = 2
    def from_str(name: str):
        match cleanstr(name):
            case "direct": return DamageMode.direct
            case "indirect": return DamageMode.indirect
            case "ignoreresist": return DamageMode.ignore_resist
            case _: return warn(f"Tried to form DamageMode from {name}, returning DamageMode.direct instead.") and DamageMode.direct
class ReturnCode(IntEnum):
    ok = 200
    wrong_turn = 400
    no_energy = 401
    cant = 402
@dataclass
class EffectSurvey:
    "Contain all values returned by an attack"
    damage: int = 0
    heal: int = 0
    return_code: ReturnCode = ReturnCode.ok
    def __add__(self, other):
        return EffectSurvey(self.damage + other.damage, self.heal + other.heal, self.return_code)
    def __iadd__(self, other):
        return self + other # please save me from this language; the more I discover the more I ask myself why python is used.
class AbstractEffect:
    def __init__(self):
        warn("AbstractEffect class serves only as a superclass; initialize object of more specific classes instead.")
    def execute(self, **kwargs):
        "`kwargs` needed for execution: player, board, main_target, target_mode, user, survey"
        warn(f"AbstractEffect of type {type(self)} has no execute method defined.")
    def endturn(self, target: ActiveCard):
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
                    *filter((lambda x: x != None), kwargs["board"].unactive_player.active),
                    *filter((lambda x: x != None and x != kwargs["user"]), kwargs["board"].active_player.active),
                ]
            case TargetMode.massivedestruction:
                return [
                    *filter((lambda x: x != None), kwargs["board"].unactive_player.active),
                    *filter((lambda x: x != None), kwargs["board"].active_player.active),
                    kwargs["board"].unactive_player.commander,
                    kwargs["board"].active_player.commander
                ]
            case _: []
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
            case "heal":  return HealEffect.from_json(json)
            case "drain": return DamageDrain.from_json(json)
            case "withprobability": return WithProbability.from_json(json)
            case "gainenergy": return EnergyEffect.from_json(json)
            case "addenergy": return EnergyEffect.from_json(json)
            case "energygain": return EnergyEffect.from_json(json)
            case "dot": return DOTEffect.from_json(json)
            case "damageovertime": return DOTEffect.from_json(json)
            case "delay": return DelayEffect.from_json(json)
            case "null": return NullEffect()
            case "noeffect":  return NullEffect()
            case None: return NullEffect()
            case _: return warn(f"Tried to parse an effect with type {type}. Returning NullEffect instead.") and NullEffect()
class NullEffect(AbstractEffect):
    "Does literally nothing except consumming way to much RAM thanks to this beautiful innovation that OOP is."
    def __init__(self): return
    def execute(self, **kwargs):
        return
    def from_json():
        return NullEffect()
    def __str__(self) -> str:
        return "nothing"
@dataclass
class EffectUnion(AbstractEffect):
    effect1: AbstractEffect # use two field rather than a list so that length is now at interpretation time (would be useful if Python was LLVM-compiled)
    effect2: AbstractEffect # I might change that later though, but for now use `Union(Union(effect1, effect2), effect3)` or similar for more than 2 effects.`
    def execute(self, **kwargs):
        self.effect1.execute(**kwargs)
        self.effect2.execute(**kwargs)
    def from_json(json: dict):
        return EffectUnion(AbstractEffect.from_json(json["effect1"]), AbstractEffect.from_json(json["effect2"]))
    def __str__(self) -> str:
        return f"{str(self.effect1)} and {str(self.effect2)}"
@dataclass
class ChangeTarget(AbstractEffect):
    "Change targetting mode of sub-effects."
    effect: AbstractEffect
    new_target: TargetMode
    def execute(self, **kwargs):
        kwargs = kwargs.copy()
        kwargs["target_mode"] = self.new_target
        self.effect.execute(**kwargs)
    def from_json(json: dict):
        return ChangeTarget(AbstractEffect.from_json(json["effect"]), TargetMode.from_str(json["new_target"]))
    def __str__(self) -> str:
        return f"{str(self.effect)} on {self.target.to_str()}"
@dataclass
class ChangeState(AbstractEffect):
    "Change the target(s) state to `new_state`."
    new_state: State
    def execute(self, **kwargs):
        for card in AbstractEffect.targeted_objects(**kwargs):
            card.state = self.new_state
    def from_json(json: dict):
        return ChangeState(TargetMode.from_str(json["new_state"]))
    def __str__(self) -> str:
        match self.new_state:
            case State.blocked: return "block them"
            case State.invisible: return "make them invisible
            case State.default: return "reset their state"
            case _: return "???"
@dataclass
class DamageEffect(AbstractEffect):
    "Does indirect damage to the target(s). Indirect damage are not affected by modifier on the user.\nChange the Attack power | target in order to change direct damages."
    amount: int
    damage_mode: DamageMode = DamageMode.direct
    def execute(self, **kwargs):
        kwargs = kwargs.copy()
        kwargs["damage_mode"] = self.damage_mode
        for card in AbstractEffect.targeted_objects(**kwargs):
            kwargs["survey"].damage += card.damage(self.amount, **kwargs)
    def from_json(json: dict):
        return DamageEffect(json["amount"], DamageMode.from_str(json["damage_mode"]))
    def __str__(self) -> str:
        return f"{self.amount} {self.damage_mode.to_str()} damage"
@dataclass
class DOTEffect(AbstractEffect):
    damage: int
    turn: int
    def copy(self):
        return DOTEffect(self.damage, self.turn)
    def from_json(json: dict):
        return DOTEffect(json["damage"],json["time"])
    def execute(self, **kwargs):
        for target in AbstractEffect.targeted_objects(**kwargs):
            target.effects.append(self.copy())
    def endturn(self, target: ActiveCard):
        amount = self.damage // self.turn
        self.damage -= amount
        self.turn -= 1
        target.indirectdamage(damage)
        return self.turn > 0
    def __str__(self) -> str:
        return f"{self.damage} damage over {self.time} turns"
@dataclass
class DelayEffect(AbstractEffect):
    effect: AbstractEffect
    time: int
    kwargs: dict = {}
    def with_kwargs(self, kwargs):
        return DelayEffect(self.effect, self.time)
    def from_json(json: dict):
        return DelayEffect(AbstractEffect.from_json(json["effect"]), json["delay"])
    def execute(self, **kwargs):
        for target in AbstractEffect.targeted_objects(**kwargs):
            target.effects.append(self.with_kwargs(kwargs))
    def endturn(self, target: ActiveCard):
        if self.time > 0:
            self.ime -= 1
            return True
        kwargs = kwargs.copy()
        self.kwargs["main_target"] = target
        self.kwargs["target_mode"] = TargetMode.target
        self.effect.execute(**self.kwargs)
    def __str__(self):
        return f"{str(self.effect)} after {self.time} turns"
@dataclass
class DamageDrain(AbstractEffect): # I don't know if this'll ever get a use.
    "Heal for a ratio (rational) of total damage (indirect/direct) "
    numerator: int
    denominator: int
    effect: AbstractEffect
    def execute(self, **kwargs):
        main_survey = kwargs["survey"]
        kwargs = kwargs.copy()
        kwargs["survey"] = EffectSurvey()
        self.effect.execute(**kwargs)
        kwargs["user"].heal(self.numerator * kwargs["survey"] // self.denominator)
        main_survey += kwargs["survey"]
    def from_json(json: dict):
        return DamageDrain(json["num"], json["den"], AbstractEffect.from_json(json["effect"]))
    def __str__(self):
        return f"heal {self.numerator}/{self.denominator} of damage dealt from {str(self.effect)}"
@dataclass
class HealEffect(AbstractEffect):
    "Heal target(s) by amount."
    amount: int
    def execute(self, **kwargs):
        for card in AbstractEffect.targeted_objects(**kwargs):
            kwargs["survey"].heal += card.heal(self.amount)
    def from_json(json: dict):
        return HealEffect(json["amount"])
    def __str__(self):
        return f"heal from {self.amount} damage"
@dataclass
class WithProbability(AbstractEffect):
    "Apply either `self.effect1` or `self.effect2` such that `self.effect1` has `self.probability` to happen."
    probability: float
    effect1: AbstractEffect
    effect2: AbstractEffect = NullEffect()
    def execute(self, **kwargs):
        if rng.rand() < self.probability:
            return self.effect1.execute(**kwargs)
        self.effect2.execute(**kwargs)
    def from_json(json: dict):
        return WithProbability(getordef(json, "probability", 0.5), AbstractEffect.from_json(json["effect1"]), AbstractEffect.from_json(getordef(json, "effect2", "null")))
    def __str__(self):
        return f"{str(self.effect1)} {int(100.0*self.probability)}% of the time, {self.effects2} otherwise"
@dataclass
class EnergyEffect(AbstractEffect):
    "Adds (or remove) to the user's Player, energy, max_energy and energy_per_turn."
    energy: int
    max_energy: int
    energy_per_turn: int
    def execute(self, **kwargs):
        kwargs["player"].max_energy += self.max_energy
        kwargs["player"].energy_per_turn += self.energy_per_turn
        kwargs["player"].add_energy(self.energy)
    def from_json(json: dict):
        return EnergyEffect(getordef(json, "gain", 0), getordef(json, "max", 0), getordef(json, "per_turn", 0))
    def __str__(self):
        f"an increase of {self.energy} energy, {self.max_energy} maximum energy & {self.energy_per_turn} per turn" # TODO: find prettier way to write this.

@dataclass
class Attack:
    name: str
    power: int
    target_mode: TargetMode
    cost: int
    effect: AbstractEffect # use EffectUnion for multiple Effects
    tags: tuple = ()
    def from_json(json: dict):
        return Attack(
            getordef(json, "name", ""),
            int(json["power"]), # no float in power
            TargetMode.from_str(json["target_mode"]),
            int(json["cost"]),
            AbstractEffect.from_json(getordef(json, "effect", "null")),
            (*getordef(json, "tags", ()),)
        )
    def __str__(self) -> str:
        "Return a verbal representation of self."
        s = f"{self.name} (cost:{str(self.cost)}) targets {self.target_mode.to_str()} "
        if self.power != 0:
            s += "dealing {self.power} damages and "
        s += f"doing {str(self.effect)}"
        f"does {self.power} damages on {self.target_mode.to_str()} and does {self.effect}."
        

@dataclass
class AbstractCard:
    name: str
    id: int
    element: Element # all card types until now have an element; if a new card type doesn't require an element, we'll force the element field to Element.elementless in the from_json constructor (which allows flexibility with Element.efective).
    def __init__(self, *args):
        warn("AbstractCard class serves only as a superclass; initialize object of more specific classes instead.")
    def from_json(json: dict, id: int): # id from index in list
        "Dispatch the from_json method according to \"type\" field. The method hence doesn't return an AbstractCard object."
        type = json["type"]
        if type == "creature":
            return CreatureCard.from_json(json, id)
        if type == "spell":
            return SpellCard.from_json(json, id)
        warn(f"Card with name {json['name']} has type {type} which isn't handled.")
    def copy(self): # Method is inherited to every subclass. Will be needed as otherwise every card with the same id have shared HP.
        "Self explanatory."
        return type(self)(**vars(self)) # a bit spaghetti coded but I can't really do better because Python. TODO: copy recursively to avoid sharing completely
    def iscommander(self) -> bool: return False # in case we can't know if the card is a Creature or not, it avoids a crash.

@dataclass
class CreatureCard(AbstractCard):
    max_hp: int
    attacks: list # list of Attack objects
    passives: list
    cost: int
    def from_json(json: dict, id: int):
        "Initialize either a CreatureCard object or a CommanderCard object depending on \"commander\" field with every field filled from the JSON (Python) dict passed in argument."
        args = (
            json["name"],
            id,
            Element.from_json(json),
            json["hp"],
            [Attack("Default Attack", 10, TargetMode.target, 0, NullEffect()), *(Attack.from_json(attack) for attack in getordef(json, "attacks", []))],
            [],
            json["cost"]
        )
        if getordef(json, "commander", False): # so we don't need to define "commander":false for every card (might be changed later to "type":"commander" though).
            return CommanderCard(*args)
        return CreatureCard(*args)
    def __str__(self) -> str:
        "Return beautiful string reprensenting self instead of ugly mess defaulting from dataclasses."
        pretty = f"{self.name} (id:{self.id}): {self.element.to_str}\nMax HP : {self.max_hp}\nCost   : {self.cost}\nAttacks: [\n"
        for attack in self.attacks:
            pretty += f" \n" + str(attack)
        pretty += "]\nPassives: [\n (unimplemented yet)\n]"
        return pretty
        
@dataclass
class CommanderCard(CreatureCard):
    # Note: all field of CommanderCard must have a default value as CreatureCard ends with one. (inheritance)
    def iscommander(self) -> bool: return True
class Player: pass # necessary cause Python
class Board: pass
@dataclass
class ActiveCard:
    card: CreatureCard
    hp: int
    element: Element # to change active type after a specific effect
    owner: Player
    board: Board
    attacked: bool = False
    state: State = State.default
    effects: list = []
    def __init__(self, card: CreatureCard, owner: Player, board: Board):
        self.card = card
        self.hp = card.max_hp
        self.element = card.element
        self.owner = owner
        self.board = board
        self.effects = []
    def attack(self, attack: Attack, target, **kwargs) -> EffectSurvey:
        "Make `self` use `attack` on `other`, applying all of its effects, and return a EffectSurvey object (containing total damage and healing done)."
        getorset(kwargs, "survey", EffectSurvey())
        if self.board.active_player != self.owner:
            kwargs["survey"].return_code = ReturnCode.wrong_turn
            return kwargs["survey"] # doesn't act if it can't
        if self.state == State.blocked or target.state == State.invisble or self.attacked:
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
        for card in AbstractEffect.targeted_objects(**kwargs):
            kwargs["survey"].damage += card.damage(attack.power, **kwargs)
        attack.effect.execute(**kwargs)
        self.owner.energy -= attack.cost
        self.board.unactive_player.boarddiscard()
        self.board.active_player.boarddiscard()
        self.attacked = True
        if DEV():
            self.board.devprint()
        return kwargs["survey"]
    def damage(self, amount, **kwargs) -> int:
        "Does direct damage to self, modified by any modifiers."
        mode = getordef(kwargs, "damage_mode", DamageMode.direct)
        if mode == DamageMode.indirect:
            return self.indirectdamage(amount)
        attacker = kwargs["user"]
        return self.indirectdamage(amount * ifelse(attacker.element.effectiveness(self.element) and mode != DamageMode.indirect, 12, 10) // ifelse(self.element.resist(attacker.element) and mode == DamageMode.direct, 12, 10))
    def indirectdamage(self, amount: int) -> int:
        "Reduce HP by amount but never goes into negative, then return damage dealt."
        if DEV() and type(amount) != int:
            warn(f"Card with name \"{self.name}\" took non integer damages; converting value to int. /!\\ PLEASE FIX: automatic type conversion is disabled when out of DEV mode /!\\")
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
        self.effects = [effect for effect in self.effects if effect.endturn(self)]

@dataclass
class SpellCard(AbstractCard):
    on_use: Attack
    def from_json(json: dict, id: int):
        return SpellCard(json["name"], id, Element.from_str(json["element"]), Attack.from_json(json["on_use"]))
    def use(self, target: ActiveCard, board: Board):
        sim = ActiveCard(
            CreatureCard(self.name, self.id, self.element, 0, [self.on_use], []),
            board.active_player,
            board
        )
        survey = sim.attack(self.on_use, target)
        if survey.return_code == ReturnCode.ok:
            board.active_player.iddiscard(self.id)
        return survey

class Constants: # to change variables quickly. TODO: remove Python from this universe.
    default_max_energy = 4
    default_energy_per_turn = 3
    default_hand_size = 5
    default_deck_size = min(30, len(getCARDS()))
    board_size = rng.randint(1, 7)

@dataclass # for display
class Player:
    name: str
    commander: CommanderCard
    deck: list  # lists of `AbstractCard`s
    discard: list
    hand: list
    energy: int
    max_energy: int
    energy_per_turn: int
    active: list
    def __init__(self, name: str, commander: CommanderCard, deck: list = ifelse(DEV(), getCARDS(), [])):
        if len(deck) != Constants.default_deck_size:
            raise f"Player {name} tried to play with too few cards (error handling will be done later)."
        self.name = name
        self.commander = ActiveCard(commander, self, None)
        self.deck = deck.copy() # avoid sharing, notably if deck is left to default in DEV() mode, as Python is a terrible language
        rng.shuffle(self.deck)
        self.discard = [] # is not shared
        self.hand = []
        self.draw()
        self.energy = Constants.default_energy_per_turn
        self.max_energy = Constants.default_max_energy
        self.energy_per_turn = Constants.default_energy_per_turn
        active = []
    def from_save(name: str):
        fname = cleanstr(name);
        io = open("data/players.json");
        player = loads(io.read())[fname];
        io.close();
        return Player(name, getCOMMANDERS[player["commander"]], [getCARDS[i] for i in player["deck"]])
    def save(self):
        # prendre username et juste rentrer dans players.json ?
        # comment faire la syntaxe json la dedans ?
    def save(self, name: str):
        # TODO: la syntaxe json??
        io = open("data/players.json");
        userdata = {cleanstr(self.name):{"commander":cleanstr(self.commander.card.name),"deck":self.deck}} # must change a little
        io.dump(userdata)
        io.close()
    def draw(self) -> list:
        if len(self.hand) >= Constants.default_hand_size:
            pass # TODO: start a prompt to discard one card OR give an option to discard any amount of card during turn (which allow to draw a number of desired card at the end of the turn)
        new = [self.deck.pop() for _ in range(Constants.default_hand_size - len(self.hand))] # Please note that the top of the deck is the end of the self.deck list.
        self.hand.extend(new)
        return new # to display drawing(s) on the GUI?
    def add_energy(self, amount: int) -> int:
        amount = min(amount, self.max_energy - self.energy)
        self.energy += amount
        return amount # for displaying
    def haslost(self) -> bool :
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
        discards = []
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
    def place(self, i: int, j: int, board: Board):
        "Place the `i`th card of hand onto the `j`th tile of board, activing it. Return `True` if sucessful, `False` otherwise."
        if not 0 <= i < len(self.hand):
            return False
        if not 0 <= j < len(self.active):
            return False
        if self.active[j] is not None:
            return False
        if self.energy < self.hand[i].cost:
            return False
        self.energy -= self.hand[i].cost
        self.active[j] = ActiveCard(self.hand.pop(i), self, board)
        return True

def rps2int(rpc: str):
    match rpc:
        case "rock": return 0
        case "r": return 0
        case "paper": return 1
        case "p": return 1
        case "scissor": return 2
        case "s": return 2
        case _: return rng.randint(0,3)
@dataclass
class Board:
    player1: Player
    player2: Player
    board_size: int # between 1 and 6 max active cards, chosen at random at the begining of every game.
    active_player: Player
    unactive_player: Player
    turn: int
    def rps_win(player1: str, player2: str):
        "Return `0` if player1 win Rock Paper Scissor against player2, `1` if player2 wins and `-1` if it's a draw."
        player1, player2 = rps2int(player1), rps2int(player2)
        if player1 == (player2 + 1) % 3:
            return 0
        if (player1 - 1) % 3 == player2:
            return 1
        return -1
    def rpsbo5dev(): # no idea why this is a method
        "Return `True` if player1 reaches 3 Rock Paper Scissor wins before player2. Used for DEV() mode."
        DEV() or print("I think you forgot to update something in your code 'cause it's currently running rpsbo5dev while DEV() = False.")
        DEV() and return False
        wins = [0, 0]
        while max(*wins) != 3:
            win = Board.rps_win(input("<◁< Player1, choose your move (r/p/s) >>>: "), input("\x1b[1A\x1b[0J<<< Player2, choose your move (r/p/s) >▷>: "))
            if win < 0:
                print("It's a draw!")
                break
            wins[win] += 1
        return wins[0] == 3
    def __init__(self, player1: Player, player2: Player):
        if not (DEV() and Board.rpsbo5dev()): # if player1 lose rpsbo5: player2 start
            player1, player2 = player2, player1
        player1.commander.board = self
        player2.commander.board = self
        self.player1 = player1
        self.player2 = player2
        self.board_size = rng.randint(1, 7)
        player1.active = [None for _ in range(self.board_size)]
        player2.active = self.player1.active.copy()
        self.active_player = player1 # player1 start
        self.unactive_player = player2
        self.turn = 0
        self.devprint()
    def getwinner(self) -> Player | None:
        if self.unactive_player.haslost():
            return self.active_player
        if self.active_player.haslost():
            return self.unactive_player()
        return None
    def endturn(self) -> tuple:
        "End the turn returning (player_who_ends_turn: Player, energy_gained: int, card_drawn: list, current_turn: int, winner: None | Player)"
        for card in self.active_player.active:
            card.endturn()
        self.active_player.commander.endturn()
        self.active_player, self.unactive_player = self.unactive_player, self.active_player
        self.turn += 1
        ret = (self.unactive_player, self.unactive_player.add_energy(self.unactive_player.energy_per_turn), self.unactive_player.draw(), self.turn, self.getwinner())
        if DEV():
            if ret[4] is not None:
                print(f"The winner is {ret[4].name}")
                return ret
            print(ret)
            input("\033[H\033[2J")
            self.devprint()
        return ret
    def devprint(self):
        you = self.active_player
        them = self.unactive_player
        print(self.turn)
        print(f"Them: {them.energy}/{them.max_energy} energies.")
        print(them.commander.card.name, f"({them.commander.hp}/{them.commander.card.max_hp})")
        for card in them.active:
            if card is None:
                print("none ", end="")
                continue
            print(cleanstr(card.card.name), f"({card.hp}/{card.card.max_hp}) ", end="")
        print(f"\n\nYou : {you.energy}/{you.max_energy} energies")
        print(you.commander.card.name, f"({you.commander.hp}/{you.commander.card.max_hp})")
        for card in you.active:
            if card is None:
                print("none ", end="")
                continue
            print(cleanstr(card.card.name), f"({card.hp}/{card.card.max_hp}) ", end="")
        print()
        print([cleanstr(card.name) for card in you.hand])
