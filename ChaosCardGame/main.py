# The Card Game

from dataclasses import dataclass # easier class declaration
from enum import IntEnum # for clear, lightweight (int) elements/state.
from numpy import random as rng # for shuffle function/rng effects
import numpy as np # for gcd for Kratos card
from json import loads

def getCARDS(CARDS = []) -> list:
    "Return the list of every card defined in `./data/cards.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(CARDS) != 0:
        return CARDS
    io = open("data/cards.json");
    json = loads(io.read()); # assuming people aren't stupid enough to write invalid JSON in cards.json. Don't forgot commas.
    io.close();
    id = -1; # starts at -1 + 1 = 0
    CARDS += [AbstractCard.from_json(card, (id := id + 1)) for card in json if ((not "example" in card) or DEV()) and (not getordef(json, "commander", False))] # please note that whether example is put to true or false it is excluded from the list.
    return CARDS
def getCOMMANDERS(COMMANDERS = []) -> list:
    "Return the list of every card defined `./data/commanders.json`, initializing it if necessary. Must be called without argument, is the identidy function otherwise."
    if len(COMMANDERS) != 0:
        return COMMANDERS
    io = open("data/commanders.json");
    json = loads(io.read());
    io.close()
    id = -1;
    COMMANDERS += [CreatureCard.from_json(card, (id := id + 1)) for card in json if (not "example" in card) or DEV()]
    return COMMANDERS
def DEV() -> bool: return True; # enable debugging; function to avoid taking from global scope
class Constants: # to changing variables quickly, might be removed later.
    default_max_energy = 4
    default_energy_per_turn = 3
    default_hand_size = 5
    default_deck_size = min(30, len(getCARDS))

# convenience functions, might be moved to a separate file later.
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
    return dict.get(key)
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
    return dict.get(key)
def warn(*args, dev = DEV(), **kwargs) -> bool:
    """
    Print arguments in warning-style (if in DEV mode) and returns `True` to allow chaining.

    # Examples
    ```py
    >>> warn("foobarbaz") and print("do something here")
    ┌ Warning:
    └ foobarbaz
    do something here
    ```
    """
    if dev: # hard check to avoid mistakes
        print("\x1b[1;33m┌ Warning:\n└ ", *args, "\x1b[0m", **kwargs); # might not work in every terminal, but should in VS Code
    return True # this is definitevely not spaghetti code.
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
    return "".join(filter(str.isalnum, s)).lower()

class Element(IntEnum):
    elementless = 0 # used instead of None as a placeholder (for type-safeness) or for elementless card types for flexibility when using Element.effective
    water = 1
    fire = 2
    air = 3
    earth = 4
    chaos = 5 # Weak defense against all but chaos (x1,2 damage taken) but powerful attack against all but chaos (x1.2 damage output)
    def from_str(name: str):
        "Return an Element value from name string."
        match name.strip().lower():
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
    def effective(self, other) -> bool:
        """
            Element.effective(self, other: Element)
        
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
        Equivalent to `other.efectiveness(self)`.

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
        return other.effectiveness(self)
class State(IntEnum):
    default = 0 # placeholder

class AbstractEffect:
    def __init__(self):
        warn("AbstractEffect class serves only as a superclass; initialize object of more specific classes instead.")
    def execute(self, *args):
        warn(f"AbstractEffect of type {type(self)} has no execute method defined.")
@dataclass
class EffectUnion(AbstractEffect):
    effect1: AbstractEffect # use two field rather than a list so that length is now at interpretation time (would be useful if Python was LLVM-compiled)
    effect2: AbstractEffect # I might change that later though, but for now use `Union(Union(effect1, effect2), effect3)` or similar for more than 2 effects.`
    def execute(self, *args):
        self.effect1.execute(*args)
        self.effect2.execute(*args)

@dataclass
class Attack:
    power: int
    cost: int
    effects: AbstractEffect # use EffectUnion for multiple Effects
    def from_json(json: dict):
        pass # TODO: return an Attack object

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
    hp: int
    attacks: list # list of Attack objects
    passives: list
    state: State = State.default
    def from_json(json: dict, id: int):
        "Initialize either a CreatureCard object or a CommanderCard object depending on \"commander\" field with every field filled from the JSON (Python) dict passed in argument."
        args = (
            json["name"],
            id,
            Element.from_json(json),
            json["hp"],
            # use default argument for State
        )
        if getordef(json, "commander", False): # so we don't need to define "commander":false for every card (might be changed later to "type":"commander" though).
            return CommanderCard(*args)
        return CreatureCard(*args)
    def damage(self, d: int) -> int:
        "Reduce hp by d but never goes into negative, then return damage dealt; exists so we can add modifier in it if necessary."
        if DEV() and type(d) != int:
            warn(f"Card with name \"{self.name}\" took non integer damages; converting value to int. /!\\ PLEASE FIX: automatic type conversion is disabled when out of DEV mode /!\\")
            d = int(d)
        if d > self.hp:
            dealt = self.hp
            self.hp = 0
            return dealt
        self.hp -= d
        return d
    def attack(self, attack: Attack, other) -> int: # other is CreatureCard.
        "Make `self` use `attack` on `other` and return damage dealt."
        return other.damage(attack.power * ifelse(self.element.effective(other.element), 12, 10) // ifelse(other.element.resist(self.element), 12, 10))
@dataclass
class CommanderCard(CreatureCard):
    # Note: all field of CommanderCard must have a default value as CreatureCard ends with one. (inheritance)
    def iscommander(self) -> bool: return True
    
@dataclass
class SpellCard(AbstractCard):
    def from_json(json: dict, id: int):
        return SpellCard(json["name"], id, json["element"])

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
    def __init__(self, name: str, commander: CommanderCard, deck: list = ifelse(DEV(), getCARDS(), [])):
        if len(deck) != Constants.default_deck_size:
            raise f"Player {name} tried to play with too few cards (error handling will be done later)."
        self.name = name
        self.commander = commander.copy() # copy otherwise the same commander would be shared between players
        self.deck = deck.copy()           # avoid shared, notably if deck is left to default in DEV() mode, as Python is a terrible language
        rng.shuffle(self.deck)
        self.discard = [] # is not shared
        self.hand = []
        self.draw()
        self.energy = Constants.default_energy_per_turn
        self.max_energy = Constants.default_max_energy
        self.energy_per_turn = Constants.default_max_energy
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
        if self.commander.hp <= 0: # don't mind that I'll change it it's really spaghetti coded rn
            return True
        return False

@dataclass
class Board:
    player1: Player
    player2: Player
