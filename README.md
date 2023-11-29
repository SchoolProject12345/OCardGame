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

## Contributors
- [AxaQuilPre](https://github.com/AxaQuilPre)
- [OrnitOnGithub](https://github.com/OrnitOnGithub)
- [DrN1ghtW0lf](https://github.com/DrN1ghtW0lf)
- [andrei73457](https://github.com/andrei73457)
- [ErdaBerda](?)
- [flowey0101](https://github.com/flowey0101)
- [swisscookieman](https://github.com/swisscookieman)
- [luiza1607](https://github.com/luiza1607)
- [UgandanSuperfighter](https://github.com/UgandanSuperfighter)
