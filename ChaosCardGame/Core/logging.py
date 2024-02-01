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
          "deck_length":core.Constants.default_deck_size - core.Constants.default_hand_size,
          "hand":core.Constants.default_hand_size,
          "commander":{"name":"","hp":600,"max_hp":600,"element":0,"charges":0},
          "board":[],
          "discard":[],
          "energy":core.Constants.default_energy_per_turn,
          "max_energy":core.Constants.default_max_energy,
          "energy_per_turn":core.Constants.default_energy_per_turn
         },
         "p2":{
          "name":"",
          "deck_length":core.Constants.default_deck_size - core.Constants.default_hand_size,
          "hand":core.Constants.default_hand_size,
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
                pass
            case "draw":
                pass

def get_commander(name: str) -> core.CommanderCard:
    "Return correct commander or UNKNOWN if not implemented in current save."
    if name in core.getCOMMANDERS():
        return core.getCOMMANDERS()[name]
    return core.CommanderCard("UNKNOWN", 1j, core.Element.elementless, 600, [], [], 0, ("any", "unknown"))


def devlog(*msg, dev: bool = core.DEV()):
    dev and print(*msg)
    return True
