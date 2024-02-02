# Basics
Player are refered as `p{i}` (e.g. `p1` is player1, i.e. server) and board index as `p{i}{j}` with `{j}` letter (e.g. `p2b` is the 2nd index (i.e. 1) of player2 (i.e. client)'s field.)\
Note: field size of 27 or more is not supported.\
Note: commander are refered through `p{i}@`

`{element}`, `{return_code}` and `{target_mode}` are given as integers.

# Initialization
For each player:

`player|p{i}|{Player Name}|{commandername}|{max_hp}|{element}`\
`hand|p{i}|{Card Name}|{...}`

# Actions
`place|p{i}{j}|{Card Name}|{max_hp}|{element}`\
`discard|p{i}|{Card Name}`\
`draw|p{i}|{Card Name}`\
`defeat|p{i}{j}`\
`spell|{Spell Name}|p{i}{j}|{target_mode}`\
`attack|p{i1}{j2}|{Attack Name}|p{i2}{j2}|{target_mode}|{return_code}`\
`-damage|p{i}{j}|{current_hp}/{max_hp}`\
`-heal|p{i}{j}|{current_hp}/{max_hp}`\
`passive|p{i}{j}|{Passive Name}`\
`-formechange|p{i}{j}|{Forme Name}|{hp}/{max_hp}|{element}`\
`-element|p{i}{j}|{new_element}` Note: not yet supported as useless.\
`-hypno|p{i}{j}|p{i'}{j'}`

# Misc
`chat|{Player Name}|{content}`\
`win|p{i}|{Player Name}`\
`raw|{msg}`\
`energy|p{i}|{current}/{max}|{per_turn}`\
`turn|{turn}`\
`-ccharge|p{i}|{amount}`
