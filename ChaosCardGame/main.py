# The Card Game
"""
Card Type {
    Modular Elements (Rock Paper Scissor / Water Fire Air Earth)
    Creature, Terrain, Spell
}
Rules {
Rock<Paper<Scissor<, Water>Fire>Air>Earth>
Deck of N cards
Special Effect
Leader Card => HP
}
"""
from dataclasses import dataclass # easier Class declaration
from enum import IntEnum # for clear, lightweight (Int) elements/state.
from numpy import random as rng # for shuffle function/rng effects?
def getcards() -> dict:
    io = open("cards.json");
    json = eval(io.read()); # assuming people aren't stupid enough to write invalid JSON in cards.json.
    io.close();
    id = -1 # starts at -1 + 1 = 0
    return [AbstractCard.from_json(card, (id := id + 1)) for card = json]
CARDS = getcards();
class Element(IntEnum):
    elementless = 0, # used instead of None as a placeholder; shouldn't be used otherwise (except if that's intentional?).
    rock = 1, # I added it we never know.
    paper = 2,
    scissor = 3,
    water = 4,
    fire = 5,
    air = 6,
    earth = 7,
    chaos = 8 # It's already chaotic, it's already too late.
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
            case _: return Element.elementless # not sure this works in Python, not very useful anyway, it's just bug-handling but honestly I shoudld rather throw an error or at least print a warning.
    def effectiveness(self, other): # `other` is Element I can't annote because Python.
        match self:
            case _: return # I don't know what to return
class State(IntEnum):
    default = 0 # state aren't listed
class AbstractCard:
    def __init__(self, name: str, id):
        pass
    def from_json(json: dict, id: int): # id from index in list
        with type as json["type"]:
            if type == "creature":
                return CreatureCard.from_json(json, id)
            if type == "element":
                return ElementCard.from_json(json, id)
            if type == "spell":
                return SpellCard.from_json(json, id)
@dataclass
class CreatureCard(AbstractCard):
    name: str = "",
    id: int = None, # type annotation in Python is completly useless. I hate Python.
    element: Element = Element.elementless, # placeholder
    state: State = State.default
    def from_json(json: dict, id: int):
        CreatureCard(json["name"], id, Element.from_str(json["element"]), State.default)
@dataclass
class ElementCard(AbstractCard):
    def from_json(json: dict, id: int):
        return # Avoid crash, MUST BE MODIFIED
@dataclass
class SpellCard(AbstractCard):
    def from_json(json: dict, id: int):
        return # Avoid crash, MUST BE MODIFIED
