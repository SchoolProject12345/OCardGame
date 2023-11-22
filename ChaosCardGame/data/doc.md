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
### Creature, Attacks and Passives
```js
{
 "type":"creature",
 "name":"Cute Cat Riding a Monstruous Mystical Flying Fish",
 "element":"chaos",
 "hp":70,
 "attacks":[
  {
   "name":"Indiscrimante (Neutral) Draining Attack That Destroy This Cat Mental Health™",
   "cost":2,
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
       "damage_mode":"direct"
       "amount":40 // will heal the Cat as inside a "drain" block.
      }
     }
    },
    "effect2":{
     "type":"state_change",
     "new_state":"blocked" // there is no target_change effect before, so the effect is using the attack's target: self
     "for":2
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
  },
  {
   "name":"Unlimited Attack",
   "cost":1,
   "target_mode":"target",
   "power":40,
   "effect":{
    "type":"target_change",
    "new_target":"self",
    "effect":{"type":"state_change","new_state":"unattacked"} // can be used more than once per turn.
   }
  }
 ],
 "passives":[
  {
   "name":"Fish Crunching"
   "trigger":"endofturn",
   "effect":{"type":"heal","amount":15}
  }
 ]
} // commander is set to false by default
```
### Spells
```js
{
 "type":"spell",
 "name":"Large Fireball",
 "element":"fire",
 "on_use":{
  "name":"Throw",
  "cost":2,
  "power":80,
  "target_mode":"target",
  "effect":{"type":"null"}
 }
}
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
- `"self"`: the user of the move.
- `"foes"`: all of the opponent's cards.
- `"allies"`: all of your cards.
- `"target"`: the card targeted by the attack.
- `"commander"`: your opponent's commander
- `"allied_commander"`: your commander.
- `"all_commanders"`, `"both_commanders"` or `"commanders"`: both commanders
- `"all"`: every card but the user.
- `"massivedestruction"` or `"guarenteedchaos"`: EVERY card.
- `"random_chaos"` or `"random_target_mode"`: change the targetting mode to random. Yes.
To select a (or multiple) random target among the target distribution, use the following effect:
```js
{
 "type":"random_targets",
 "sample":2 // number of targets sampled
 "effect":{/*effect object*/} // "effect" is applied on each target selected
}
```
## Passive
A Passive object is formed as follow:
```js
{
 "name":"passive's name"
 "trigger":"{PassiveTrigger string}",
 "effect":{/*effect object*/}
}
```
With possible values for field `"trigger"` being:
- `"endofturn"`: applied on self at the end of each turn.
- `"whenattack"` or `"whenattacking"`: applied with same property as the attack whenever attacking (before damages).
- `"whenplaced"`: applied on self when card is placed for the first time.
- `"whendefeated"`: applied on attacker when defeated directly.
(***upcoming***)
- `"whendiscarded"`: applied on allied commander when discarded, either when defeated or from hand.
- `"whendrawn"`: applied on allied commander when drawn.
- `"whenattacked"`: applied on attack when attacked.

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
(***upcoming***) use the following syntax to form a chain of nested unions can be automatically created from an arbitrary amount of effect objects.
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
(***upcoming***) use the following syntax to use independant targets for the same effect. Overlaping units are affected multiple times (e.g. `"new_targets":["foes","massivedestruction","random_foe"]` would apply once the effect to the allies and commanders, twice to most active foes except one who would receive them thrice).
```js
{
 "type":"target_union",
 "new_targets":["{TargetMode string}", /*...*/]
 "effect":{/*effect object*/}
}
```

### State Change:
Change the state of every target(s).
```js
{
 "type":"state_change",
 "new_state":"{State string}"
}
```
Form a temporary State change (doesn't work for `"new_state":"unattacked"`), that last `"for"` a given number of turns, reverting afterward, with the following syntax:
```js
{
 "type":"state_change",
 "new_state":"{State string}",
 "for":1 // revert at the end of the targeted team next turn (at the end of the current turn if targeting an ally)
}
```
With possible values of field `"new_state"` being:
    `"default"`: has no effect.
    `"block"` or `"blocked"`: cannot attack.
    `"invisible"`: cannot attack nor be targeted.
    `"unattacked"`: allow to attack one more time during turn, if already attacked before effect take place. This doesn't actually change the targets' states.
    (unimplemented yet)
    `"damageless"`: cannot receive damage.

### HP Manipulation
Inflict damages to target(s), which depend on mode.
DamageModes include:
    `"direct"`: depend on weakness, resistance & other modification
    `"ignore_resist"` or `"ignore_resistance"`: depend on weakness & other modification, but not resistance.
    `"indirect"`: doesn't depend on anything else, reduce the target HP directly.
```js
{
 "type":"damage",
 "amount":0,
 "damage_mode":"{DamageMode string}"
}
```
Heal target(s) by `amount`.
```js
{
 "type":"heal",
 "amount":0
}
```
Damage Over Time, deal `"damage"` over `"time"` turns. A DOT over 1 turn is equivalent to indirect damage, with the only difference being that it happens at the end of the target's owner's next turn and hence doesn't count in draining.
As the name suggest, the `"damage"` field represent the *total* damage dealt over the time; in the following example the target would lose 2 HP, then 3 and finally 3, for a total of 8 damages over 3 turns.
```js
{
 "type":"dot",
 "damage":8,
 "time":3
}
```
Heal from a ratio of total damage dealt in sub-effects. This doesn't take end of turn damages (such as DOT) into account.
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


###  Control:
Apply either `"effect1"` or `"effect2"`, chosen at random, with `"probability"` of being `effect1`.
`probability` defaults to 0.5 and `effect2` to no effect.
```js
{
 "type":"with_probability",
 "probability":0.5 // probability between 0.0 and 1.0
 "effect1":{/*effect object*/}
 "effect2":{/*effect object*/}
}
```
Apply `"effect"` after `"delay"` turns of delay.
```js
{
 "type":"delay",
 "effect":{/*effect object*/},
 "delay":1
}
```
Apply `effect` at the end of every turn, until the user is defeated if `"infinite"` is set to `false` (default value).
```js
{
 "type":"loop",
 "effect":{/*effect object*/},
 "infinite":true // false is undefined
}
```
