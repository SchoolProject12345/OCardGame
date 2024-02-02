import Core.core_main as core

class ReplayHandler:
    state: dict[str, any]
    replay: list[str]
    def __init__(self):
        self.state = ReplayHandler.default_state()
        self.replay = []
    def get_state(self):
        return self.state
    def get_replay(self):
        replay = ""
        for log in self.replay:
            replay += log + "\n"
        return replay.strip()
    def save_replay_as(self, name: str):
        if "Replay" not in core.os.listdir():
            core.os.mkdir(core.os.path.join(core.Constants.cwd_path, "Replay"))
        with open(core.os.path.join(core.Constants.cwd_path, "Replay", name), "w") as io:
            io.write(self.get_replay())
            io.close()
        return self
    def default_state():
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
         "arena":0
        }
    def play_log(self, log: str) -> str:
        """
        Play a log updating `self.state` and returning a string to be or not logged to the terminal for text-based.
        Note: `log` is considered to be a correctly formed log, if not there is no guarantee that it will return without crash/bug.
        """
        self.replay.append(log)
        head, *args = log.split('|')
        match head:
            case "player":
                ind = args[0]
                self.state[ind]["name"] = args[1]
                commander = get_commander(args[2])
                self.state[ind]["commander"]["name"] = commander.name
                self.state[ind]["commander"]["hp"] = self.state[ind]["commander"]["max_hp"] = commander.max_hp
                self.state[ind]["commander"]["element"] = commander.element.value
                return ""
            case "discard":
                # No error handling AT ALL
                if args[1] in self.state[args[0]]["hand"]:
                    self.state[args[0]]["hand"].remove(args[1])
                else:
                    # If cards are hidden (e.g. opponnent's)
                    self.state[args[0]]["hand"].pop()
                self.state[args[0]]["discard"].append(args[1])
                name = self.state[args[0]]["name"]
                return f"{name} discarded {args[1]} of their hand."
            case "draw":
                self.state[args[0]]["hand"].append(args[1])
                self.state[args[0]]["deck_length"] -= 1
                name = self.state[args[0]]["name"]
                return f"{name} drew a {args[1]}."
            case "chat":
                if not core.DEV():
                    print(
                        "\033[1m" + stringclr(args[0]) + args[0] + "\033[0m:" + args[1]
                    )
            case "defeat":
                player, i = player_index(args[0])
                self.state[player]["discard"].append(defeated := self.state[player]["board"][i]["name"])
                self.state[player]["board"][i] = None
                return f"{defeated} has been defeated."
            case "spell":
                # Spell discard is treated independently so that it's easier.
                # Actually using a spell launch an attack, so that's kinda pointless
                # Just ignore this.
                player, i = player_index(args[1])
                target = self.state[player]["board"][i]["name"]
                return f"{args[0]} has been launched on {core.TargetMode(args[2]).name}, specifically {target}."
            case "attack":
                owner, i = player_index(args[0])
                user = self.state[owner]["board"][i]["name"]
                oppon, j = player_index(args[2])
                target = self.state[oppon]["board"][j]["name"]
                if args[3] < 299:
                    return f"{user} sucessfully used {args[1]} against {target}."
                return f"{user}'s {args[1]} failed."
            case "-damage":
                raw_hp, max_hp = args[1].split("/")
                # No handling at all
                raw_hp = int(raw_hp)
                max_hp = int(max_hp)
                player, i = player_index(args[0])
                pre_hp = self.state[player]["board"][i]["hp"]
                target = self.state[player]["board"][i]
                target["hp"] = raw_hp
                target["max_hp"] = max_hp
                return f"{target['name']} took {pre_hp - raw_hp} damages."
            case "-heal":
                raw_hp, max_hp = args[1].split("/")
                # No handling at all
                raw_hp = int(raw_hp)
                max_hp = int(max_hp)
                player, i = player_index(args[0])
                pre_hp = self.state[player]["board"][i]["hp"]
                target = self.state[player]["board"][i]
                target["hp"] = raw_hp
                target["max_hp"] = max_hp
                return f"{target['name']} healed {pre_hp - raw_hp} damages."


def player_index(index: str):
    "Parse an index in the form pix with i int and x letter (e.g. p1a)."
    return (index[0:2], ord(index[2])-97)

def stringclr(string: str):
    "Used for username color in chat."
    t = sum([ord(c) for c in string])
    # All 0x1000000 RGB values should be possible as (1, 2, 7, 255) are co-primes,
    # But I'm not 100% sure.
    # And I should've mod 256 but whatever.
    r = t % 255
    g = 2*t % 255
    b = 7*t % 255
    return f"\033[38;2;{r};{g};{b}m"                

def get_commander(name: str) -> core.CommanderCard:
    "Return correct commander or UNKNOWN if not implemented in current save."
    if name in core.getCOMMANDERS():
        return core.getCOMMANDERS()[name]
    return core.CommanderCard("UNKNOWN", 1j, core.Element.elementless, 600, [], [], 0, ("any", "unknown"))

def devlog(*msg, dev: bool = core.DEV()):
    dev and print(*msg)
    return True
