# The Card Game

from dataclasses import dataclass # easier Class declaration
from enum import IntEnum # for clear, lightweight (Int) elements/state.
from numpy import random as rng # for shuffle function/rng effects

def getcards() -> dict: # only used to define `global CARDS`
    io = open("cards.json");
    json = eval(io.read()); # assuming people aren't stupid enough to write invalid JSON in cards.json. Don't forgot commas.
    io.close();
    id = -1 # starts at -1 + 1 = 0
    return [AbstractCard.from_json(card, (id := id + 1)) for card in json if not "example" in card] # please note that whether example is put to true or false it is excluded from the list.
CARDS = getcards();
DEV   = True; # enable debugging

 # convenience functions, might be moved to a separate file later.
def getordef(d: dict, key, default):
    """
        getordef(dict, key, default)
    
    Get value at `key` from `dict` if it exist, returns `default` otherwise.

    # Examples
    ```py
    >>> getordef({"foo":"bar"}, "foo", 3)
    "bar"
    >>> getordef({"foo":"bar"}, "baz", 3)
    3
    ```
    """
    if key not in dict:
        return default
    return dict.get(key)
def warn(*args, dev = DEV, **kwargs):
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
    if dev: # hard check to avoid mistakes (and to avoid taking DEV from global scope, which would hugely slow down the code)
        print("\x1b[1;33m┌ Warning:\n└ ", *args, "\x1b[0m", **kwargs) # might not work in every terminal, but should in VS Code
    return True # this is definitevely not spaghetti code.

class Element(IntEnum):
    elementless = 0 # used instead of None as a placeholder; shouldn't be used otherwise (except if that's intentional?).
    rock = 1 # I added it we never know. (Technically you could replace it by earth)
    paper = 2
    scissor = 3
    water = 4
    fire = 5
    air = 6
    earth = 7
    chaos = 8 # Weak defense against all  (x1,2 damage taken) but powerful attack against all (x1.2 damage output)
    def from_str(name: str):
        match name.lower():
            case "rock": return Element.rock
            case "paper": return Element.paper
            case "scissor": return Element.scissor
            case "water": return Element.water
            case "fire": return Element.fire
            case "air": return Element.air
            case "earth": return Element.earth
            case "chaos": return Element.chaos
            case _: return warn(f"Tried to form an Element from \"{name}\"; returned Element.elementless instead.") and Element.elementless
    def from_json(json: dict):
        if "element" not in json:
            return warn(f"Card with name {json["name"]} has no element defined (don't do that intentionally please)") and Element.elementless
        return Element.from_str(json["element"])
    def effectiveness(self, other):
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
        if self == Element.chaos or other == Element.chaos:
            return True

        if self == Element.rock and other == Element.scissor:
            return True
        if self == Element.paper and other == Element.rock:
            return True
        if self == Element.scissor and other == Element.paper:
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
    def resist(self, other):
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
        if self == Element.chaos or other == Element.chaos:
            return False
        return other.effectiveness(self)
class State(IntEnum):
    default = 0 # placeholder
    defeated = 1 # I suppose

@dataclass
class AbstractCard:
    name: str
    id: int
    element: Element # all card types until now have an element; if a new card type doesn't require an element, we'll force the element field to Element.elementless in the from_json constructor (which allows flexibility with Element.efectiveness).
    def __init__(self, *args):
        warn("AbstractCard class serves only as a superclass; initialize object of more specific classes instead.")
    def from_json(json: dict, id: int): # id from index in list
        "Dispatch the from_json method according to \"type\" field. The method hence doesn't return an AbstractCard object."
        type = json["type"]
        if type == "creature":
            return CreatureCard.from_json(json, id)
        if type == "element":
            return ElementCard.from_json(json, id)
        if type == "spell":
            return SpellCard.from_json(json, id)
        warn(f"Card with name {json["name"]} has type {type} which isn't handled.")
            
@dataclass
class CreatureCard(AbstractCard):
    hp: int
    state: State = State.default
    def from_json(json: dict, id: int):
        args = (
            json["name"],
            id,
            Element.from_json(json),
            json["hp"],
        )
        if getordef(json, "commander", False): # so we don't need to define "commander":false for every card (might be changed later to "type":"commander" though).
            return CommanderCard(*args)
        return CreatureCard(*args) # use default argument for State (it means all CreatureCard share the same state object due to Python being Python)
@dataclass
class CommanderCard(CreatureCard):
    pass # Note: all field of CommanderCard must have a default value as CreatureCard ends with one. (inheritance)

@dataclass
class ElementCard(AbstractCard):
    def from_json(json: dict, id: int):
        return ElementCard(json["name"], id, json["element"])
    
@dataclass
class SpellCard(AbstractCard):
    def from_json(json: dict, id: int):
        return SpellCard(json["name"], id, json["element"])
