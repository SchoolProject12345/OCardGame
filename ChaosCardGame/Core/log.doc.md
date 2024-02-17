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
 "arena":Core.core_main.Arena.själøssmängd # Arena enum object, see Core/core_main.py@Arena(IntEnum)
}
```
It is hence *completely* symmetrical; a code written to display from the host's perspective would work to display the client's perspective without *any* modification, as long as **no method are used outside of `ReplayHandler`'s**.
This is also valid for other methods (i.e. [`handle.run_action`](#actions)).

# Actions
Actions are applied through the high-level `handle.run_action(action: str)`. The client automatically send ran action to the host, which are automatically executed with error and cheat handling. `ReplayHandler` doesn't support this method, resulting in a crash. [Logs](#logs) resulting form actions are automatically read by the host and sent to the client which read them.

## Universal
`attack|{ally index*}|{attack index}|{target index*}`\
`spell|{hand index}|{target index*}`\
`place|{hand index}|{board index}`\
`discard|{hand index}`\
`endturn` causes to draw and end the turn.\
`chat|{msg}` sends `{msg}` in chat.

### Indices
Indices marked with `*` can be any of the following:
- `ally{i}`: `{i}`th creature on your side of the board.
- `foe{i}`: `{i}`th creature on your opponent's side of the board.
- `allied_commander`: your commander.
- `commander`: your opponent's commander.\
Other indices are regular integer, starting from 0. Some indices have aliases.

### Examples
`handle.run_action("attack|ally1|0|foe2")`
requests the 2nd card on the player's board to use its 1st (i.e. Default) attack on the 3rd card of their opponent's board.\
`handle.run_action("attack|allycommander|1|foe0")`
requests the player's commander to use its ultimate on the 1st card of their opponent's board.\
`discard|3` requests to discard the 4th card of the player's hand.

## DEV()-mode (Text-based)
`help`
`doc|{card name}`
`doc|{card name}|noimg`
`dochand`
`showboard`

# Logs
## Basics
Logs are what are send resulting of actions. Each handler automatically read logs, send them (if host) and update its state with them. Logs are all that is necessary to reconstruct a game.

Player are refered as `p{i}` (e.g. `p1` is player1, i.e. server) and board index as `p{i}{j}` with `{j}` letter (e.g. `p2b` is the 2nd index (i.e. 1) of player2 (i.e. client)'s field.)\
Note: field size of 27 or more is not supported.\
Note: commander are refered through `p{i}@`

`{arena}`, `{element}`, `{return_code}` and `{target_mode}` are given as integers.

## Initialization
For each player:

`player|p{i}|{Player Name}|{Commander Name}|{max_hp}|{element}`\
`boardsize|p{i}|{size}`\
`-firstp|p{i}`\
`arena|{arena}`

## Main
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
`-hypno|p{i}{j}|p{i'}{j'}`\
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
Hide opponent's hand.
