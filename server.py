import socket
import pickle
import requests
from bs4 import BeautifulSoup

    
#def handle_client(client_socket):
    
        

def start_server():
    #AF_INET: specifies the address family — here, IPv4.
    # SOCK_STREAM: specifies the socket type — here, TCP.
    #	bind() assigns the socket to an address (host, port) tuple.
    #"localhost" means the server is only reachable from the same machine (use "0.0.0.0" or actual IP for public).

    print("Starting server...")
    print("Creating socket...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("binding socket...")
    s.bind(("localhost", 5050))
    print("Listening for connections...")
    #5 is the backlog — the max number of queued connection requests
    s.listen(5)
    print("Server is listening on port 5050...")


    
    while True:
    # Accepting connections in a loop
    #s.accept() blocks and waits for a client to connect.
    # client_socket is the new socket object for the connection.
    # addr is the address of the client.
        client_socket, addr = s.accept()
        print(f"Connection from {addr} has been established.")
        handle_client(client_socket)


if __name__ == "__main__":
    start_server()
