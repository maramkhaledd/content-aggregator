import socket
import pickle
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def is_valid_news_link(url, base_url):
    """Check if the link is a valid news article link."""
    # Skip social media and common non-news domains
    social_domains = {
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "linkedin.com",
        "youtube.com",
        "pinterest.com",
        "tiktok.com",
        "reddit.com",
    }

    # Parse the URL
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)

    # Skip if it's a social media domain
    if any(domain in parsed_url.netloc.lower() for domain in social_domains):
        return False

    # Skip if it's not from the same domain as the base URL
    if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
        return False

    # Skip common non-article paths
    skip_paths = {
        "/login", "/signup", "/subscribe", "/account", "/profile", "/search",
        "/category", "/categories", "/section", "/sections", "/tag", "/tags",
        "/author", "/authors", "/archive", "/archives"
    }
    if any(path in parsed_url.path.lower() for path in skip_paths):
        return False

    # Skip URLs that are likely main pages or category pages
    path_parts = parsed_url.path.strip('/').split('/')

    # Skip if the URL is too short (likely a main page)
    if len(path_parts) < 2:
        return False

    # Skip if the URL doesn't contain any numbers or dates (common in news articles)
    has_numbers = any(any(c.isdigit() for c in part) for part in path_parts)
    if not has_numbers:
        return False

    return True


def process_url(url, base_url):
    """Convert relative URL to absolute URL and validate it."""
    if not url or url == "No link available":
        return "No link available"

    # Convert relative URL to absolute URL
    absolute_url = urljoin(base_url, url)

    # Validate the URL
    if is_valid_news_link(absolute_url, base_url):
        return absolute_url
    return "No link available"


def fetch_articles(url, max_articles=30):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        seen_titles = set()

        # First, look for structured content
        for tag in soup.find_all(["article", "div", "section"]):
            title = tag.find(["h1", "h2", "h3"])
            title = title.get_text(strip=True) if title else None
            link = tag.find("a", href=True)
            link = process_url(
                link["href"], url) if link else "No link available"

            if title and len(title) > 10 and title not in seen_titles and link != "No link available":
                articles.append((title, link))
                seen_titles.add(title)

        # Only fallback to global <p> if no articles were found
        if not articles:
            for tag in soup.find_all("p"):
                title = tag.get_text(strip=True)
                link = tag.find_parent("a", href=True)
                link = process_url(
                    link["href"], url) if link else "No link available"

                if title and len(title) > 10 and title not in seen_titles and link != "No link available":
                    articles.append((title, link))
                    seen_titles.add(title)

        return articles[:max_articles]
    except Exception as e:
        return []


def handle_client_request(client_socket):
    try:
        data_length_bytes = client_socket.recv(4)
        data_length = int.from_bytes(data_length_bytes, "big")

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
        client_socket.sendall(response_length.to_bytes(4, "big"))
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
