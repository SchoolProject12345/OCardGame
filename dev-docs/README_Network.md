# Network

This is a pretty simple networking library that allows the synchronisation of data between two users.

This library does not use the standard client-server model. Instead, the clients connect to eachother with sockets and send eachother the modifications they want to bring to the data.json file.

template.json replaces data.json, effectively clearing all data from the data.json file.

    # Usage

    ### The project must be organised like in this example:

    ```
    public/
    ├─ data.json
    network.py
    main.py
    template.json
    ```

### In the main file, import network.

```python
import network as net
```

### Two functions should be used in main.

`start_peer_to_peer(action, target_ip)` - This function is the starting point of the connection. "action" space includes "start" and "join" ; "target_ip" is the ip you want to join.

`send(socket: socket.socket, action: str, path: str, data: str)` - This function sends the changes to the other client and updates the local data.json at the same time.
    
> - socket (socket.socket): The client socket.
>
> - action (str): Specifies the action to be performed. Possible values are 'append', 'remove', or 'replace'.
>
> - path (str): The path in the JSON file (e.g., 'Player0/deck/1').
>
> - data (str): The value you want appended or replaced.


# Example Usage


```python
filename: main.py

# This represents the game
import socket # socket is only used for docs
import json

import network as net
from network import send



def main(client_socket: socket.socket):
    """
    main represents the thread on which the game is running.
    """
    try:
        while True:
            x = str(input("Enter 1 to send smth: \n"))
            if x == "1":
                send(client_socket, "append", "Player0/deck/1", "1010101010") ## example 1 of append
                send(client_socket, "append", "Player0/deck", json.dumps({"2": "202020202"})) ## example 2 of append
                # tested 'replace' method, 100% functionality
                # tested 'append' method, 100% functionality
                # tested 'remove' method, 100% functionality
            try:
                # check if socket is closed
                # this method will not work with the POC input(), but will work in the game
                client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            except:
                break
    except Exception as e:
        print(e)
        print("main thread error/closing")
    finally:
        client_socket.close()





if __name__ == "__main__":
    """
    The idea is we set up the listening function on thread 1, 

    then return the socket on thread 0 (this is thread 0),

    then start the game loop using the socket,
    """
    action = "join"
    target_ip = ""
    if input("Start party or join a party? ").lower() == "start":
        action = "start"
    else:
        target_ip = input("Enter the target peer's IP address (or 'exit' to quit): ")
    
    client_socket = net.start_peer_to_peer(action, target_ip)

    if client_socket:
        main(client_socket)
#        mainThread = threading.Thread(target=main, args=(client_socket,))
#        mainThread.start()
    else:
        print("Error with connection (Most likely timed out)")
```

# Background

### network.py:

* Functions:
>
> `send(socket: socket.socket, action: str, path: str, data: str)`: As explained above: update local JSON and send modifications to peer.
>
> `listen(client_socket: socket.socket)`: Must run on a separate thread. Receives data sent by peer, sends this data to data_handler(), and prints a bible verse.

* Connection set-up:
> `listen_for_connection(ip: str, port: str)`: This function is run by the host, while the host is waiting for a connection from the peer.
>
> `start_peer_to_peer()`: As explained above.

### data_handler.py:

* Functions:
> `data_handler(action: str, path: str, data: str)`: Updates data.json with the modifications.

# To implement in future:

Scanning for other players & join by name instead of IP
(currently woking on this)

# Known issues:

none, if you have one stop being a bish