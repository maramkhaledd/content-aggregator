import socket
import pickle
import requests
from bs4 import BeautifulSoup

#def process_url()

def fetch_articles(url, max_articles=30):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return [("Failed to fetch data", f"HTTP {response.status_code}")]

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        seen_titles = set()

        # First, look for structured content
        for tag in soup.find_all(['article', 'div', 'section']):
            title = tag.find(['h1', 'h2', 'h3'])
            title = title.get_text(strip=True) if title else None
            link = tag.find('a', href=True)
            link = process_url(
                link['href'], url) if link else "No link available"

            if title and title not in seen_titles and link != "No link available":
                articles.append((title, link))
                seen_titles.add(title)

        # Only fallback to global <p> if no articles were found
        if not articles:
            for tag in soup.find_all('p'):
                title = tag.get_text(strip=True)
                link = tag.find_parent('a', href=True)
                link = process_url(
                    link['href'], url) if link else "No link available"

                if title and title not in seen_titles and link != "No link available":
                    articles.append((title, link))
                    seen_titles.add(title)

        return articles[:max_articles] if articles else [("No articles found", "")]
    except Exception as e:
        return [("Error occurred", str(e))]

def handle_client_request(client_socket):
    try:
        data_length_bytes = client_socket.recv(4)
        data_length = int.from_bytes(data_length_bytes, 'big')

        data = b""
        while len(data) < data_length:
            data += client_socket.recv(min(4096, data_length - len(data)))

        domains = pickle.loads(data)
        all_articles = []
        for domain in domains:
            if not domain.startswith(("http://", "https://")):
                domain = f"https://{domain}"
            articles = fetch_articles(domain, max_articles=10)
            all_articles.extend(articles)

        response = pickle.dumps(all_articles)
        response_length = len(response)
        client_socket.sendall(response_length.to_bytes(4, 'big'))
        client_socket.sendall(response)
        client_socket.close()
    except Exception as e:
        print(f"Error handling client request: {e}")
        client_socket.close()
      


def start_server():
    # AF_INET: specifies the address family — here, IPv4.
    # SOCK_STREAM: specifies the socket type — here, TCP.
    # 	bind() assigns the socket to an address (host, port) tuple.
    # "localhost" means the server is only reachable from the same machine (use "0.0.0.0" or actual IP for public).

    print("Starting server...")
    print("Creating socket...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("binding socket...")
    s.bind(("localhost", 5050))
    print("Listening for connections...")
    # 5 is the backlog — the max number of queued connection requests
    s.listen(5)
    print("Server is listening on port 5050...")

    while True:
        # Accepting connections in a loop
        # s.accept() blocks and waits for a client to connect.
        # client_socket is the new socket object for the connection.
        # addr is the address of the client.
        client_socket, addr = s.accept()
        print(f"Connection from {addr} has been established.")
        handle_client_request(client_socket)


if __name__ == "__main__":
    start_server()
