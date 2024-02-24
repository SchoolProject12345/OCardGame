import Network.network as net
from time import time_ns
from Core.replay import * # includes core
import re
core.os.system("") # Python somehow requires that to enable ANSI on most terminal.

core.Constants.clientside_actions = ["help", "doc", "dochand", "showboard", "debug"] # debug prints gamestate.
core.Constants.anytime_actions = ["chat", "forfeit", "ready"] # can be used even if not their turn.
core.Constants.serverside_actions = ["attack", "spell", "place", "discard", "endturn"] + core.Constants.anytime_actions

class SingletonMonad(type):
    """
    Setting this has a metaclas allow the class *itself* to be a wrapper around its field defined through `wrap`.
    All the wrapped field's fields are also accessible from the class itself.
    Instances of the class are typically not created.
    All non-existing fields are returned as the `Void` value, which can then be infinitely accessed.

    # Example
    ```py
    >>> class Foo:
    ...     x: int
    ...     y: int
    ...     def __init__(self, x: int, y: int):
    ...         self.x = x
    ...         self.y = y
    ...     def sum(self):
    ...         return self.x + self.y
    >>> class FooWrapper(metaclass=SingletonMonad):
    ...     wrap: str = "foo" # name of the wrapped value
    ...     foo: Foo = Foo(3, 2) # wrapped value
    ...     @classmethod # methods need to be classmethod to take self.
    ...     def prod(self): # other methods/field can be implemented as well for error handling
    ...         return self.x * self.y # equivalent to `self.foo.x * self.foo.y`
    >>> FooWrapper.sum()
    5
    >>> FooWrapper.prod()
    6
    >>> FooWrapper.field.that.doesnt.exist() is Void
    True
    ```
    """
    wrap: str
    def __getattribute__(self, name: str): # different from __getattr__ obviously ( ͡° ͜ʖ ͡°)
        try: # hasattr is just a try
            return type.__getattribute__(self, name) # for other fields, methods or such
        except AttributeError:
            pass
        try: # I hate Python so much
            wrap: ReplayHandler = type.__getattribute__(self, type.__getattribute__(self, "wrap"))
            return wrap.__getattribute__(name)
        except AttributeError:
            return Void # fallback method
    def __call__(self, *_, **kwargs):
        return self # avoid creating instances.

class Void(metaclass=SingletonMonad):
    pass

class HandlerHandler(metaclass=SingletonMonad):
    wrap: str = "_handle"
    _handle: ReplayHandler = ReplayHandler()
    ip_address: str = "Loading..."
    initialized: bool = False
    @classmethod
    def init_handler(self, method: object, *args: str, **kwargs):
        "Setup connection and store the handle created as `self.handle`."
        self._handle = method(*args, **kwargs)
        self.initialized = True
    @classmethod
    def fetch_handler(self, method: object, *args: str, **kwargs) -> bool:
        """
        Setup connection on another thread and store the handle created as `self.handle`.
        Return `True` if successful, `False` otherwise.
        """
        if method is ReplayHandler.read_replay:
            args = (SingletonMonad.__getattribute__("_handle"), *args)
        if method in [join, host]:
            self.ip_adress = args[1]
            if self.deck is not Void:
                core.Player.save_json(args[0], HandlerHandler.deck, HandlerHandler.commander)
        elif method not in [ReplayHandler.read_replay]:
            core.warn(f"Tried to intiialize HandlerHandler with unrecognized method: {method.__qualname__}")
            return False
        if method is host:
            arena = core.Arena.random()
            self.state["arena"] = arena
            kwargs["arena"] = arena
        net.threading.Thread(
            target=self.init_handler,
            args=(method, *args),
            kwargs=kwargs,
            daemon=True
        ).start()
        return True

def get_ip():
    "Return local IP or localhost if not found, and set it to HandlerHandler."
    ip = HandlerHandler.ip_address # doesn't recompute IP
    expr = re.compile(r"^\d+\.\d+\.\d+\.\d+$") # only IPv.4
    localhost = re.compile(r"^127\.\d+\.\d+\.\d+") # only return localhost in case of error
    if ip is Void or not re.match(expr, ip):
        ip = "127.0.0.1"
    else:
        return ip
    ips: list = net.socket.getaddrinfo(net.socket.gethostname(), None) # might not be 100% system independant
    ips = [ip[4][0] for ip in ips]
    ips = [ip for ip in ips if re.match(expr, ip) and not re.match(localhost, ip)]
    ip = ip if len(ips) == 0 else ips[0]
    if not re.match(localhost, ip):
        HandlerHandler.ip_address = ip
        return ip
    sock = net.socket.socket(net.socket.AF_INET, net.socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip: str = sock.getsockname()[0] # most precise way to get IP
    finally:
        sock.close()
        HandlerHandler.ip_address = ip
        return ip
get_ip() # initialize HandlerHandler's ip

class ServerHandler(ReplayHandler):
    board: core.Board
    client_socket: net.socket.socket
    closed: bool = False
    ready: bool = False
    remote_ready: bool = False
    @static
    def __init__(self, board: core.Board, client_socket: net.socket.socket):
        ReplayHandler.__init__(self)
        self.board = board
        self.client_socket = client_socket
        self.closed        = False
        self.ready         = False
        self.remote_ready  = False
    @static # Just realized I destroy duck typing everywhere, while literally using it one line lower.
    def __call__(self, data: str) -> bool: # __call__ allows to quack like a function.
        if not self.ongoing:
            return False
        if data == "":
            self.ongoing = False
            return False
        if '\n' in data:
            # short circuit if false: socket was closed and should not execute any more action
            return all(self(_data) for _data in data.split('\n'))
        datas: list[str] = data.split('|')
        head = core.cleanstr(datas[0])
        if head == "ready":
            self.remote_ready = True
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
    def endgame(self):
        if core.get_setting("automatically_save_replay", True):
            self.save_replay()
        def endgame(handle: ServerHandler):
            sleep(3.0)
            handle.ongoing = False # avoids closing before seding the last informations
        net.threading.Thread(target=endgame, args=(self,))
        return self
    def isp1(self) -> bool: return True
    @static
    def run_action(self, action: str) -> bool:
        args = action.split('|')
        head = args[0]
        if head == "ready":
            self.client_socket.send(b"ready")
            self.ready = True
            return True
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
            head, *args, kwargs = kwargssplit(log)
            try:
                msg = self.play_log(log, head, *args, **kwargs) # TODO: don't log to the terminal when remote draw a card.
                if head == "draw" and args[0] == "p2":
                    devlog(f"{self.state['p2']['name']} drew a card.")
                else:
                    devlog(msg)
            except Exception as e:
                print("Error with:", log)
                print(repr(e))
            if head == "draw" and args[0] == "p1":
                log = f"draw|p1|card" # "{name} drew a card."
            logs += log + "\n"
        logs = logs.strip()
        if len(logs) != 0:
            self.client_socket.send(logs.encode()) # logs are split by line uppon reception.
        return self
    def showboard_debug(self):
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
            print(progressbar(player2.commander_charges, player2.commander.card.attacks[1].cost, style=core.Constants.progressbar_style))
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
            print(progressbar(player1.commander_charges, player1.commander.card.attacks[1].cost, style=core.Constants.progressbar_style))
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

        print("Their hand: ", end="")
        for card in player2.hand:
            print(card.name.replace(",", " -"), end=", ")
        if len(player1.hand) == 0:
            print("∅  ", end="")
        print("\033[2D ")

        return self # to chain

class ClientHandler(ReplayHandler):
    server_socket: net.socket.socket
    waiting: bool      = False
    closed: bool       = False
    ready: bool        = False
    remote_ready: bool = False
    @static
    def __init__(self, server_socket: net.socket.socket, waiting: bool = False):
        ReplayHandler.__init__(self)
        self.server_socket = server_socket
        self.waiting      = False
        self.state["pov"] = "p2"
        self.closed       = False
        self.ready        = False
        self.remote_ready = False
    @static
    def __call__(self, data: str) -> bool:
        self.waiting = False
        if data == "":
            self.ongoing = False
            return False
        if '\n' in data:
            return all(self(_data) for _data in data.split('\n'))
        head, *args, kwargs = kwargssplit(data)
        if head == "ready":
            self.remote_ready = True
            return True
        try:
            devlog(self.play_log(data, head, *args, **kwargs))
        except Exception as e:
            print("Error with:", data)
            print(repr(e))
        return True
    def endgame(self):
        if core.get_setting("automatically_save_replay", True):
            self.save_replay() # TODO ask to server
        def endgame(handle: ServerHandler):
            sleep(3.0)
            handle.ongoing = False # avoid closing before fetching last informations from server
        net.threading.Thread(target=endgame, args=(self,)).start()
        return self
    @static
    def isp1(self) -> bool: return False
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
    @static
    def run_action(self, action: str):
        "Request server to run action, returning `True` if sucessfully sent and `False` if clientside check failed."
        args = action.split('|')
        head = args[0]
        if head == "ready":
            self.ready = True
            self.server_socket.send("ready");
            return True
        if head in core.Constants.clientside_actions:
            clientside_action(self, *args)
            return True
        if head not in core.Constants.serverside_actions:
            devlog("Invalid action. Write `help` to get a list of valid actions.")
            return False
        if self.state["activep"] == "p1" and head not in core.Constants.anytime_actions:
            core.warn("Wrong turn.")
            return False
        if head == "chat":
            if len(args) < 2:
                devlog("Missing message in `chat` request.")
                return False
            action = f"chat|{self.get_state()['local']['name']}|{args[1]}"
        self.sendblock(action.encode(), max_wait=300_000_000)
        return True
    def showboard_debug(self):
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
            style = core.Constants.progressbar_style
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

@static
def sendblock(socket: net.socket.socket, *args):
    "Send and block until receiving 'ok' or any two-byte message."
    size = socket.send(*args)
    socket.recv(2)
    return size
@static
def recvok(socket: net.socket.socket, *args):
    "Send 'ok' after receiving to release `sendblock`."
    data = socket.recv(*args)
    socket.send(b"ok")
    return data
@static
def sendrecv(socket: net.socket.socket, size: int, *args):
    "Send `*args` to `socket` then wait until a message with up to `size` size is received, returning it as `bytes`."
    socket.send(*args)
    return socket.recv(size)

def username_check(username: str, *, _valid: bool = True) -> tuple[str, bool]:
    "Make various check to see if the string is a valid username and return a valid username based on the one given as argument."
    if len(username) > 64:
        return username_check(username[0:64], False) # excludes 64
    # short circuits
    if all(c == ' ' for c in username):
        return "#BLANK#", False
    return username, _valid

@static
def host(hostname: str = "Host", ip: str = "127.0.0.1", /, port: int = 12345, *, arena: core.Arena = core.Arena.själløssmängd) -> ServerHandler:
    """
    Listen for connection with peer, returning a `ServerHandler` and listening for actions on a separate thread.
    IP must either be localhost (usually "127.0.0.1") or `server.get_ip()`.
    """
    hostname, username_valid = username_check(hostname)
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
    if arena is core.Arena.själløssmängd:
        arena = core.Arena.random()
    board = core.Board(host, client, autoplay=False, arena=arena)
    handle = ServerHandler(board, client_socket)
    def listen(handler: ServerHandler):
        while handler.ongoing and not handler.closed:
            # The client shouldn't have to send more than 1024 bytes at once
            # Please don't chat too much
            if not handler(handler.client_socket.recv(1024).decode()) and not handler.closed:
                handler.client_socket.close()
                handler.ongoing = False
                handler.closed = True
    net.threading.Thread(target=listen, args=(handle,)).start()
    handle.log_sync()
    if core.DEV():
        def dev_read_for_actions(handle: ServerHandler):
            while handle.ongoing:
                action = input()
                if handle.ongoing and not handle.closed:
                    handle.run_action(action)
        net.threading.Thread(target=dev_read_for_actions, args=(handle,)).start()
    return handle

@static
def join(username: str, target_ip: str, /, port: int = 12345) -> ClientHandler:
    "Initialize connection with peer of IP `target_ip`, returning a `ClientHandler` and listening for logs on a separate thread."
    usenrame, username_valid = username_check(username)
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
        user["deck"] = [card.name for card in core.Player.get_deck()]
    sendblock(server_socket, net.json.dumps(user, separators=(',', ':')).encode())
    handle = ClientHandler(server_socket)
    def listen(handler: ClientHandler):
        while handler.ongoing:
            # Logs may be quite big so 4096 bytes buffer to be sure
            if not handler(handler.server_socket.recv(4096).decode()) and not handler.closed:
                handler.server_socket.close()
                handler.ongoing = False
                handler.closed = True
    net.threading.Thread(target=listen, args=(handle,)).start()
    if core.DEV():
        def dev_read_for_actions(handle: ClientHandler):
            while handle.ongoing:
                action = input()
                if handle.ongoing and not handle.closed:
                    handle.run_action(action)
        net.threading.Thread(target=dev_read_for_actions, args=(handle,)).start()
    return handle

@static
def replay(replayname: str, /, *, delay: float = 0.3) -> ReplayHandler:
    "Counterpart to `join` and `host` to play a replay (contained in `./Replays/`) locally."
    handle = ReplayHandler()
    net.threading.Thread(target=handle.read_replay, args=(replayname,), kwargs={"delay":delay}).start()
    return handle

@static
def str2target_client(index: str) -> object:
    data = net.get_data()
    foes, foec, allies, allyc = core.ifelse(data["server_turn"],
        (data["client"]["board"], data["client"]["commander"], data["server"]["board"], data["server"]["commander"]),
        (data["server"]["board"], data["server"]["commander"], data["client"]["board"], data["client"]["commander"])
    )
    m = re.match("(remote|foe)(\d+)", index)
    if m:
        i = int(m[2])
        if i >= len(foes):
            return None
        return foes[i]
    m = re.match("(local|ally)(\d+)", index)
    if m:
        i = int(m[2])
        if i >= len(allies):
            return None
        return allies[i]
    match core.cleanstr(index):
        case "allycommander": return allyc
        case "allyat": return allyc
        case "alliedcommander": return allyc
        case "localat": return allyc
        case "enemycommander": return foec
        case "foecommander": return foec
        case "foeat": return foec
        case "commander": return foec
        case "remoteat": return foec
        case _: return None

@static
def str2target(board: core.Board, index: str) -> core.ActiveCard | None:
    m = re.match("(foe|remote)(\d+)", index)
    if m:
        i = int(m[2])
        if i >= len(board.unactive_player.active):
            return None
        return board.unactive_player.active[i]
    m = re.match("(ally|local)(\d+)", index)
    if m:
        i = int(m[2])
        if i >= len(board.active_player.active):
            return None
        return board.active_player.active[i]
    match core.cleanstr(index):
        case "allycommander": return board.active_player.commander
        case "alliedcommander": return board.active_player.commander
        case "allyat": return board.active_player.commander
        case "localat": return board.active_player.commander
        case "enemycommander": return board.unactive_player.commander
        case "foecommander": return board.unactive_player.commander
        case "foeat": return board.unactive_player.commander
        case "commander": return board.unactive_player.commander
        case "remoteat": return board.unactive_player.commander
        case _: return None

@static
def clientside_action(handle: ClientHandler | ServerHandler, action: str, *args) -> ClientHandler | ServerHandler:
    if action == "doc":
        if len(args) == 0:
            devlog("Missing `card name` argument.")
            return handle
        cardname = core.cleanstr(args[0])
        if cardname in core.getCOMMANDERS():
            card: core.AbstractCard = core.getCOMMANDERS()[cardname]
        else:
            card: core.AbstractCard = core.getCARDS()[core.Player.card_id(cardname)]
        if len(args) < 2:
            fname = card.element.to_str() + "-" + cardname
            with open(core.os.path.join(core.Constants.path, "Data/textsprites.json")) as io:
                try:
                    json = net.json.load(io)
                    if fname in json:
                        print(json[fname])
                    else:
                        print("Image not found.\n  ______\n /  __  \\\n/__/  \\  \\\n      /  /\n     /  /\n    |  |\n    |__|\n     __\n    (__)\n")
                finally:
                    io.close()
        devlog(card.__str__())
        return handle
    if action == "dochand":
        if isinstance(handle, ServerHandler):
            for card in handle.board.player1.hand:
                clientside_action(handle, "doc", card.name)
        else:
            for card in net.get_data()["client"]["hand"]:
                clientside_action(handle, "doc", card)
        return handle
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
        return handle
    if action == "showboard":
        handle.showboard() # syncronizations is normally flawless, no need to ask for it
        return handle
    if action == "debug":
        print("\n\033[1m# Game State\033[0m\n", handle.state, "\n\n\033[1m# UI Formatted\033[0m\n", handle.get_state(), "\n", sep="")
        handle.showboard_debug()
        return handle
    devlog("Unrecognized action.")
    return handle

@static
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
            return True # socket must be closed *after* logs are sent.
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
        if survey.return_code.value > 299:
            if isclientturn:
                client_socket.send(f"error|Attack failed ({survey.return_code.value}: {survey.return_code.name})".encode())
            core.warn(f"Attack failed ({survey.return_code.value}: {survey.return_code.name})")
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
        if survey.return_code.value > 299:
            if isclientturn:
                client_socket.send(f"error|Spell {spell.name} returned with code {survey.return_code.value} ({survey.return_code.name}).".encode())
            devlog(f"Warning: spell {spell.name} retruned with code {survey.return_code.value} ({survey.return_code.name}).")
        return True
    if head == "forfeit":
        if source:
            player = board.player2
        else:
            player = board.player1
        player.forfeit()
        return True
    core.warn("Tried to run unrecognized action.")
    return True

@static
def showchat(name: str, msg: str):
    name = "\033[1m" + stringclr(name) + name + "\033[0m"
    devlog(name + ":", msg)
