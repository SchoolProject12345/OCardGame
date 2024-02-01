import Core.core_main as core

@core.dataclass
class ReplayHandler:
    state: dict
    replay: list
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

def devlog(*msg, dev: bool = core.DEV()):
    dev and print(*msg)
    return True