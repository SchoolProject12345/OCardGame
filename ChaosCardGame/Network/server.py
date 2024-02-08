import Network.network as net
from time import time_ns
from Core.replay import * # includes core
import re
core.os.system("") # Python somehow requires that to enable ANSI on most terminal.

core.Constants.clientside_actions = ["help", "doc", "dochand", "showboard"]
core.Constants.anytime_actions = ["chat", "forfeit", "sync"] # can be used even if not their turn.
core.Constants.serverside_actions = ["attack", "spell", "place", "discard", "endturn"] + core.Constants.anytime_actions
core.Constants.progressbar_sytle = 1

def gradient(x: float):
    x = 5.0*x
    r = int(255 * (core.clamp(2.0 - x, 0.0, 1.0) + core.clamp(x - 4.0, 0.0, 1.0)))
    g = int(255 * (core.clamp(x, 0.0, 1.0) - core.clamp(x - 3.0, 0.0, 1.0)))
    b = int(255 * core.clamp(x - 2.0, 0.0, 1.0))
    return f"\033[38;2;{r};{g};{b}m"
def progressbar(total: int, on: int, size: int = 15, style = 0):
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

def ansi_elementcolor(element: core.Element) -> str:
    match element:
        case core.Element.water: return "\033[38;2;0;122;247m"
        case core.Element.fire: return "\033[38;2;205;94;1m"
        case core.Element.earth: return "\033[38;2;32;153;13m"
        case core.Element.air: return "\033[38;2;223;1;209m"
        case _: return ""
def ansi_card(card: dict | None, trailing="") -> str:
    if card is None:
        return "____"
    return ansi_elementcolor(core.Element(card["element"])) + card["name"] + trailing + f"\033[0m ({card['hp']}/{card['max_hp']})"

@core.dataclass
class ServerHandler(ReplayHandler):
    board: core.Board
    client_socket: net.socket.socket
    def __init__(self, board: core.Board, client_socket: net.socket.socket):
        ReplayHandler.__init__(self)
        self.board = board
        self.client_socket = client_socket
        del self.state["pov"]
    def __call__(self, data: str) -> bool: # __call__ allows to quack like a function.
        if not self.ongoing:
            return False
        if data == "":
            self.ongoing = False
            return False
        if '\n' in data:
            return core.np.all([self(_data) for _data in data.split('\n')])
        datas: list[str] = data.split('|')
        head = core.cleanstr(datas[0])
        if head == "sync":
            self.sync()
            return True
        if  self.board.active_player is not self.board.player2 and head not in core.Constants.anytime_actions:
            self.client_socket.send(b"error|Wrong turn.")
            return True
        if head in core.Constants.serverside_actions:
            self.ongoing = run_action(self.board, self.client_socket, head, *datas[1:], source=True)
            self.log_sync()
            return self.ongoing
        self.client_socket.send(b"error|Unrecognized action.")
        return True
    def isp1(self): return True
    def run_action(self, action: str) -> bool:
        args = action.split('|')
        head = args[0]
        if head in core.Constants.clientside_actions:
            clientside_action(self, *args)
            return True
        if self.board.active_player is not self.board.player1 and head not in core.Constants.anytime_actions:
            core.warn("Wrong turn.")
            return False
        if head not in core.Constants.serverside_actions:
            devlog("Invalid action. Write `help` to get a list of valid actions.")
            return False
        ongoing = run_action(self.board, self.client_socket, *args, source=False)
        self.log_sync()
        return ongoing
    def log_sync(self):
        "Read `self.board`'s logs and send them to the client."
        logs = ""
        while len(self.board.logs) != 0: # explicit is better than implicit
            log = self.board.logs.pop(0).strip()
            try:
                devlog(self.play_log(log)) # TODO: don't log to the terminal when remote draw a card.
            except:
                print(log)
            logs += log + "\n"
        logs = logs.strip()
        if len(logs) != 0:
            self.client_socket.send(logs.encode()) # logs are split by line uppon reception.
    def showboard(self):
        board = self.board
        print(f"Turn {board.turn} ", end="")
        player1 = self.board.player1
        if board.active_player is player1:
            print(f"(Your turn)")
        else:
            print(f"({board.active_player.name}'s turn)")
        player2 = board.player2
        print(f"\n\n\033[1;4m{player2.name}'s Side\033[0m")
        print(f"Energy: \033[1m{player2.energy}\033[22m/\033[1m{player2.max_energy}\033[22m (\033[1m+{player2.energy_per_turn}/turn\033[22m)")
        if len(player2.commander.card.attacks) > 1:
            print(progressbar(player2.commander_charges, player2.commander.card.attacks[1].cost, style=core.Constants.progressbar_sytle))
        print("\033[4m" + ansi_card({
            "name":player2.commander.card.name,
            "hp":player2.commander.hp,
            "max_hp":player2.commander.card.max_hp,
            "element":player2.commander.element.value
        }, '⋆'))
        for card in player2.active:
            if card is None:
                print("____ ", end="")
                continue
            print(ansi_card({
                "name":card.card.name,
                "hp":card.hp,
                "max_hp":card.card.max_hp,
                "element":card.element.value
            }), end=" ")

        print(f"\n\n\033[1;4m{player1.name}'s Side\033[0m")
        print(f"Energy: \033[1m{player1.energy}\033[22m/\033[1m{player1.max_energy}\033[22m (\033[1m+{player1.energy_per_turn}/turn\033[22m)")
        if len(player1.commander.card.attacks) > 1:
            print(progressbar(player1.commander_charges, player1.commander.card.attacks[1].cost, style=core.Constants.progressbar_sytle))
        print("\033[4m" + ansi_card({
            "name":player1.commander.card.name,
            "hp":player1.commander.hp,
            "max_hp":player1.commander.card.max_hp,
            "element":player1.commander.element
        }, '⋆'))
        for card in player1.active:
            if card is None:
                print("____ ", end="")
                continue
            print(ansi_card({
                "name":card.card.name,
                "hp":card.hp,
                "max_hp":card.card.max_hp,
                "element":card.element
            }), end=" ")
        print()
        print("Your hand: ", end="")
        for card in player1.hand:
            print(card.name.replace(",", " -"), end=", ")
        if len(player1.hand) == 0:
            print("∅  ", end="")
        print("\033[2D ")

        return self # to chain
    def sync(self):
        "Update `network.get_data()` to prepare to send"
        data = net.get_data()

        player = self.board.player1
        server = data["server"]
        # name is constant, no need to update
        server["deck_length"] = len(player.deck)
        server["hand"] = len(player.hand)

        server["commander"]["hp"] = player.commander.hp
        server["commander"]["max_hp"] = player.commander.card.max_hp
        server["commander"]["element"] = player.commander.element.value
        server["commander"]["charges"] = player.commander_charges

        server["board"] = player.get_actives_json()
        server["discard"] = [card.name for card in player.discard]
        server["energy"] = player.energy
        server["max_energy"] = player.max_energy
        server["energy_per_turn"] = player.energy_per_turn

        data["turn"] = self.board.turn
        data["server_turn"] = self.board.active_player is player
        data["arena"] = self.board.arena.value

        player = self.board.player2
        client = data["client"]
        # name is constant, no need to update
        client["deck_length"] = len(player.deck)
        client["hand"] = [card.name for card in player.hand]

        client["commander"]["hp"] = player.commander.hp
        client["commander"]["max_hp"] = player.commander.card.max_hp
        client["commander"]["element"] = player.commander.element.value
        client["commander"]["charges"] = player.commander_charges

        client["board"] = player.get_actives_json()
        client["discard"] = [card.name for card in player.discard]
        client["energy"] = player.energy
        client["max_energy"] = player.max_energy
        client["energy_per_turn"] = player.energy_per_turn

        self.client_socket.send(("sync|" + net.json.dumps(data, separators=(',', ':'))).encode())
        return self

@core.dataclass
class ClientHandler(ReplayHandler):
    server_socket: net.socket.socket
    waiting: bool = False
    synced: bool = False
    def __init__(self, server_socket: net.socket.socket, waiting: bool = False, synced: bool = False):
        ReplayHandler.__init__(self)
        self.server_socket = server_socket
        self.synced = synced
        self.waiting = False
        del self.state["pov"]
    def __call__(self, data: str) -> bool:
        self.waiting = False
        if data == "":
            self.ongoing = False
            return False
        if '\n' in data:
            return core.np.all([self(_data) for _data in data.split('\n')])
        datas: list[str] = data.split('|')
        head = core.cleanstr(datas[0])
        if head == "sync":
            net.get_data().update(net.json.loads(datas[1]))
            self.synced = True
            return True
        try:
            devlog(self.play_log(data))
        except:
            print("Error with:", data)
        return True
    def isp1(self): return False
    def sendblock(self, *args, max_wait: int = 100_000_000):
        self.waiting = True
        start = time_ns()
        self.server_socket.send(*args)
        while self.waiting:
            if time_ns() - start > max_wait:
                core.warn(f"Response undetected after {max_wait/1_000_000_000:.4}s. Continuing thread anyway.")
                return self
        return self
    def send(self, *args):
        self.server_socket.send(*args)
        return self
    def run_action(self, action: str):
        "Request server to run action, returning `True` if sucessfully sent and `False` if clientside check failed."
        args = action.split('|')
        head = args[0]
        if head in core.Constants.clientside_actions:
            clientside_action(self, *args)
            return True
        if head not in core.Constants.serverside_actions:
            devlog("Invalid action. Write `help` to get a list of valid actions.")
            return False
        if net.get_data()["server_turn"] and head not in core.Constants.anytime_actions:
            core.warn("Wrong turn.")
            return False
        if head == "chat":
            if len(args) < 2:
                devlog("Missing message in `chat` request.")
                return False
            action = f"chat|{self.get_state()['local']['name']}|{args[1]}"
        self.sendblock(action.encode(), max_wait=300_000_000).sync()
        return True
    def get_required_charges(commander: str):
        commander: str = core.cleanstr(commander)
        if commander not in core.getCOMMANDERS():
            return 250
        commander: core.CommanderCard = core.getCOMMANDERS()[commander]
        if len(commander.attacks) > 1:
            return commander.attacks[1].cost
        return 65535
    def showboard(self):
        data: dict = net.get_data()

        print(f"Turn {data['turn']} ", end="")
        server = data["server"]
        if data["server_turn"]:
            print(f"({server['name']}'s turn)")
        else:
            print("(Your turn)")

        print(f"\n\033[1;4m{server['name']}'s Side\033[0m")
        print(f"Energy: \033[1m{server['energy']}\033[22m/\033[1m{server['max_energy']}\033[22m (\033[1m+{server['energy_per_turn']}/turn\033[22m)")
        print(progressbar(
            server["commander"]["charges"],
            ClientHandler.get_required_charges(server["commander"]["name"]),
            style = core.Constants.progressbar_sytle
        ))
        print("\033[4m" + ansi_card(server["commander"], '⋆'))
        for card in server["board"]:
            print(ansi_card(card), end=" ")

        client = data["client"]
        print(f"\n\n\033[1;4m{client['name']}'s Side\033[0m")
        print(f"Energy: \033[1m{client['energy']}\033[22m/\033[1m{client['max_energy']}\033[22m (\033[1m+{client['energy_per_turn']}/turn\033[22m)")
        print(progressbar(
            client["commander"]["charges"],
            ClientHandler.get_required_charges(client["commander"]["name"]),
            style = core.Constants.progressbar_sytle
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
    def sync(self, wait: bool = True, max_wait: int = 100_000_000):
        "Ask `self`'s sever for a synchronization, waiting its sucess for up to `max_wait` nanoseconds if `wait` is set to `True`."
        start = time_ns()
        self.synced = False
        self.server_socket.send(b"sync")
        # result is automatically obtained through listen(server_socket, self) running on separate thread
        while wait and not self.synced: # wait until update is done, ugly but it works ¯\_(ツ)_/¯
            if time_ns() - start > max_wait:
                core.warn(f"Synchronization undetected after {max_wait/1_000_000_000:.4}s. Continuing thread anyway.")
                self.sync(False)
                return self
        return self

def sendblock(socket: net.socket.socket, *args):
    "Send and block until receiving 'ok' or any two-byte message."
    size = socket.send(*args)
    socket.recv(2)
    return size
def recvok(socket: net.socket.socket, *args):
    "Send 'ok' after receiving to release `sendblock`."
    data = socket.recv(*args)
    socket.send(b"ok")
    return data
def sendrecv(socket: net.socket.socket, size: int, *args):
    "Send `*args` to `socket` then wait until a message with up to `size` size is received, returning it as `bytes`."
    socket.send(*args)
    return socket.recv(size)

def host(hostname: str = "Host", ip: str = "127.0.0.1", port: int = 12345) -> ServerHandler:
    """
    Listen for connection with peer, returning a `ServerHandler` and listening for actions on a separate thread.
    IP must either be localhost (usually "127.0.0.1") or `server.net.get_ip()`.
    """
    if len(hostname) > 64:
        hostname = hostname[:63]
    net.get_data()["server"]["name"] = hostname
    core.DEV() and print("IP:", ip)
    client_socket = net.listen_for_connection(ip, port)
    host: core.Player = core.Player.from_save(hostname)
    clientname = recvok(client_socket, 64).decode()
    net.get_data()["client"]["name"] = clientname
    client_socket.send(chr(core.Constants.default_deck_size).encode())
    if client_socket.recv(2).decode == "no":
        return host(hostname, ip, port)
    client = recvok(client_socket, 4096).decode() # decks can be quite big.
    client: core.Player = core.Player.from_json(
        clientname,
        net.json.loads(client)
    )
    net.get_data()["client"]["commander"]["name"] = client.commander.card.name
    net.get_data()["server"]["commander"]["name"] = host.commander.card.name
    board = core.Board(host, client)
    handle = ServerHandler(board, client_socket)
    handle.sync()
    net.threading.Thread(target=net.listen, args=(client_socket, handle)).start()
    while core.DEV() and handle.ongoing:
        handle.run_action(input())
    return handle

def join(username: str, target_ip: str, port: int = 12345) -> ClientHandler:
    "Initialize connection with peer of IP `target_ip`, returning a `ClientHandler` and listening for logs on a separate thread."
    if len(username) > 64:
        username = username[:63]
    server_socket: net.socket.socket = net.join_connection(target_ip, port)
    if server_socket is None:
        return
    server_socket.send(username.encode())
    server_socket.recv(2)
    core.Constants.default_deck_size = recvok(server_socket, 1)[0]
    user: dict = core.Player.get_save_json(username)
    if user is None:
        user = {
            "commander": core.cleanstr(core.Player.get_commander().name),
            "deck": [core.cleanstr(creature.name) for creature in core.Player.get_deck()],
        }
    if len(user["deck"]) != core.Constants.default_deck_size:
        core.warn(f"Opponent expected a {core.Constants.default_deck_size}-cards long deck, got {len(user['deck'])}. Sending default deck.")
        user["deck"] = core.Player.get_deck()
    sendblock(server_socket, net.json.dumps(user, separators=(',', ':')).encode())
    handle = ClientHandler(server_socket)
    net.threading.Thread(target=net.listen, args=(server_socket, handle)).start()
    while core.DEV() and handle.ongoing:
        handle.run_action(input())
    return handle

def replay(replayname: str, delay: float = 0.3) -> ReplayHandler:
    "Counterpart to `join` and `host` to play a replay (contained in `./Replays/`) locally."
    handle = ReplayHandler()
    net.threading.Thread(target=handle.read_replay, args=(replayname, delay)).start()
    return handle

def str2target_client(index: str) -> core.ActiveCard | None:
    data = net.get_data()
    foes, foec, allies, allyc = core.ifelse(data["server_turn"],
        (data["client"]["board"], data["client"]["commander"], data["server"]["board"], data["server"]["commander"]),
        (data["server"]["board"], data["server"]["commander"], data["client"]["board"], data["client"]["commander"])
    )
    m = re.match("foe(\d+)", index)
    if m:
        i = int(m[1])
        if i >= len(foes):
            return None
        return foes[i]
    m = re.match("ally(\d+)", index)
    if m:
        i = int(m[1])
        if i >= len(allies):
            return None
        return allies[i]
    match core.cleanstr(index):
        case "allycommander": return allyc
        case "alliedcommander": return allyc
        case "enemycommander": return foec
        case "foecommander": return foec
        case "commander": return foec
        case _: return None

def str2target(board: core.Board, index: str) -> core.ActiveCard | None:
    m = re.match("foe(\d+)", index)
    if m:
        i = int(m[1])
        if i >= len(board.unactive_player.active):
            return None
        return board.unactive_player.active[i]
    m = re.match("ally(\d+)", index)
    if m:
        i = int(m[1])
        if i >= len(board.active_player.active):
            return None
        return board.active_player.active[i]
    match core.cleanstr(index):
        case "allycommander": return board.active_player.commander
        case "alliedcommander": return board.active_player.commander
        case "enemycommander": return board.unactive_player.commander
        case "foecommander": return board.unactive_player.commander
        case "commander": return board.unactive_player.commander
        case _: return None

def clientside_action(handle: ClientHandler | ServerHandler, action: str, *args):
    if action == "doc":
        if len(args) == 0:
            devlog("Missing `card name` argument.")
            return
        cardname = core.cleanstr(args[0])
        if cardname in core.getCOMMANDERS():
            card: core.AbstractCard = core.getCOMMANDERS()[cardname]
        else:
            card: core.AbstractCard = core.getCARDS()[core.Player.card_id(cardname)]
        if len(args) < 2:
            fname = card.element.to_str() + "-" + cardname
            with open(net.utility.os.path.join(net.utility.cwd_path, "Data/textsprites.json")) as io:
                try:
                    json = net.json.load(io)
                    if fname in json:
                        print(json[fname])
                    else:
                        print("Image not found.\n  ______\n /  __  \\\n/__/  \\  \\\n      /  /\n     /  /\n    |  |\n    |__|\n     __\n    (__)\n")
                finally:
                    io.close()
        devlog(card.__str__())
        return
    if action == "dochand":
        if isinstance(handle, ServerHandler):
            for card in handle.board.player1.hand:
                clientside_action(handle, "doc", card.name)
        else:
            for card in net.get_data()["client"]["hand"]:
                clientside_action(handle, "doc", card)
        return
    if action == "help":
        devlog(
"""
# Actions
help
doc|{card name}
doc|{card name}|noimg
dochand
showboard
attack|{ally index*}|{attack index}|{target index*}
spell|{hand index}|{target index*}
place|{hand index}|{board index}
discard|{hand index}
endturn
chat|{msg}

# Indices
Indices marked with * can be any of the following:
- `ally{i}`: `{i}`th creature on your side of the board.
- `foe{i}`: `{i}`th creature on your opponent's side of the board.
- `allied_commander`: your commander.
- `commander`: your opponent's commander.
Other indices are regular integer, starting from 0.
"""
        )
        return
    if action == "showboard":
        return handle.sync().showboard() # that's not clientside then
    devlog("Unrecognized action.")

def run_action(board: core.Board, client_socket: net.socket.socket, head: str, *args: str, source: bool) -> bool:
    """
    Run the following actions on the server, sending logs to the client.

    attack|{ally index*}|{attack index}|{target index*}
    spell|{hand index}|{target index*}
    place|{hand index}|{board index}
    discard|{hand index}
    endturn
    """
    head = core.cleanstr(head)
    isclientturn = board.active_player is board.player2
    if head == "endturn":
        result = board.endturn()
        if result[4] is not None:
            #sendblock(client_socket, log_win(None, result[4].name).encode())
            #client_socket.close()
            return True # socket must be closed *after* logs are sent.
        #logs = ""
        #for card in result[2]:
        #    if isclientturn:
        #        pass
        #        logs += log_draw(None, card.name) + "\n"
        #    else:
        #        devlog(f"You have drawn a {card.name}.")
        #logs += log_endturn(None, board.unactive_player.name,
        #            board.unactive_player.energy, board.unactive_player.max_energy, board.unactive_player.energy_per_turn)
        #client_socket.send(logs.encode())
        return True
    if head == "attack":
        if len(args) < 3:
            if isclientturn:
                client_socket.send(b"error|Missing arguments in attack request.")
            return devlog("Warning: Missing arguments in attack request.")
        user = str2target(board, args[0])
        if (user is None) or (user.owner == board.unactive_player):
            if isclientturn:
                client_socket.send(b"error|Wrong user in attack request.")
            return devlog("Warning: Wrong user target in attack request.")
        try:
            attack = user.card.attacks[int(args[1])]
        except:
            if isclientturn:
                client_socket.send(f'error|{user.name} has no such attack "{args[1]}".')
            return devlog(f'Warning: {user.name} has no such attack "{args[1]}".')
        target = str2target(board, args[2])
        if target is None:
            if isclientturn:
                client_socket.send(b"error|Invalid target.")
            return devlog("Warning: Invalid target.")
        survey = user.attack(attack, target)
        if survey.return_code.value > 299 and isclientturn:
            client_socket.send(f"error|Attack failed ({survey.return_code.value})".encode())
        return True
    if head == "chat":
        if len(args) == 0:
            return devlog("Warning: Message not found.")
        if len(args) == 1:
            log = f"chat|{core.ifelse(source, board.player2.name, board.player1.name)}|{args[0]}"
        else:
            log = f"chat|{args[0]}|{args[1]}"
        board.logs.append(log) # are sent through `handle.log_sync()`
        return True
    if head == "place":
        if len(args) < 2:
            if isclientturn:
                client_socket.send("error|Missing argument(s) to place card from hand.".encode())
            return devlog("Warning: Missing argument(s) to place card from hand.")
        try:
            i, j = int(args[0]), int(args[1])
        except:
            if isclientturn:
                client_socket.send("error|place expected integers.".encode())
            return devlog("Warning: place expected integers.")
        result = board.active_player.place(i, j)
        if not result:
            if isclientturn:
                client_socket.send("error|Invalid index (out of bound, wrong card or no card can be placed here).".encode())
            return devlog("Warning: Invalid index (out of bound, wrong card or no card can be placed here).")
        card: core.ActiveCard = board.active_player.active[j]
        #client_socket.send(log_place(None, card.card.name, str(j), str(card.card.cost)).encode())
        return True
    if head == "discard":
        if len(args) < 1:
            if isclientturn:
                client_socket.send("error|discard require one argument.".encode())
            return devlog("Warning: discard require one argument.")
        try:
            i = int(args[0])
        except:
            if isclientturn:
                client_socket.send("error|discard expected a number.".encode())
            return devlog("Warning: discard expected a number.")
        if i >= len(board.active_player.hand):
            if isclientturn:
                client_socket.send("error|out of bound discard.".encode())
            return devlog("Warning: out of bound discard.")
        card: core.AbstractCard = board.active_player.handdiscard(i)
        #client_socket.send(log_discard(None, card.name).encode())
        return True
    if head == "spell":
        if len(args) < 2:
            if isclientturn:
                client_socket.send("error|Missing arguments in spell request.".encode())
            return devlog("Warning: Missing arguments in spell request.")
        try:
            spell: core.SpellCard = board.active_player.hand[int(args[0])]
        except:
            if isclientturn:
                client_socket.send("error|Wrong spell index.".encode())
            return devlog("Warning: Wrong spell index.")
        if not isinstance(spell, core.SpellCard):
            if isclientturn:
                client_socket.send("error|Wrong spell index.".encode())
            return devlog("Warning: Wrong spell index.")
        target = str2target(board, args[1])
        if target is None:
            if isclientturn:
                client_socket.send("error|Invalid target.".encode())
            return devlog("Warning: Invalid target.")
        survey = spell.use(target)
        #logs = log_attack(None, spell.name, target.card.name,
        #                  spell.on_use.name, str(spell.on_use.cost),
        #                  str(survey.return_code.value),
        #                  str(survey.damage), str(survey.heal))
        #client_socket.send(logs.encode())
        return True
    if head == "forfeit":
        client_socket.send("win|???".encode())
        client_socket.close()
        return False
    core.warn("Tried to run unrecognized action.")
    return True

def showchat(name: str, msg: str):
    name = "\033[1m" + stringclr(name) + name + "\033[0m"
    devlog(name + ":", msg)
