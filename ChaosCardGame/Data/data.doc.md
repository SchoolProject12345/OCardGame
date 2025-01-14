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
   "target_mode":"user",
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
      "new_target":"user",
      "effect":{"type":"damage","amount":70}
     },
     "effect2":{ // has 60% chance of happening
      "type":"damage",
      "amount":100
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
### TargetMode
A TargetMode is either a `str`ing or a `list` of strings.
Strings represent elementary targets or flags, whereas list of strings allow to create **Target Union**.\
Here are the different elementary target that can be placed inside a list:
- `"target"`: the target targeted by the player attacking.
- `"foes"`: all foes but commander.
- `"allies"`: all allies but commander.
- `"user"`: the attack user.
- `"commander"`: the opponent's commander
- `"allied_commander"`: the owner's commander.

Additionaly, the following can be set as **flags**, flags do not change the targets themselves but the behavior of the targetting:
- `"can_self"`: allow this attack to be used on user.
- `"nocommander"`: prevent this attack to be used on a commander.

Finally, the following can be used as alliases:
- `"all"` <=> `["allies", "foes"]`
- `"massivedestruction"` <=> `["all", "commander", "allied_commander"]`

Example of complex `TargetMode`s:
```js
["foes", "nocommander"]  // prevent from targetting the commander with a foes target, useful in case of redirect which would deal way to much damages.
["foes", "commander"]  // target commander in addition of foes.
["target", "canself"]  // allow to damage/buff self if necessary.
["foes", "commander", "user"]  // damage all foes but user as a drawback.
```

To select a (or multiple) random target among the target distribution, use the following effect:
```js
{
 "type":"random_targets",
 "sample":2 // number of targets sampled, defaults to one.
 "effect":{/*effect object*/} // "effect" is applied on each target selected
}
```
## Passive
A Passive object is formed as follow:
```js
{
 "name":"passive's name",
 "trigger":"{PassiveTrigger string}",
 "effect":{/*effect object*/}
}
```
With possible values for field `"trigger"` being:
- `"endofturn"`: applied on self at the end of each turn.
- `"whenattack"` or `"whenattacking"`: applied with same property as the attack whenever attacking (before damages).
- `"whenplaced"`: applied on self when card is placed for the first time.
- `"whendefeated"`: applied on attacker when defeated directly.
- `"whenattacked"`: applied on attacker when attacked.
- `"whendamaged"`: applied on damager when damaged only, damage taken can be retrieved through Numeric `"damage_taken"`.
- (***upcoming***)
- `"whendiscarded"`: applied on allied commander when discarded, either when defeated or from hand.
- `"whendrawn"`: applied on allied commander when drawn.

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
To combine any number of identical objects, use this syntax:
```js
{
 "type":"repeat",
 "effect":{/*effect object*/},
 "n":1 // number of time to repeat the effect for.
}
```
Additionaly, each effect inside the repeat are evaluated with a special property that can be retrived through `{"type":"property","path":"repeat_depth","attr":""}` and used as an int ∈ [0;n) inside the effects.

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
    `"unattacked"`: allow to attack one more time during turn, if already attacked before effect take place. This doesn't always change the targets' actual states.
    `"damageless"`: cannot receive damage nor new State.
    `"cloudy"`: all attacks are single-random-targeted.
    `"monotonous"`: damages are not affected by weaknesses.
Cleanse effects and tags by tags. `by_tags` defaults to `["+", "-", "+-"]`. Default supported tags are #`+` (positive state/effect), #`-` (negative state/effect) & #`+-` (positive with drawback state/effect). All effects than can be tagged should be tagged (i.e. loop & delay) for this to work properly.
```
{
 "type":"cleanse",
 "by_tags":["+", "-", "+-"]
}
```

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
Redirect `amount` damages from `from` distribution to targets.
```js
{
 "type":"direct",
 "from":"{TargetMode string}",
 "amount":0
}
```
Add to max HP and heal (doesn't change missing health):
```
{
 "type":"addmaxhp",
 "amount":0
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
Additionaly, a `"player"` field may be set to either `"foe"` or `"ally"` to change the targeted player.

### Creature Maniplation
Summon a creature card on the user's owner's board if possible
```js
{
 "type":"summon",
 "count":1, // number of creature to spawn; defaults to 1
 "creature":{/*creature object*/}
}
```
Additionaly, `"creature"` may be replaced by `"by_name"` allowing to summon an already existing creature, hence breaking a possible loop.
```js
{
 "type":"summon",
 "count":1,
 "by_name":"Chaos Brigade" // equivalent to "by_name":"chaosbrigade"
}
```
Change the target∙s owner to user's owner, changing their place on the field. Please don't allow it to target commanders. It wouldn't work anyway.
```js
{"type":"hypnotize"} // yeah that's it, no fields.
```
Change the target's own card to `new_forme`. Please note that when the card is discarded, only the new forme will be avaible to redraw, so one might want to add a passive with trigger "whenplaced" to revert to the base forme. Cost of the `new_forme` is also necessary for this same reason.
```js
{
 "type":"changeforme",
 "new_forme":{/*creature card object*/}
}
```
Taunt the targets to a random target from the `new_targets` distribution for `duration` (set to -1 or 65535 for infinite taunt). A taunted creature's target automatically changed to its taunter whenever it attacks. `duration` is in number of attacks rather than number of turns.
```js
{
 "type":"taunt",
 "new_targets":"{TargetMode string}",
 "duration":1
}
```

### Board Resize
Change the number of slots available by `"target"` (either `"active"` or `"unactive"` player) by `"delta"`, but never goes below 1 (in case `"delta"` is negative), nor above 26,  nor remove a creature to remove a slot (if board is full, no slot can be removed).
```js
{
 "type":"boardresize",
 "target":"unactive", // defaults to "unactive"
 "delta":-1
}
```

### Discard
Discard `"delta"` cards from the `"player"` (either `"owner"` or `"opponent"`) player.
```js
{
 "type":"discard",
 "delta":1,
 "player":"owner"
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
 "delay":1,
 "tags":[]
}
```
Apply `effect` at the end of every turn, until the user is defeated if `"infinite"` is set to `false` (default value).
```js
{
 "type":"loop",
 "effect":{/*effect object*/},
 "infinite":true
 "tags":[]
}
```
Evaluate `effect` if `value` is evalutated greater or equal than `cond`, evaluate `else` otherwise.
```
{
 "type":"if",
 "value":{/*Numeric expr*/},
 "cond":/*Numeric expr or int, defaults to 0*/
 "effect":{/*effect object*/}
 "else":  {/*effect object*/}
}
```

### Hardcode
Hardcoding is sometime unavoidable. You can use the following syntax to run completely arbitrary Python code. Additionaly, a `"desc"`ription of the effect may be given for documentation (do it). Some hardcoding might require to go deeper into the code, in which case this may still be used as an effect with only `"desc"` for documentation.\
Note₁₂: All variables from `Core/core_main.py`'s AbstractEffect.eval's scope are available.
Note₂: You must really know you're doing before using this.
```
{
 "type":"hardcoded",
 "desc":"Does some cool stuff."
 "code":"kwargs['board'].logs.append(ifelse(kwargs['user'].taunt is not None, f"raw|{kwargs[\"user\"].name} is taunted!', 'raw|Hello world!'))" // supports statements as well.
}
```

## Numeric Expressions
In most cases, integers in effect objects can be replaced by other object which are evaluated to integers every time the effect is applied.

### List of targets' HP
Eval into a `list`, which must then be further processed into a `int`.
```js
{"type":"HPs", "target_mode":"{TargetMode string}"}
```

### GCD
Return the GCD of all elements in the evaluation of sample.
```js
{
 "type":"gcd",
 "sample":{/*numeric expression returning a list (e.g. list of HP)*/}
}
```

### Sum
Return the sum of all elements in the evaluation of sample. This can be used with a single-valued list to obtain its first (and only) element.
```js
{
 "type":"sum",
 "sample":{/*numeric expression returning a list (e.g. list of HP)*/}
}
```

### Count
Return the number of targets matching either by any tag or by any element. Both `tags` and `elements` are optional arguments, defaulting to an empty set.
```js
{
 "type":"count",
 "tags":["...", /*...*/],
 "elements":["{Element string}", /*...*/]
}
```

### Energy Count
Return the number of energy by type. Type can be either "max", "current" or "per_turn".
```js
{
 "type":"energy",
 "type":"current"
}
```

### Multiplication
Multiply evaluate numeric by rational.
```js
{
 "type":"mul",
 "times":{/*numeric expr*/},
 "num":2,
 "den":1
}
```

### Addition
a + b
```js
{
 "type":"add",
 "a":{/*...*/},
 "b":{/*...*/}
}
```

### Property
If you want to go more into code, you can access a kwarg property (AKA attribute) through the following syntax:
```js
{
 "type":"property",
 "path":"user",
 "attr":"card.max_hp"
}
```
In this example, it will first search for the user's card and then this card's max_hp. It is equivalent to the code:
```py
kwargs["user"].card.max_hp
```
This might have many uses, such as:
```py
kwargs["user"].hp
kwargs["user"].card.cost
kwargs["board"].turn
kwargs["repeat_depth"]
```

### Current turn
```js
{"type":"turn"}
```

### Damage Taken
For passive trigger `whendamaged`.
```js
{"type":"damage_taken"}
```
