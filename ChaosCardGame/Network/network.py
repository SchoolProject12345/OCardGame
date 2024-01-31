import socket
import json
import threading
import utility

def get_data(loaded_data = {}):
    if bool(loaded_data):
        return loaded_data
    with open(utility.os.path.join(utility.cwd_path, 'Network/template.json')) as file:
        try:
            loaded_data.update(json.load(file))
        finally:
            file.close()
    return loaded_data

def data_handler(action: str, path: str, data: str, loaded_data: dict = get_data()):
    """
    Appends/removes/replaces data in a JSON file.

    Parameters:
        - action (str): Specifies the action to be performed. Possible values are 'append', 'remove' or 'replace'.

        - path (str): The path in the JSON file (e.g., 'Player0/deck/1').

        - data (str): The value you want appended or replaced.
    """
    if action not in ['append', 'remove', 'replace']:
        print("Invalid action. Supported actions: 'append', 'remove', 'replace'")
        return

    # Check if data is a dictionary
    try:
        if type(json.loads(data)) == dict:
            data = json.loads(data)
    except:
        pass

    keys = path.split('/')
    # Navigate the JSON structure based on the path
    current_node = loaded_data
    for key in keys[:-1]:
        if key in current_node:
            current_node = current_node[key]
        else:
            # Create the missing path for 'append'
            if action == 'append':
                current_node[key] = {}
                current_node = current_node[key]
            else:
                print(f"Key '{key}' not found in the JSON data at path '{path}'.")
                return

    last_key = keys[-1]
    if action == 'append':
        if last_key in current_node:
            if isinstance(current_node[last_key], list):
                current_node[last_key].append(data)
            elif isinstance(current_node[last_key], dict):
                for key, value in data.items():
                    current_node[last_key][key] = value
            else:
                print(f"Cannot append to a non-list node at path '{path}'.")
                return
        else:
            current_node[last_key] = data

    elif action == 'remove':
        if last_key in current_node:
            del current_node[last_key]
        else:
            print(f"Key '{last_key}' not found in the JSON data.")
            return

    elif action == 'replace':
        if isinstance(current_node, list):
            if not last_key.isnumeric():
                return print(f"Index '{last_key}' is not an integer.")
            current_node[int(last_key)] = data
        elif last_key in current_node:
            current_node[last_key] = data
        else:
            print(f"Key '{last_key}' not found in the JSON data.")
            return

    else:
        print("Invalid action. Supported actions: 'append', 'remove', 'replace'")
        return

    # can be read from here, but shouldn't get modified as the modifiction wouldn't be send to the peer.
    return loaded_data

def get_ip():
    "get local IP (its clapped, but works)"
    clapped = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clapped.connect(("8.8.8.8", 80))
    host = clapped.getsockname()[0]
    clapped.close()
    return host

def send(client_socket: socket.socket, action: str, path: str, data: str):
    """
    `send` updates both the local and peer's JSON file.
    See `data_handler` for information on arguments.
    """
    # Update local JSON
    data_handler(action, path, data)
    # Send update to peer
    client_socket.send((f"{action}|{path}|{data}").encode("utf-8"))

def default_handler(data: str) -> bool:
    "Default function used by `listen`."
    if not bool(data):
        return False
    data = data.split("|")
    action = data[0]
    path = data[1]
    data = data[2]
    data_handler(action, path, data)
    return True

def listen(client_socket: socket.socket, handler = default_handler):
    """
    `listen(client_socket)` must run constantly on a separate
    thread, as it needs to listen all the time
    for changes to the public directory
    """
    while True:
        data = client_socket.recv(4096).decode() # 4 kb of data, just to be sure.
        if not (handler(data) or bool(data)): # if empty byte string (socket was closed)
            client_socket.close()
            break

## ======================= SET UP CONNECTION ======================= ##

def listen_for_connection(ip: str, port: int):
    """
    This function is run by the host while
    the host is waiting for a connection request.
    """
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind((ip, port))
    listening_socket.listen(5)

    print(f"Listening for connection on {ip}:{port}")

    client_socket, addr = listening_socket.accept()  # one connection max
    print(f"Accepted connection from {addr}")

    return client_socket

def join_connection(target_ip: str, port: int):
    "Allow to join a connection started by `listen_for_connection` or `start_peer_to_peer` without running `listen` on separated thread."
    client_socket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)  # sock_stream for TCP
    client_socket.settimeout(5)

    try:
        client_socket.connect((target_ip, port))
        client_socket.settimeout(None)
        return client_socket
    except socket.error as e:
        print(f"Error connecting to {target_ip}:{port}: {str(e)}")
        return

def start_peer_to_peer(action, target_ip: str = get_ip(), port: int = 12345, handler = default_handler): # You can choose any available port
    """
    `start_peer_to_peer(action, target_ip)` is the starting point of the network program.
    The user will choose to join or to host a party.
    """
    # reset the data.json file
    get_data().clear()

    if action == "start":
        print("IP:", target_ip) # taking ip in argument allows to localhost
        client_socket = listen_for_connection(target_ip, port)
    else:
        client_socket = join_connection(target_ip, port)
        if client_socket is None:
            return False

        # This will run separately from the game.
    network_thread = threading.Thread(target=listen, args=(client_socket, handler))
    network_thread.start()
    return client_socket
