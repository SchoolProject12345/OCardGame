# Game State
Is retrieved through the method `handle.get_state()` as a dict.\
The game state follow this structure:
```py
{
 "remote":{
  "name":"", # Player's name (e.g. "Ånyks")
  "deck_length":core.Constants.default_deck_size, # number of card remaining in deck.
  "hand":[], # ui_formated name (e.g. "wtr_shiao") of cards in hand.
  # Note: in remote's hand, all cards are nammed as "hidden". (TODO)
  "commander":{"name":"","hp":600,"max_hp":600,"element":0,"charges":0}, # Self explanatory
  "board":[], # list[None | dict[str, Any]] with None meaning that no cards are at this index,
  # and the dict has the same structure as {"name":"", "hp":0, "max_hp":0, "element":0},
  # representing an ActiveCard object
  "discard":[], # ui_formated name of cards in discard.
  # Self explanatory:
  "energy":core.Constants.default_energy_per_turn,
  "max_energy":core.Constants.default_max_energy,
  "energy_per_turn":core.Constants.default_energy_per_turn
 },
 "local":{
  # Same as remote: completely symmetrical
 },
 "turn":0,
 "isactive":True, # True is it is local's (self's) turn, False otherwise
 "arena":0 # Arena as an integer, see `./Core/core_main.py@Arena(IntEnum)` to see the different values and their meaning.
}
```
It is hence *completely* symmetrical; a code written to display from the host's perspective would work to display the client's perspective without *any* modification, as long as **no method are used outside of `ReplayHandler`'s**.
This is also valid for other methods (i.e. `handle.run_action`).

# Logs
## Basics
Player are refered as `p{i}` (e.g. `p1` is player1, i.e. server) and board index as `p{i}{j}` with `{j}` letter (e.g. `p2b` is the 2nd index (i.e. 1) of player2 (i.e. client)'s field.)\
Note: field size of 27 or more is not supported.\
Note: commander are refered through `p{i}@`

`{element}`, `{return_code}` and `{target_mode}` are given as integers.

## Initialization
For each player:

`player|p{i}|{Player Name}|{Commander Name}|{max_hp}|{element}`\
`boardsize|p{i}|{size}`\
`-firstp|p{i}`

## Actions
`place|p{i}{j}|{Card Name}|{max_hp}|{element}`\
`discard|p{i}|{Card Name}`\
`draw|p{i}|{Card Name}`\
`defeat|p{i}{j}`\
`spell|{Spell Name}|p{i}{j}|{target_mode}|{return_code}`\
`attack|p{i1}{j2}|{Attack Name}|p{i2}{j2}|{target_mode}|{return_code}`\
`-damage|p{i}{j}|{current_hp}/{max_hp}`\
`-heal|p{i}{j}|{current_hp}/{max_hp}`\
`passive|p{i}{j}|{Passive Name}`\
`-formechange|p{i}{j}|{Forme Name}|{hp}/{max_hp}|{element}`\
`-element|p{i}{j}|{new_element}` Note: not yet supported as useless.\
`-hypno|p{i}{j}|p{i'}{j'}`
`-summon|p{i}{j}|{Card Name}|{max_hp}|{element}`

## Misc
`chat|{Player Name}|{content}`\
`win|p{i}|{Player Name}`\
`raw|{msg}`\
`energy|p{i}|{current}/{max}|{per_turn}`\
`turn|{turn}`\
`-ccharge|p{i}|{amount}`\
`shuffle|p{i}`

# TODO
Add `version|x.y.z` log.\
Read minor logs together and draw logs together.\
Add optional `from` kwarg through `head|log|[from] Somewhere` e.g. `-damage|p1a|60/70|[from] Default Attack`.\
Hide opponent's hand.
