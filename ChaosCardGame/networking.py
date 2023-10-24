import socket



def host():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind(('127.0.0.1', 12345))
    # Listen for incoming connections
    server_socket.listen(5)

    print("Server listening for connections...")

    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}")



def connect():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect(('127.0.0.1', 12345))
