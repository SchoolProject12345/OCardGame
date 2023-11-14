# Cards
Cards must be defined in `cards.json` as follow:
```js
// Creature and Commander Cards
{
 "type":"creature",
 "name":"{card's name}",
 "element":"{element string}",
 "hp":"{card's max HP}",
 "attacks":[{/*attack object*/}, /*...*/],
 "passives":[{/*passive object*/}, /*...*/],
 "commander":false // true for commanders, non-necessary for basic creatures.
}
// Spell Cards
{
 "type":"spell",
 "name":"{card's name}",
 "element":"{element string}",
 "on_use":{/*attack object*/}
}
```
With possible values for field `"element"` being: `"water"`, `"fire"`, `"air"`, `"earth"` and `"chaos"`

## Complete Example
```js
{
 "type":"creature",
 "name":"Cute Cat Riding a Monstruous Mystical Flying Fish",
 "element":"chaos",
 "hp":70,
 "attacks":[
  {
   "name":"Indiscrimante (Neutral) Draining Attack That Destroy This Cat Mental Health™",
   "cost":5,
   "power":30,
   "target_mode":"self",
   "effect":{
    "type":"union",
    "effect1":{
     "type":"drain", // draining only apply to sub-effect, not to main damages.
     "num":2,
     "den":5, // heal ⅖ of damages done.
     "effect":{
      "type":"target_change",
      "new_target":"all",
      "effect":{
       "type":"damage",
       "amount":40 // isn't affected by weakness/resistance as it come from a "damage" effect and will heal the Cat as inside a "drain" block.
      }
     }
    },
    "effect2":{
     "type":"state_change",
     "new_state":"blocked" // there is no target_change effect before, so the effect is using the attack's target: self
    }
   }
  },
  {
   "name":"Coinflip of Chaos",
   "cost":1,
   "power":0,
   "target_mode":"commander",
   "effect":{
    "type":"union",
    "effect1":{
     "type":"with_probability",
     "probability":0.4,
     "effect1":{ // has 40% chance of happening
      "type":"target_change",
      "new_target":"self",
      "effect":{"type":"damage","amount":70}
     },
     "effect2":{ // has 60% chance of happening
      "type":"damage",
      "amount":100 // is this card balanced?
     }
    },
    "effect2":{
     "type":"with_probability",
     "probability":0.3,
     "effect1":{
      "heal":30
     } // effect2 is null by default
    }
   }
  }
 ],
 "passives":[/*unimplemented yet*/]
} // commander is set to false by default
```
See below for more details

## Attack
An attack object is formed as follow:
```js
{
 "name":"attack's name",
 "cost":0, // energy cost
 "power":0, // base damage
 "target_mode":"{TargetMode string}",
 "effect":{/*effect object*/}
}
```
With possible values for field `"target_mode"` being:
    `"self"`: the user of the move.
    `"foes"`: all of the opponent's cards.
    `"allies"`: all of your cards.
    `"target"`: the card targeted by the attack.
    `"commander"`: your opponent's commander
    `"allied_commander"`: your commander.
    `"all_commanders"`, `"both_commanders"` or `"commanders"`: both commanders
    `"all"`: every card but the user.
    `"massivedestruction"` or `"guarenteedchaos"`: EVERY card.

Effect objects exists through different type as follow:

### Effect Union:
Effect union apply two effect, allowing to make attack with two completely independant effects.
```js
{
 "type":"union",
 "effect1":{/*effect object*/},
 "effect2":{/*effect object*/}
}
```
To combine 3 or more effect, one may use chain of nested unions.
(**TODO**) using the following syntax to form a chain of nested unions can be automatically created from an arbitrary amount of effect objects.
```js
{
 "type":"union_chain",
 "effects":[{/*effect object*/}, /*...*/]
}
```

### Target Change:
Change the target of every sub-effects to a new target_mode.
```js
{
 "type":"target_change",
 "new_target":"{TargetMode string}",
 "effect":{/*effect object*/}
}
```

### State Change:
Change the state of every target(s).
```js
{
 "type":"state_change",
 "new_state":"{State object}"
}
```
With possible values of field `"new_state"` being:
    `"default"`: has no effect.
    `"block"` or `"blocked"`: cannot attack.
    `"invisible"`: cannot attack nor be targeted.

### HP Manipulation
Inflict indirect damages to target(s), which ignore any change.
```js
{
 "type":"damage",
 "amount":0
}
```
Heal target(s) by `amount`.
```js
{
 "type":"heal",
 "amount":0
}
```
Heal from a ratio of total damage dealt in sub-effects.
```js
{
 "type":"drain",
 "num":0,
 "den":1,
 "effect":{/*effect object*/}
}
```

### Energy Manipulation
```js
{
 "type":"add_energy",
 "energy":0, // add to the user's owner's raw energy
 "max_energy":0, // add to the user's owner maximum's energy
 "energy_per_turn":0 // add to the user's owner's energy per turn
}
```


### Conditional Effect:
```js
{
 "type":"with_probability",
 "probability":0.5 // probability between 0.0 and 1.0
 "effect1":{/*effect object*/}
 "effect2":{/*effect object*/}
}
```
Apply either `effect1` or `effect2`, chosen at random, with `probability` of being effect1.
`probability` defaults to 0.5 and `effect2` to no effect.
