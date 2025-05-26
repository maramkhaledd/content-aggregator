import socket
import pickle
import requests
from bs4 import BeautifulSoup


def start_server():
    print("Creating socket...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("binding socket...")
    s.bind("localhost", 5050)
    print("Listening for connections...")
    s.listen(5)
    print("Server is listening on port 5050...")

    while True:
        client_socket, addr = s.accept()
        print(f"Connection from {addr} has been established.")


if __name__ == "__main__":
    start_server()
