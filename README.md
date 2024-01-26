# OCardGame
OCardGame is a little chaotic card game coded exhaustively in Python. Inspired by the popular game *Magic The Gathering*, fight powerful monsters through special abilities and level up your card companions!

## Rules
- Each player start with one commander and a deck of 30 cards, drawing 5 cards from it.
- The player who move first is determined by 5 rounds of Rock Paper Scissors.
- During their turn a player may place (costing energy) or discard a card from their hand, attack with their creatures (once per turn per creature costing energy) and use spells (costing energy)
- At the end of their turn, the player gain energy and draw cards until they have 5 in hand.

## Coding Conventions & Rules
- All variables, field and function should be in lowercase or snake_case *(e.g. `from_json`, `getordef`)*
- All constants (variables that are indented not to change, as constants does not exist in Python) should be in UPPERCASE or UPPER_SNAKE_CASE *(e.g. `CARDS`)*
  - You may want to define some constants using functions to avoid too much performance loss when used at local scope. In this case, name it similarly to how you would name the constant *(e.g. `getCARDS()`, `DEV()`)*
- All type/class should be in UpperCamelCase *(e.g. `AbstractCard`)*
- All commit message must be a an exhaustive descirption of the new feature.
- All commits must incude at least one **finished** new feature.

### Libraries:
- Must be specified in the `requirements.txt` file.
- Must be only used if **truly** necessary.

## Play
Launch `launcher_dev.py` and follow the instructions to connect with a peer.
Once connected with another peer (or in localhost), write "help" to get a list of actions.

## Initialization (`DEV()`-mode)
The `os.chdir("")` at line 7 must have its argument replaced by the directory in which the file is stored.
After running the code, two players objects must be initialized, and a board must be initialized from them:
```py
player1 = Player("Player1's name", getCOMMANDERS()["commandername1"], Player.get_deck()) # third argument can be replaced by any list of 30 AbstractCard objects (from the `getCARDS()` list)
player1 = Player("Player2's name", getCOMMANDERS()["commandername2"], Player.get_deck()) # an `AIPlayer`, which plays automatically, can be initialized instead.
board = Board(player1, player2)
```

## Actions (`DEV()`-mode)
Actions usually do not check whether the player is able to perform the action. The user must do its own error/cheat-handling.
### Drawing
Is automatically done when ending the turn with `board.endturn()`
### Placing
`board.active_player.place(i, j)` where `i` is the index of the card in hand and `j` is the index to place the card on, on the board. Returns `True` if sucessful, `False` otherwise.
### Discarding
`board.active_player.handdiscard(i)` return the `i`th card of the active player's hand after discarding it. There is no error handling, the user must hence ensure to chose a valid index. 
`board.active_player.iddiscard(id)` discard the card with id `id`, which can be acessed through `card.id`. Return `None` if the card doesn't exist in the player's hand.
### Attacks
```py
board.active_player.active[j1].attack(
  board.active_player.active[j1].attacks[k]
  board.unactive_player.active[j2]
)
```
With
- `j1`: the index on board of the attacker
- `k` : the index of the attacker's attack
- `j2`: the index on board of the target (`unactive_player` can be changed with `active_player` in order to target a card from the same side as the attacker)
This is really ugly and will probably be changed soon.
### Spells
`board.active_player.hand[i].use(board.unactive_player.active[j])` where `i` is the index in hand of the spell to use and `j` the index on board of its target. The spell is automatically discarded if sucessful.
### Targets
Attacks and spell can use the following targets:
`board.active_player.active[j]` targets a card owned by the player, at the `j`th index on board.
`board.active_player.commander` targets the player's commander.
`board.unactive_player.active[j]` targets a card owned by the player's opponent, at the `j`th index on board.
`board.unactive_player.commander` targets the player's opponent's commander.

## Contributors
- [AxaQuilPre](https://github.com/AxaQuilPre)
- [OrnitOnGithub](https://github.com/OrnitOnGithub)
- [DrN1ghtW0lf](https://github.com/DrN1ghtW0lf)
- [andrei73457](https://github.com/andrei73457)
- [ErdaBerda](????????????????????????????????)
- [flowey0101](https://github.com/flowey0101)
- [swisscookieman](https://github.com/swisscookieman)
- [luiza1607](https://github.com/luiza1607)
- [UgandanSuperfighter](https://github.com/UgandanSuperfighter)
