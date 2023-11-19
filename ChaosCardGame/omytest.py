import discord
from discord.ext import commands
import os
os.chdir("")
import main
from numpy.random import choice, random
import re

intents = discord.Intents.default()
intents.message_content = True
BOT = commands.Bot(
    command_prefix="omy> ",
    intents=intents
)
def getPLAYERS(players: list = []) -> list:  return players

@BOT.event
async def on_ready():
    print("Omy is ready to cause chaos among OCG's players :3")

@BOT.command()
async def join(msg: commands.Context, players: list = getPLAYERS()):
    if len(players) > 2:
        return await msg.channel.send("There's already two players on the board. Isn't Omy a player?")
    id = str(msg.author.id)
    for player in players:
        if player.name == id:
            return await msg.channel.send("You're already in, even Omy knew that.")
    players.append(main.Player(id, main.getCOMMANDERS()["sircation"]))
    await msg.channel.send("Omy's notifying you that you're inded in the game cuz its stupid dev asked it to.")
    if len(players) == 2:
        players.append(main.Board(players[0], players[1]))

@BOT.command()
async def showboard(msg: commands.Context):
    players = getPLAYERS()
    if len(players) != 3:
        await msg.channel.send("Omy is sorry but there's not enough players for an OCG game.")
        return
    reply = f"Turn {players[2].turn} (<@{players[2].active_player.name}>'s)\n<@{players[0].name}>: {players[0].energy}/{players[0].max_energy} (+{players[0].energy_per_turn}) energies\n{players[0].commander.card.name} ({players[0].commander.hp}/{players[0].commander.card.max_hp})\n"
    for card in players[0].active:
        if card is None:
            reply += "none "
            continue
        reply += f"{main.cleanstr(card.card.name)} ({card.hp}/{card.card.max_hp}) "
    reply += f"\n\n<@{players[1].name}>: {players[1].energy}/{players[1].max_energy} (+{players[1].energy_per_turn}) energies\n{players[1].commander.card.name} ({players[1].commander.hp}/{players[1].commander.card.max_hp})\n"
    for card in players[1].active:
        if card is None:
            reply += "none "
            continue
        reply += f"{main.cleanstr(card.card.name)} ({card.hp}/{card.card.max_hp}) "
    reply += "\nUse `omy> showhand` to see your hand. This is espcially useful after drawing."
    if random() < 0.2:
        reply += ".. To see if you've drawn an Omy."
    await msg.channel.send(reply)

@BOT.command()
async def showhand(msg: commands.Context):
    id = str(msg.author.id)
    for player in getPLAYERS():
        if type(player) != main.Player:
            continue
        if player.name == id:
            cards = [main.cleanstr(card.name) for card in player.hand]
            reply = str(cards)
            if "omy" in cards:
                reply += "\nYou've got an Omy in your cards?! ✨"
            dm = await msg.author.create_dm()
            return await dm.send(reply)
    roast = choice([
        "Omy think you're brain is not superconducting enough, as you're didn't even join a game. How'd'ya wish to have a hand?",
        "Even Omy knew you don't have a hand.",
        "Only players have a hand. And Omy.",
        'Sadly, you don\'t have a hand. Omy can show you its: ["omy", "omy", "omy", "omy", "icbm"]. Pretty cool uh?',
        "Think before asking Omy thing it can obviously not do. Omy was sleeping!"
    ])
    await msg.channel.send(roast)

@BOT.command()
async def shutdown(msg):
    if msg.author.id == 482881970947227651:
        await msg.channel.send("OmicronBot has been shut down by <@482881970947227651>\nThat is mean... Why would you kill Omy...")
        await BOT.close()
    else:
        await msg.channel.send("Omy has an anti-shutdown protection.")

@BOT.command()
async def discard(ctx: commands.Context):
    players: list = getPLAYERS()
    if len(players) < 3:
        await ctx.channel.send("There's not enough people to discard cards yet. Join with `omy> join`.")
        return
    id: str = str(ctx.author.id)
    if id not in [players[0].name, players[1].name]:
        await ctx.channel.send("You're not even in the game! Stop trying to cheat! Only Omy is allowed to cheat!")
        return
    if id != players[2].active_player.name:
        roast: str = choice([
            "It's Omy's turn, not yours!",
            f"It's <@{players[2].active_player.name}>'s turn, not yours!",
            "Stop trying to cheat! Only Omy can.",
            "You're supposed to discard cards, not your brain. Without it, you don't even know when your turn is."
        ])
        await ctx.channel.send(roast)
        return
    if re.match(".*(\\d+)", ctx.message.content) is None:
        await ctx.channel.send("Omy couldn't find any number in your request. Perhaps... Omy is the number!")
    n: int = int(re.match(".*(\\d+)", ctx.message.content)[1])
    if 0 > n >= len(players[2].active_player.hand):
        await ctx.channel.send("You have no such card in hand. Maybe humans tend to forget list indices usually start with 0. Omy tend to forget that too.")
    card = players[2].active_player.handdiscard(n)
    reply: str = "Ya discarded this card: " + card.name
    if main.cleanstr(card.name) == "omy":
        reply += "\nDid ya discard Omy?! You're a monster!"
    await ctx.channel.send(reply)

@BOT.command()
async def place(ctx: commands.Context):
    players: list = getPLAYERS()
    if len(players) < 3:
        return await ctx.channel.send("There's not enough people to place cards yet. Join with `omy> join` (place Omy afterward, it wanna play too).")
    id: str = str(ctx.author.id)
    if id not in [players[0].name, players[1].name]:
        return await ctx.channel.send("You're not even in the game! Stop trying to cheat!" + main.ifelse(random() < 0.5, " Only Omy is allowed to cheat!", ""))
    if id != players[2].active_player.name:
        roast: str = choice([
            "It's Omy's turn, not yours!",
            f"It's <@{players[2].active_player.name}>'s turn, not yours!",
            "Stop trying to cheat! Only Omy can.",
            "If you can place card when it's not even your turn, then Omy gonna place a landmine. Actually no, *many* landmines. :3"
        ])
        return await ctx.channel.send(roast)
    m = re.match(".*(\\d+) +(\\d+)", ctx.message.content)
    if m is None:
        return await ctx.channel.send("Omy couldn't find the numbers in your request. Perhaps... Omy is the numbers!")
    i: int = int(m[1])
    j: int = int(m[2])
    if 0 > i >= len(players[2].active_player.hand):
        return await ctx.channel.send("You have no such card in hand. Maybe humans tend to forget list indices usually start with 0. Omy tend to forget that too.")
    card = players[2].active_player.hand[i]
    if type(card) != main.CreatureCard:
        return await ctx.channel.send(f"That's not a creature, that's a {card.name}! You can only place creature (and robots like Omy).")
    placed = players[2].active_player.place(i, j, players[2])
    if not placed:
        await ctx.channel.send("You couldn't place this card here... Perhaps could you place an Omy there?")
    if main.cleanstr(card.name) == "omy" and placed:
        await ctx.channel.send("\nDid ya place Omy?! That's the play of the game!")
    return await showboard(ctx)

@BOT.command()
async def doc(ctx: commands.Context):
    "`omy> doc Card Name` prints a detailed documentation of card with name \"Card Name\""
    tofind: str = main.cleanstr(re.match("omy> doc(.*)", ctx.message.content)[1])
    for card in main.getCARDS():
        if main.cleanstr(card.name) == tofind:
            return await ctx.channel.send(str(card))
    await ctx.channel.send("There's no such card as the one you asked. Try searching for Omy's card instead.")

@BOT.command()
async def endturn(ctx: commands.Context):
    "`omy> endturn` ends your turn, anouncing the winner and reseting the setup if finished. Allow to draw cards and regain energies."
    if len(getPLAYERS()) != 3:
        return await ctx.channel.send("There's no OCG Game ready yet. Join with `omy> join` (and use Omy).")
    if getPLAYERS()[2].active_player.name != str(ctx.author.id):
        roast = choice([
            "That's not your turn yet!",
            "How can you end something you didn't start yet?",
            "Omy doesn't want to end its turn yet."
        ])
        return await ctx.channel.send(roast)
    ret = getPLAYERS()[2].endturn()
    if ret[4] is not None:
        getPLAYERS().clear()
        return await ctx.channel.send(f"The winner is <@{ret[4].name}>! Start a new game using `omy> join` (and don't forget to play Omy).")
    return await showboard(ctx)

@BOT.command()
async def attack(ctx: commands.Context):
    "`omy> attack i's j against {target}` uses the `j`th attack of the card at the `i`th index of your board against `{target}`, if possible. Target can either be `foe#`, `commander`, `allied#` or `allied_commande` with `#` being the board's index of the target, and only influence moves using `target` targeting mode."
    players = getPLAYERS()
    if len(players) != 3:
        return await ctx.channel.send("There's nobody to attack, they must first join with `omy> join`.")
    if str(ctx.author.id) != players[2].active_player.name:
        return await ctx.channel.send("It's not your turn!")
    m = re.match(".*(\\d+)'s +(\\d+) against ((allied|foe)(\\d+)|commander|allied_commander)", ctx.message.content)
    if m is None:
        return await ctx.channel.send("It seems you didn't quite understand the format so Omy gonna teach you. `omy> attack `*active card index*`'s`*attack index*` against `*either `foe`*card index*, `allied`*card index* or `commander`*")
    i: int = int(m[1])
    if (not 0 <= i < len(players[2].active_player.active)) or (players[2].active_player.active[i] is None):
        return await ctx.channel.send("You have no card at this index on your board. " + main.ifelse(random() < 0.5, "Place an Omy there first.", "Place a card there first."))
    card: main.ActiveCard = players[2].active_player.active[i]
    j: int = int(m[2])
    if not 0 <= j < len(card.card.attacks):
        return await ctx.channel.send("This card has no Attack at such index." + main.ifelse(0 <= j < 4, " Omy would have one.", ""))
    attack: main.Attack = card.card.attacks[j]
    target: str = m[3]
    if target == "commander":
        reply = attack_reply(card.attack(attack, players[2].unactive_player.commander), card, attack)
        return await ctx.channel.send(reply)
    if target == "allied_commander":
        reply = attack_reply(card.attack(attack, players[2].active_player.commander), card, attack)
        return await ctx.channel.send(reply)
    target: str = m[4]
    player: main.Player = main.ifelse(target == "foe", players[2].unactive_player, players[2].active_player)
    k: int = int(m[5])
    if (not 0 <= k < len(player.active)) or (player.active[k] is None):
        return await ctx.channel.send("Your opponent has no card at this index on their board.")
    survey: main.EffectSurvey = card.attack(attack, player.active[k])
    reply = attack_reply(survey, card, attack)
    return await ctx.channel.send(reply)
@BOT.command()
async def spelluse(ctx: commands.Context):
    "`omy> spelluse i against {target}` uses the spell at the `i`th index of your hand against `targeet`, if possible. See `omy> help attack` for detail on `{target}`"
    players = getPLAYERS()
    if len(players) != 3:
        return await ctx.channel.send("There's nobody to attack, they must first join with `omy> join`.")
    if str(ctx.author.id) != players[2].active_player.name:
        return await ctx.channel.send("It's not your turn!")
    m = re.match(".*(\\d+) against ((allied|foe)(\\d+)|commander|allied_commander)", ctx.message.content)
    if m is None:
        return await ctx.channel.send("It seems you didn't quite understand the format so Omy gonna teach you. `omy> attack `*active card index*`'s`*attack index*` against `*either `foe`*card index*, `allied`*card index* or `commander`*")
    i: int = int(m[1])
    if (not 0 <= i < len(players[2].active_player.hand)):
        return await ctx.channel.send("You have no card at this index in your hand. " + main.ifelse(random() < 0.5, "Draw an Omy first.", "End your turn to draw more cards."))
    card: main.SpellCard = players[2].active_player.hand[i]
    if type(card) != main.SpellCard: # why isn't Python static typed
        return await ctx.channel.send(f"That's not even a spell, that's a {card.name}.")
    target: str = m[2]
    if target == "commander":
        reply = spell_reply(card.use(players[2].unactive_player.commander, players[2]), card, card.on_use)
        return await ctx.channel.send(reply)
    if target == "allied_commander":
        reply = spell_reply(card.use(players[2].active_player.commander, players[2]), card, card.on_use)
        return await ctx.channel.send(reply)
    target: str = m[3]
    player: main.Player = main.ifelse(target == "foe", players[2].unactive_player, players[2].active_player)
    k: int = int(m[4])
    if (not 0 <= k < len(player.active)) or (player.active[k] is None):
        return await ctx.channel.send("Your opponent has no card at this index on their board.")
    survey: main.EffectSurvey = card.use(player.active[k], players[2])
    reply = spell_reply(survey, card, card.on_use)
    return await ctx.channel.send(reply)
def attack_reply(survey: main.EffectSurvey, user: main.ActiveCard, attack: main.Attack) -> str:
    reply = f"{user.card.name}'s {attack.name} returned with code {survey.return_code}: {survey.return_code.name}, dealt {survey.damage} damages and healed for {survey.heal} HP!"
    if survey.damage < 70 and main.cleanstr(user.card.name) != "omy" and random() < 0.5:
        reply += "\nOmy would have dealt more."
    if main.cleanstr(user.card.name) == "omy":
        reply += "\nOmy finally gets to play!"
    if survey.damage > 100 and random() < 0.5:
        reply += "\nThat's a lot of damage!"
    return reply
def spell_reply(survey: main.EffectSurvey, card: main.SpellCard, attack: main.Attack):
    return f"Spell {card.name} returned with code {survey.return_code}: {survey.return_code.name}, dealt {survey.damage} damages and heald for {survey.heal} HP!"
