import socket
import json
import threading
import shutil


def data_handler(action: str, path: str, data: str):
    """
    Appends/removes/replaces data in a JSON file.

    Parameters:
        - action (str): Specifies the action to be performed. Possible values are 'append', 'remove', or 'replace'.

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

    with open('./public/data.json', 'r') as file:
        loaded_data = json.load(file)

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
                print(
                    f"Key '{key}' not found in the JSON data at path '{path}'.")
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
        if last_key in current_node:
            current_node[last_key] = data
        else:
            print(f"Key '{last_key}' not found in the JSON data.")
            return

    else:
        print("Invalid action. Supported actions: 'append', 'remove', 'replace'")
        return

    # Write the modified data back to the file
    with open("./public/data.json", 'w') as file:
        json.dump(loaded_data, file, indent=2)


def get_ip():
    """
    get local IP (its clapped, but works)
    """
    clapped = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clapped.connect(("8.8.8.8", 80))
    host = clapped.getsockname()[0]
    clapped.close()
    return host


def send(client_socket: socket.socket, action: str, path: str, data: str):
    """
    send() updates both the local and peer's JSON file.
    """
    # Update local JSON
    data_handler(action, path, data)
    # Send update to peer
    client_socket.send((f"{action}|{path}|{data}").encode("utf-8"))


def listen(client_socket: socket.socket):
    """
    listen() must run constantly on a separate
    thread, as it needs to listen all the time
    for changes to the public directory
    """
    while True:
        data = client_socket.recv(1024).decode("utf-8")  # 1 kb of data

        if not data:  # if empty byte string (socket was closed)
            client_socket.close()
            break

        data = data.split("|")
        action = data[0]
        path = data[1]
        data = data[2]
        data_handler(action, path, data)


## ======================= SET UP CONNECTION ======================= ##

def listen_for_connection(ip: str, port: str):
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

    network_thread = threading.Thread(target=listen, args=(client_socket,))
    network_thread.start()

    return client_socket


def start_peer_to_peer(action, target_ip: str = ""):
    """
    start_peer_to_peer() is the starting point of the network program.
    The user will choose to join or to host a party.
    """
    ip = get_ip()

    # reset the data.json file
    shutil.copyfile('template.json', './public/data.json')
    # host = socket.gethostname()
    port = 12345  # You can choose any available port
    print("IP: ", ip)

    if action == "start":
        client_socket = listen_for_connection(ip, port)
        return client_socket
    else:
        target_port = 12345

        client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # sock_stream for TCP
        client_socket.settimeout(5)

        try:
            client_socket.connect((target_ip, target_port))
            client_socket.settimeout(None)
        except socket.error as e:
            print(f"Error connecting to {target_ip}:{target_port}: {str(e)}")
            return False

        # This will run separately from the game.
        network_thread = threading.Thread(target=listen, args=(client_socket,))
        network_thread.start()
        return client_socket
