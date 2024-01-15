import Network.network as net
import Core.core_main as core
import re
core.os.system("") # Python somehow requires that to enable ANSI on most terminal.

@core.dataclass
class PseudoActiveCard:
    name: str
    hp: int
    max_hp: int
    element: core.Element
    card: core.AbstractCard
    def from_name(name: str):
        card: core.AbstractCard = core.getCARDS()[core.Player.card_id(name)]
        if not isinstance(card, core.CreatureCard):
            return PseudoActiveCard(name, 1j, 1j, core.Element.elementless, card)
        return PseudoActiveCard(name, card.max_hp, card.max_hp, card.element, card)
    def commander(name: str):
        if name in core.getCOMMANDERS():
            card: core.CommanderCard = core.getCOMMANDERS()[name]
            return PseudoActiveCard(name, card.max_hp, card.max_hp, card.element, card)
        return PseudoActiveCard(
            name, 600, 600, core.Element.elementless,
            core.CommanderCard(
                name, 1j, core.Element.elementless, 600,
                [], [], 0, ()
            )
        )

@core.dataclass
class PartialGameState:
    server: net.socket.socket
    canplay: bool
    foe_name: str
    foes: list[PseudoActiveCard | None]
    enemy_commander: PseudoActiveCard
    ally_name: str
    allies: list[PseudoActiveCard | None]
    ally_commander: PseudoActiveCard
    turn: int
    arena: core.Arena
    hand: list[str]
    deck_size: int
    discard: list[str]
    enemy_discard: list[str]
    opponent_energies: list[int] # current, max, /turn
    energies: list[int]
    def devprint(self):
        print("Turn", self.turn, "(" + core.ifelse(self.canplay, self.ally_name, self.foe_name) + "'s)\n")
        print(self.foe_name + "'s side:")
        print(self.enemy_commander.card.name + f" ({self.enemy_commander.hp}/{self.enemy_commander.card.max_hp})")
        for card in self.foes:
            if card is None:
                print("none ", end="")
                continue
            print(core.cleanstr(card.card.name), f"({card.hp}/{card.card.max_hp})", end = " ")
        print("\n")
        print(self.foe_name + "'s side:")
        print(self.ally_commander.card.name + f" ({self.ally_commander.hp}/{self.ally_commander.card.max_hp})")
        for card in self.allies:
            if card is None:
                print("none ", end="")
                continue
            print(core.cleanstr(card.card.name), f"({card.hp}/{card.card.max_hp})", end = " ")
        print(self.deck_size, "cards in deck.")
        print("\n")
        print("Your hand:", self.hand)

def sendblock(socket: net.socket.socket, *args):
    size = socket.send(*args)
    socket.recv(2)
    return size
def recvok(socket: net.socket.socket, *args):
    data = socket.recv(*args)
    socket.send(b"ok")
    return data

def host(hostname: str = "Host", ip: str = "127.0.0.1", port: int = 12345):
    if len(hostname) > 64:
        hostname = hostname[:63]
    core.DEV() and print("IP:", ip)
    client_socket = net.listen_for_connection(ip, port)
    host: core.Player = core.Player.from_save(hostname)
    clientname = client_socket.recv(64).decode()
    client_socket.send(b"ok")
    client = client_socket.recv(1024).decode() # decks can be quite big.
    client: core.Player = core.Player.from_json(
        clientname,
        net.json.loads(client)
    )
    board = core.Board(host, client)
    # turn info
    client_socket.send(core.ifelse(board.active_player is host, b'\0', b'\1'))
    # opponent's infos
    sendblock(client_socket, hostname.encode())
    client_socket.send(chr(len(host.active)).encode())
    sendblock(client_socket, core.cleanstr(host.commander.card.name).encode())
    # board's infos
    client_socket.send(chr(board.arena.value).encode())
    sendblock(client_socket, net.json.dumps([card.name for card in client.hand], separators=(',', ':')).encode())
    sendblock(client_socket, f"{host.energy}|{host.max_energy}|{host.energy_per_turn}".encode())
    sendblock(client_socket, f"{client.energy}|{client.max_energy}|{client.energy_per_turn}".encode())
    if core.DEV():
        server_dev(board, client_socket)
    return board, client_socket

def join(username: str, target_ip: str, port: int = 12345):
    if len(username) > 64:
        username = username[:63]
    server_socket: net.socket.socket = net.join_connection(target_ip, port)
    if server_socket is None:
        return
    server_socket.send(username.encode())
    server_socket.recv(2)
    user: dict = core.Player.get_save_json(username)
    if user is None:
        user = {
            "commander": core.cleanstr(core.Player.get_commander().name),
            "deck": [core.cleanstr(creature.name) for creature in core.Player.get_deck()],
        }
    server_socket.send(net.json.dumps(user, separators=(',', ':')).encode())
    canplay = bool(ord(server_socket.recv(1)))
    foe_name = recvok(server_socket, 64).decode()
    if foe_name == username:
        if len(foe_name) > 55:
            foe_name = "Opponent " + foe_name[:54]
        else:
            foe_name = "Opponent " + foe_name
    board_size = ord(server_socket.recv(1))
    enemy_commander = recvok(server_socket, 64).decode()
    arena = core.Arena(ord(server_socket.recv(1)))
    hand = net.json.loads(recvok(server_socket, 512).decode())
    opponent_energies = recvok(server_socket, 32).decode().split('|')
    energies = recvok(server_socket, 32).decode().split('|')
    game = PartialGameState(
        server_socket,
        canplay,
        foe_name,
        [None for _ in range(board_size)],
        PseudoActiveCard.commander(enemy_commander),
        username,
        [None for _ in range(board_size)],
        PseudoActiveCard.commander(user["commander"]),
        0,
        arena,
        hand,
        len(user["deck"]) - len(hand),
        [],
        [],
        [int(i) for i in opponent_energies],
        [int(i) for i in energies]
    )
    if core.DEV():
        client_dev(game)
    return game

def str2target_client(game: PartialGameState, index: str) -> core.ActiveCard | None:
    foes, foec, allies, allyc = core.ifelse(game.canplay,
        (game.foes, game.enemy_commander, game.allies, game.ally_commander),
        (game.allies, game.ally_commander, game.foes, game.enemy_commander)
    )
    m = re.match("foe(\d+)", index)
    if m:
        i = int(m[1])
        if i >= len(foes):
            return None
        return game.foes[i]
    m = re.match("ally(\d+)", index)
    if m:
        i = int(m[1])
        if i >= len(allies):
            return None
        return game.allies[i]
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

def client_dev(game: PartialGameState):
    ongoing = True
    while ongoing:
        while not game.canplay:
            data = recvok(game.server, 1024).decode()
            if data == "":
                ongoing = False
                devlog("Your opponent interrupted connection.")
                game.server.close()
                return
            logplay(game, data)
        action = input()
        head = action.split('|')[0]
        if head in ["doc", "help", "showboard", "dochand"]:
            clientside_action(game, *action.split('|'))
            continue
        if head not in ["help", "attack", "place", "spell", "discard", "endturn", "chat"]:
            print("Invalid action. Write `help` to get a list of valid actions.")
            continue
        game.server.send(action.encode())
        logplay(game, game.server.recv(512).decode())

def clientside_action(board: core.Board | PartialGameState, action: str, *args):
    if action == "doc":
        if len(args) == 0:
            return devlog("Missing `card name` argument.")
        cardname = core.cleanstr(args[0])
        if len(args) < 2:
            card: core.AbstractCard = core.getCARDS()[core.Player.card_id(cardname)]
            fname = card.element.to_str() + "-" + cardname
            with open("textsprites.json") as io:
                try:
                    json = net.json.load(io)
                    if fname in json:
                        print(json[fname])
                    else:
                        print("Image not found.\n  ______\n /  __  \\\n/__/  \\  \\\n      /  /\n     /  /\n    |  |\n    |__|\n     __\n    (__)\n")
                finally:
                    io.close()
        return devlog(card.__str__())
    if action == "dochand":
        if isinstance(board, core.Board):
            for card in board.player1.hand:
                clientside_action(board, "doc", card.name)
        else:
            for card in board.hand:
                clientside_action(board, "doc", card)
        return
    if action == "help":
        return devlog(
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
    if action == "showboard":
        return board.devprint()
    return devlog("Unrecognized action.")

def server_dev(board: core.Board, client_socket: net.socket.socket):
    ongoing = True
    while ongoing:
        while board.active_player is board.player2: # while the client is playing.
            data = recvok(client_socket, 1024).decode()
            if data == "":
                ongoing = False
                devlog("Your opponent interrupted connection.")
                client_socket.close()
                return
            run_action(board, client_socket, *data.split('|'))
            if len(data.split('|')) != 0 and core.cleanstr(data.split('|')[0]) == "endturn":
                break
        action = input()
        head = action.split('|')[0]
        if head in ["doc", "help", "showboard", "dochand"]:
            clientside_action(board, *action.split('|'))
            continue
        if head not in ["help", "attack", "place", "spell", "discard", "endturn", "chat"]:
            print("Invalid action. Write `help` to get a list of valid actions.")
            continue
        run_action(board, client_socket, *action.split('|'))

def run_action(board: core.Board, client_socket: net.socket.socket, head: str, *args: str):
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
            sendblock(client_socket, log_win(None, result[4].name).encode())
            client_socket.close()
            return
        logs = ""
        for card in result[2]:
            if isclientturn:
                logs += log_draw(None, card.name) + "\n"
            else:
                devlog(f"You have drawn a {card.name}.")
        logs += log_endturn(None, board.unactive_player.name,
                    board.unactive_player.energy, board.unactive_player.max_energy, board.unactive_player.energy_per_turn)
        sendblock(client_socket, logs.encode())
        return
    if head == "attack":
        if len(args) < 3:
            if isclientturn:
                client_socket.send("error|Missing arguments in attack request.".encode())
            return devlog("Warning: Missing arguments in attack request.")
        user = str2target(board, args[0])
        if len(args[0]) < 3 or (args[0][:3] not in ["all"]) or (user is None):
            if isclientturn:
                client_socket.send("error|Wrong user in attack request.".encode())
            return devlog("Warning: user target in attack request.")
        try:
            attack = user.card.attacks[int(args[1])]
        except:
            if isclientturn:
                client_socket.send(f'error|{user.name} has no such attack "{args[1]}".')
                return devlog(f'Warning: {user.name} has no such attack "{args[1]}".')
        target = str2target(board, args[2])
        if target is None:
            if isclientturn:
                client_socket.send("error|Invalid target.".encode())
            return devlog("Warning: Invalid target.")
        survey = user.attack(attack, target)
        logs = log_attack(None, user.card.name, target.card.name,
                          attack.name, str(attack.cost),
                          str(survey.return_code.value),
                          str(survey.damage), str(survey.heal))
        client_socket.send(logs.encode())
    if head == "chat":
        if isclientturn:
            return devlog(board.active_player.name + ":", *args)
        else:
            if len(args) < 1:
                return devlog("Warning: Message not found.")
            client_socket.send(f"chat|{args[0]}".encode())
            return
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
            devlog("Warning: place expected integers.")
            return
        result = board.active_player.place(i, j)
        if not result:
            if isclientturn:
                client_socket.send("error|Invalid index (out of bound, wrong card or no card can be placed here).".encode())
            return devlog("Warning: Invalid index (out of bound, wrong card or no card can be placed here).")
        card: core.ActiveCard = board.active_player.active[j]
        client_socket.send(log_place(None, card.card.name, str(j), str(card.card.cost)).encode())
        return
    if head == "discard":
        if len(args) < 1:
            if isclientturn:
                client_socket.send("error|discard require one argument.".encode())
            devlog("Warning: discard require one argument.")
        try:
            i = int(args[0])
        except:
            if isclientturn:
                client_socket.send("error|discard expected a number.".encode())
            devlog("Warning: discard expected a number.")
        card: core.AbstractCard = board.active_player.handdiscard(i)
        client_socket.send(log_discard(None, card.name).encode())
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
        survey = spell.use(target, board)
        logs = log_attack(None, spell.name, target.name,
                          spell.on_use.name, str(spell.on_use.cost),
                          str(survey.return_code.value),
                          str(survey.damage), str(survey.heal))
        client_socket.send(logs.encode())

def logplay(game: PartialGameState | None, log: str):
    if not bool(log):
        return
    if "\n" in log:
        for _log in log.split("\n"):
            logplay(game, _log)
    log: list[str] = log.split('|')
    args = [game] + log[1:]
    match core.cleanstr(log[0]):
        case "attack": log_attack(*args)
#       case "damage": log_damage(*args)
#       case "heal": log_heal(*args)
        case "defeat": log_defeat(*args)
        case "win": log_win(*args)
        case "endturn": core.show(log); log_endturn(*core.show(args))
        case "draw": log_draw(*args)
        case "discard": log_discard(*args)
        case "place": log_place(*args)
        case "error": devlog(f"Error: {args[1]}")
        case "chat": devlog(game.foe_name + ":", *log[1:])
        case _: devlog(f"Unown logging ({log[0]}):", *log[1:])

def devlog(*msg, dev: bool = core.DEV()):
    dev and print(*msg)

def log_attack(game: PartialGameState | None, user: str,
               target: str, attackname: str, cost: str,
               return_code: str, damage_dealt: str, healing_done: str):
    if int(return_code) != core.ReturnCode.ok:
        devlog(f"Attack {attackname} of {user} failed ({return_code}).")
    else:
        devlog(f"{user} successfully used {attackname} against {target} dealing {damage_dealt} and healing {healing_done} damages")
    return f"attack|{user}|{target}|{attackname}|{cost}|{return_code}|{damage_dealt}|{healing_done}"

def log_endturn(game: PartialGameState | None, player_name: str, energy: str, max_energy: str, energy_per_turn: str):
    devlog(f"{player_name} ends their turn. Their current energy is {energy}/{max_energy} after the gained {energy_per_turn}.")
    if game is not None:
        if game.canplay:
            game.energies[:] = [energy, max_energy, energy_per_turn]
            game.canplay = False
        else:
            game.opponent_energies[:] = [energy, max_energy, energy_per_turn]
            game.canplay = True
    return f"endturn|{player_name}|{energy}|{max_energy}|{energy_per_turn}"

def log_place(game: PartialGameState | None, cardname: str, index: str, cardcost: str):
    devlog(f"A {cardname} has been placed at the {index}th index.") # 1th > 1st
    if game is not None:
        if game.canplay:
            game.energies[0] -= int(cardcost)
            game.allies[int(index)] = PseudoActiveCard.from_name(cardname)
        else:
            game.opponent_energies[0] -= int(cardcost)
            game.foes[int(index)] = PseudoActiveCard.from_name(cardname)
    return f"place|{cardname}|{index}|{cardcost}"

def log_draw(game: PartialGameState | None, card_drawn: str):
    if game is not None:
        devlog(f"You have drawn a {card_drawn}.")
        game.deck_size -= 1
        if game.deck_size == 0:
            game.deck_size = len(game.discard)
            game.discard.clear()
    return f"draw|{card_drawn}"
def log_discard(game: PartialGameState | None, card_discarded: str):
    devlog(f"The active player discarded {card_discarded}")
    if game is not None and game.canplay:
        game.discard.append(card_discarded)
    return f"discard|{card_discarded}"

def log_win(game: PartialGameState | None, winner: str):
    devlog(f"The winner is {winner}.")
    if game is not None:
        game.server.close()
    return f"win|{winner}"

def log_defeat(game: PartialGameState | None, index: str):
    devlog("Creature at index {index} has been defeated.")
    if game is not None:
        creature: PseudoActiveCard = str2target_client(game, index)
        if creature is not None:
            for i in range(len(game.allies)):
                if game.allies[i] is creature:
                    game.allies[i] = None
                    game.discard.append(creature.card.name)
            for i in range(len(game.foes)):
                if game.foes[i] is creature:
                    game.foes[i] = None
                    game.enemy_discard.append(creature.card.name)
    return f"defeat|{index}"
