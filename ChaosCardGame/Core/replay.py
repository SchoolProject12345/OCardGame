import Core.core_main as core
from datetime import datetime # ???
from utility import static
from time import sleep

class ReplayHandler:
    "A game state handler which as everything necessary for replaying a game, i.e. a log player and a data retriever."
    state: dict[str, any]
    replay: list[str]
    ongoing: bool
    def __init__(self):
        self.state = ReplayHandler.default_state()
        self.replay = []
        self.ongoing = True
    def isp1(self) -> bool: return self.state["pov"] == "p1" # POV can be used to change replay POV
    def get_state(self) -> dict:
        """
        Return `self`'s state as a dict (see `./Core/log.doc.md`).\n
        This is different from `self.state`, whcih returns raw data,
        `self.get_state()` first format the state to be easier to process by the UI.\n
        /!\\ DO NOT MUTATE: this might have repercussion on the actual game state,
        even after a shallow copy.
        """
        state = {
         "remote":core.ifelse(self.isp1(), self.state["p2"], self.state["p1"]).copy(),
         "local":core.ifelse(self.isp1(), self.state["p1"], self.state["p2"]).copy(),
         "turn":self.state["turn"],
         "isactive":not (self.isp1() ^ (self.state["activep"] == "p1")),
         "arena":self.state["arena"].value
        }
        state["remote"]["commander"] = format_active_ui(state["remote"]["commander"])
        state["local"]["commander"] = format_active_ui(state["local"]["commander"])
        state["remote"]["board"] = [format_active_ui(card) for card in state["remote"]["board"]] 
        state[ "local"]["board"] = [format_active_ui(card) for card in state[ "local"]["board"]]
        state["remote"]["hand"]  = [format_name_ui_elt(card) for card in state["remote"]["hand"]]
        state[ "local"]["hand"]  = [format_name_ui_elt(card) for card in state[ "local"]["hand"]]
        state["remote"]["discard"] = [format_name_ui_elt(card) for card in state["remote"]["discard"]]
        state[ "local"]["discard"] = [format_name_ui_elt(card) for card in state[ "local"]["discard"]]
        return state
    @static
    def get_required_charges(commander: str) -> int:
        commander: str = core.cleanstr(commander)
        if commander not in core.getCOMMANDERS():
            core.warn(f"Tried to fetch unknown commander: {commander}.")
            return 250
        commander: core.CommanderCard = core.getCOMMANDERS()[commander]
        if len(commander.attacks) > 1:
            return commander.attacks[1].cost
        return 65535
    def showboard(self):
        # `self.state` is faster than `self.get_state()` and contains more informations as less formatted
        data = self.state
        local, remote = core.ifelse(self.isp1(), ("p1", "p2"), ("p2", "p1"))

        print(f"Turn {data['turn']} ", end="")
        server = data[remote]
        if data["activep"] == remote:
            print(f"({server['name']}'s turn)")
        else:
            print("(Your turn)")

        print(f"\n\033[1;4m{server['name']}'s Side\033[0m")
        print(f"Energy: \033[1m{server['energy']}\033[22m/\033[1m{server['max_energy']}\033[22m (\033[1m+{server['energy_per_turn']}/turn\033[22m)")
        print(progressbar(
            server["commander"]["charges"],
            ReplayHandler.get_required_charges(server["commander"]["name"]),
            style = core.Constants.progressbar_style
        ))
        print("\033[4m" + ansi_card(server["commander"], '⋆'))
        for card in server["board"]:
            print(ansi_card(card), end=" ")

        client = data[local]
        print(f"\n\n\033[1;4m{client['name']}'s Side\033[0m")
        print(f"Energy: \033[1m{client['energy']}\033[22m/\033[1m{client['max_energy']}\033[22m (\033[1m+{client['energy_per_turn']}/turn\033[22m)")
        print(progressbar(
            client["commander"]["charges"],
            ReplayHandler.get_required_charges(client["commander"]["name"]),
            style = core.Constants.progressbar_style
        ))
        print("\033[4m" + ansi_card(client["commander"], '⋆'))
        for card in client["board"]:
            print(ansi_card(card), end=" ")
        print()
        print("Your hand: ", end="")
        for card in client["hand"]:
            print(card.replace(",", " -"), end=", ")
        if len(client["hand"]) == 0:
            print("∅  ", end="")
        print("\033[2D ")

        return self
    def get_replay(self):
        replay = ""
        for log in self.replay:
            replay += log + "\n"
        return replay.strip()
    def read_replay(self, name: str, delay: float = 0.0):
        """
        Try to read replay contained at `./Replays/{name}`,
        mutating `self`'s game state and printing logs to the terminal if in DEV()-mode.
        If `delay` is specified, wait `delay` seconds between each log.
        """
        with open(core.os.path.join(core.Constants.path, "Replays", name), "r", encoding="utf-8") as io:
            try:
                logs = io.read()
            except:
                core.warn(f"An error occured while trying to load {name}.")
                io.close()
                return self
            io.close()
        logs = logs.split("\n")
        for log in logs:
            try:
                devlog(self.play_log(log))
            except:
                devlog("Error with:", log)
            sleep(delay)
        return self
    def save_replay(self):
        """
        Generate a unique (unless you actively try with a stupid stuborness to break the code) name to
        save current replay as a `.log` in the `./Replays/` folder without conflicts.
        """
        name = (core.cleanstr(self.state["p1"]["name"]) +
                "-vs-" +
                core.cleanstr(self.state["p2"]["name"]) +
                str(datetime.now()) + # datetime avoids duplicates.
                ".log")
        return self.save_replay_as(name)
    def save_replay_as(self, name: str):
        "Save current replay in the `./Replays/` folder. Name should end in `.log`."
        if "Replays" not in core.os.listdir():
            core.os.mkdir(core.os.path.join(core.Constants.path, "Replays"))
        with open(core.os.path.join(core.Constants.path, "Replays", name), "x", encoding="utf-8") as io:
            try:
                io.write(self.get_replay())
            finally:
                io.close()
        return self
    def default_state() -> dict:
        return {
         "p1":{
          "name":"",
          "deck_length":core.Constants.default_deck_size,
          "hand":[],
          "commander":{"name":"","hp":600,"max_hp":600,"element":0,"charges":0},
          "board":[],
          "discard":[],
          "energy":core.Constants.default_energy_per_turn,
          "max_energy":core.Constants.default_max_energy,
          "energy_per_turn":core.Constants.default_energy_per_turn
         },
         "p2":{
          "name":"",
          "deck_length":core.Constants.default_deck_size,
          "hand":[],
          "commander":{"name":"","hp":600,"max_hp":600,"element":0,"charges":0},
          "board":[],
          "discard":[],
          "energy":core.Constants.default_energy_per_turn,
          "max_energy":core.Constants.default_max_energy,
          "energy_per_turn":core.Constants.default_energy_per_turn
         },
         "turn":0,
         "activep":"p1",
         "arena":core.Arena.själløssmängd,
         "pov":"p1" # used for replays.
        }
    def get_target(self, index: str):
        "Return the active dict corresponding to the pix index, supporting commander's @ indices."
        if index[2] == '@':
            return self.state[index[0:2]]["commander"]
        player, i = player_index(index)
        return self.state[player]["board"][i]
    @static
    def play_log(self, log: str) -> str:
        """
        Play a log updating `self.state` and returning a string to be or not logged to the terminal for text-based.
        Note: `log` is considered to be a correctly formed log, if not there is no guarantee that it will return without crash/bug.
        """
        log = log.strip() # might always be useful
        head, *args, kwargs = kwargssplit(log)
        match head:
            case "player":
                ind = args[0]
                self.state[ind]["name"] = args[1]
                self.state[ind]["commander"]["name"] = args[2]
                self.state[ind]["commander"]["hp"] = self.state[ind]["commander"]["max_hp"] = int(args[3])
                self.state[ind]["commander"]["element"] = int(args[4])
                ret = f"Contestant {args[1]} commands through {args[2]}."
            case "boardsize":
                psize = len(self.state[args[0]]["board"])
                delta = int(args[1]) - psize
                l = delta
                if l < 0:
                    while l < 0:
                        self.state[args[0]].remove(None) # no error handling
                        l += 1
                else:
                    self.state[args[0]]["board"] += [None]*l
                if psize == 0:
                    ret = ""
                else:
                    ret = f"{self.state[args[0]]['name']} "
                    if delta > 0:
                        ret += f"gained {delta} slots on their board."
                    else:
                        ret += f"lost {-delta} slots on their board."
            case "discard":
                # No error handling AT ALL
                if args[1] in self.state[args[0]]["hand"]:
                    self.state[args[0]]["hand"].remove(args[1])
                else:
                    # If cards are hidden (e.g. opponnent's)
                    self.state[args[0]]["hand"].pop()
                self.state[args[0]]["discard"].append(args[1])
                name = self.state[args[0]]["name"]
                ret = f"{name} discarded {args[1]} of their hand."
            case "place":
                # commanders can't be placed so this is safe
                player, i = player_index(args[0])
                self.state[player]["board"][i] = {
                    "name":args[1],
                    "hp":int(args[2]),
                    "max_hp":int(args[2]),
                    "element":int(args[3])
                }
                if args[1] in self.state[player]["hand"]:
                    self.state[player]["hand"].remove(args[1])
                else:
                    self.state[player]["hand"].pop()
                ret = f"{self.state[player]['name']} placed a {args[1]} at the {core.nth(i)} position."
            case "-summon":
                # same as place
                player, i = player_index(args[0])
                self.state[player]["board"][i] = {
                    "name":args[1],
                    "hp":int(args[2]),
                    "max_hp":int(args[2]),
                    "element":int(args[3])
                }
                ret = f"A {args[1]} appeared at the {core.nth(i)} position of {self.state[player]['name']}'s board."
            case "draw":
                self.state[args[0]]["hand"].append(args[1])
                self.state[args[0]]["deck_length"] -= 1
                name = self.state[args[0]]["name"]
                return f"{name} drew a {args[1]}."
            case "chat":
                msg = "\033[1m" + stringclr(args[0]) + args[0] + "\033[0m: " + args[1]
                if not core.DEV():
                    print(msg)
                ret = msg
            case "defeat":
                # commanders can't be defeated (that would result in a `win|pi|Name` log)
                player, i = player_index(args[0])
                self.state[player]["discard"].append(defeated := self.state[player]["board"][i]["name"])
                self.state[player]["board"][i] = None
                ret = f"{defeated} has been defeated."
            case "spell":
                target = self.get_target(args[1])["name"]
                if int(args[3]) < 299:
                    ret = f"{args[0]} has been launched on {core.TargetMode(int(args[2])).name}, specifically {target}."
                else:
                    ret = f"{args[0]} failed ({args[3]})"
            case "attack":
                user = self.get_target(args[0])["name"]
                target = self.get_target(args[2])["name"]
                if int(args[4]) < 299:
                    ret = f"{user} sucessfully used {args[1]} against {target}."
                else:
                    ret = f"{user}'s {args[1]} failed ({args[4]})."
            case "-damage":
                raw_hp, max_hp = args[1].split('/')
                # No error handling at all
                raw_hp = int(raw_hp)
                max_hp = int(max_hp)
                target = self.get_target(args[0])
                pre_hp = target["hp"]
                target["hp"] = raw_hp
                target["max_hp"] = max_hp
                ret = f"{target['name']} took {pre_hp - raw_hp} damages."
            case "-heal":
                raw_hp, max_hp = args[1].split('/')
                # No error handling at all
                raw_hp = int(raw_hp)
                max_hp = int(max_hp)
                target = self.get_target(args[0])
                pre_hp = target["hp"]
                target["hp"] = raw_hp
                target["max_hp"] = max_hp
                ret = f"{target['name']} healed {raw_hp - pre_hp} damages."
            case "passive":
                user = self.get_target(args[0])["name"]
                ret = f"{user}'s {args[1]} activated."
            case "-formechange":
                # Please don't change the commander's forme though
                target = self.get_target(args[0])
                pre_name = target["name"]
                target["name"] = args[1]
                raw_hp, max_hp = args[2].split('/')
                raw_hp = int(raw_hp)
                max_hp = int(max_hp)
                target["hp"] = raw_hp
                target["max_hp"] = max_hp
                target["element"] = args[3]
                ret = f"{pre_name} changed to {args[1]}."
                # -element not yet supported as useless.
            case "-hypno":
                # commanders can't be hypnotized, so this is safe
                owner, i = player_index(args[0])
                oppon, j = player_index(args[1])
                self.state[oppon]["board"][j] = self.state[owner]["board"][i]
                self.state[owner]["board"][i] = None
                ret = f"{self.state[oppon]['board'][j]['name']} changed of side."
            case "win":
                self.ongoing = False
                ret = f"{args[1]} won the game!"
            case "raw":
                ret = args[0]
            case "error":
                return "\033[1;31m┌ Error:\n└\033[0m " + "".join(args)
            case "energy":
                player = self.state[args[0]]
                energy, max_energy = args[1].split('/')
                prev_energy = player["energy"]
                energy = int(energy)
                max_energy = int(max_energy)
                player["energy"] = energy
                player["max_energy"] = max_energy
                player["energy_per_turn"] = int(args[2])
                ret = f"{player['name']} gained {energy-prev_energy}/{max_energy} energy."
            case "turn":
                self.state["turn"] = int(args[0])
                if self.state["activep"] == "p1":
                    self.state["activep"] = "p2"
                else:
                    self.state["activep"] = "p1"
                ret = f"{self.state[self.state['activep']]['name']}'s turn started."
            case "-ccharge":
                player = self.state[args[0]]
                pcharges = player["commander"]["charges"]
                player["commander"]["charges"] = int(args[1])
                ret = f"{player['name']} charged {player['commander']['charges'] - pcharges} damages into their commander."
            case "shuffle":
                player = self.state[args[0]]
                player["deck_length"] = len(player["discard"])
                player["discard"].clear()
                ret = f"{player['name']} shuffled their discard pile into their deck."
            case "-firstp":
                self.state["activep"] = args[0]
                if (self.state["activep"] == "p1" and self.isp1()) or (self.state["activep"] == "p2" and not self.isp1()):
                    ret = "It's your turn."
                else:
                    ret = "It's " + self.state[self.state["activep"]]["name"] + "'s turn."
            case "arena":
                arena = core.Arena(int(args[0]))
                self.state["arena"] = arena
                ret = f"The battle take place in the Mighty Arena of {arena.name}"
            case "": # allows to put empty lines in `.log`'s for clarity/time spacing.
                ret = ""
        # isn't appended if an error is thrown, so that the replay is always valid.
        self.replay.append(log)
        return ret

@static
def format_name_ui_elt(name: str) -> str:
    "Same as `core.format_name_ui` but infer element."
    card = core.AbstractCard.get_card(name)
    if card is None:
        return core.format_name_ui(name)
    return card.ui_id

@static
def format_active_ui(active: dict[str, object] | None) -> dict[str, object] | None:
    if active is None:
        return
    active = active.copy()
    active["name"] = core.format_name_ui(active["name"], active["element"])
    return active

def player_index(index: str):
    "Parse an index in the form pix with i int and x letter (e.g. p1a). Doesn't parse commander (i.e. pi@) indices."
    return (index[0:2], ord(index[2])-97)

def stringclr(string: str):
    "Used for username color in chat."
    t = sum([ord(c) for c in string])
    # All 0x1000000 RGB values should be possible as (1, 2, 7, 255) are co-primes,
    # But I'm not 100% sure.
    # And I should've mod 256 but whatever.
    # A few days later, I'm 100% sure this doesn't work,
    # But I won't change, cuz "Ånyks" has a great color.
    r = t % 255
    g = 2*t % 255
    b = 7*t % 255
    return f"\033[38;2;{r};{g};{b}m"

@static
def gradient(x: int | float):
    x = 5.0*x
    r = int(255 * (core.clamp(2.0 - x, 0.0, 1.0) + core.clamp(x - 4.0, 0.0, 1.0)))
    g = int(255 * (core.clamp(x, 0.0, 1.0) - core.clamp(x - 3.0, 0.0, 1.0)))
    b = int(255 * core.clamp(x - 2.0, 0.0, 1.0))
    return f"\033[38;2;{r};{g};{b}m"

@static
def progressbar(total: int, on: int, size: int = 15, style: int = 0):
    if style == 3:
        complete = size * total // on # can exceed 15
        stack = complete // size # number of times it exceeds 15
        complete = complete % (size + 1)
        bar = "["
        bar += gradient(min((stack + 1) * 0.2, 1.0)) + "=" * (complete) # max 5 stacks
        if complete < size:
            bar += ">" + gradient(min(stack * 0.2, 1.0)) + core.ifelse(stack == 0, ' ', '=') * (14 - complete)
        return bar + "\033[0m]"
    total = min(total, on)
    if total == on:
        if style == 0:
            return "[" + gradient(1.0) + "=" * size + "\033[0m]"
        elif style == 1:
            bar = "["
            for i in range(size):
                bar += gradient(i/size) + "="
            return bar + "\033[0m]"
        elif style == 2:
            return "[" + "="*size + "]"
    complete = total * size // on
    bar = "["
    if style != 2:
        bar += gradient(total/on)
    bar += "="*complete + ">" + " "*(size - complete - 1)
    if style != 2:
        bar += "\033[0m"
    return bar + "]"

@static
def ansi_elementcolor(element: core.Element) -> str:
    match element:
        case core.Element.water: return "\033[38;2;0;122;247m"
        case core.Element.fire: return "\033[38;2;205;94;1m"
        case core.Element.earth: return "\033[38;2;32;153;13m"
        case core.Element.air: return "\033[38;2;223;1;209m"
        case _: return "\033[38;2;91;1;215m"
@static
def ansi_card(card: dict[str, object] | None, trailing: str = "") -> str:
    if card is None:
        return "____"
    return ansi_elementcolor(core.Element(card["element"])) + card["name"] + trailing + f"\033[0m ({card['hp']}/{card['max_hp']})"

def get_commander(name: str) -> core.CommanderCard:
    "Return correct commander or UNKNOWN if not implemented in current save."
    name = core.cleanstr(name)
    if name in core.getCOMMANDERS():
        return core.getCOMMANDERS()[name]
    return core.CommanderCard("UNKNOWN", 1j, core.Element.elementless, 600, [], [], 0, ("any", "unknown"))

def devlog(*msg, dev: bool = core.DEV()):
    dev and print(*msg)
    return True

def kwargssplit(log: str) -> list[str | dict[str, str]]:
    logs = log.split('|')
    rexpr: str = "\\[(.*?)\\] +(.*)"
    i: int = len(logs)
    for j in range(len(logs)):
        if core.re.match(rexpr, logs[j]):
            i = j
            break
    args: list[str] = logs[0:i]
    kwargs: dict[str, str] = {}
    for j in logs[i:]:
        m = core.re.match(rexpr, j)
        kwargs[m[1]] = m[2]
    args.append(kwargs)
    return args
