import socket
import pickle
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def is_valid_news_link(url, base_url):
    social_domains = {
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
        "youtube.com", "pinterest.com", "tiktok.com", "reddit.com",
    }

    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)

    if any(domain in parsed_url.netloc.lower() for domain in social_domains):
        return False
    if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
        return False

    skip_paths = {
        "/login", "/signup", "/subscribe", "/account", "/profile", "/search",
        "/category", "/categories", "/section", "/sections", "/tag", "/tags",
        "/author", "/authors", "/archive", "/archives"
    }
    if any(path in parsed_url.path.lower() for path in skip_paths):
        return False

    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        return False

    has_numbers = any(any(c.isdigit() for c in part) for part in path_parts)
    if not has_numbers:
        return False

    return True


def process_url(url, base_url):
    if not url or url == "No link available":
        return "No link available"
    absolute_url = urljoin(base_url, url)
    if is_valid_news_link(absolute_url, base_url):
        return absolute_url
    return "No link available"


def fetch_articles(url, max_articles=30):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        seen_titles = set()

        for tag in soup.find_all(["article", "div", "section"]):
            title = tag.find(["h1", "h2", "h3"])
            title = title.get_text(strip=True) if title else None
            link = tag.find("a", href=True)
            link = process_url(link["href"], url) if link else "No link available"

            if title and len(title) > 10 and title not in seen_titles and link != "No link available":
                articles.append((title, link))
                seen_titles.add(title)

        if not articles:
            for tag in soup.find_all("p"):
                title = tag.get_text(strip=True)
                link = tag.find_parent("a", href=True)
                link = process_url(link["href"], url) if link else "No link available"

                if title and len(title) > 10 and title not in seen_titles and link != "No link available":
                    articles.append((title, link))
                    seen_titles.add(title)

        return articles[:max_articles]
    except Exception as e:
        print(f"Error fetching articles from {url}: {e}")
        return []


def handle_client_request(client_socket):
    try:
        data_length_bytes = client_socket.recv(4)
        data_length = int.from_bytes(data_length_bytes, "big")

        data = b""
        while len(data) < data_length:
            data += client_socket.recv(min(4096, data_length - len(data)))

        request = pickle.loads(data)

        if isinstance(request, dict) and request.get("type") == "keyword":
            keyword = request.get("data")
            print(f"[KEYWORD] Received keyword search: {keyword}")
            search_url = f"https://www.bing.com/news/search?q={keyword}"
            articles = fetch_articles(search_url, max_articles=10)

        else:
            domains = request
            print(f"[DOMAINS] Received domain list: {domains}")
            articles = []
            for domain in domains:
                if not domain.startswith(("http://", "https://")):
                    domain = f"https://{domain}"
                articles.extend(fetch_articles(domain, max_articles=10))

        response = pickle.dumps(articles)
        response_length = len(response)
        client_socket.sendall(response_length.to_bytes(4, "big"))
        client_socket.sendall(response)
        client_socket.close()

    except Exception as e:
        print(f"Error handling client request: {e}")
        client_socket.close()


def start_server():
    print("Starting server...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 5050))
    s.listen(5)
    print("Server is listening on port 5050...")

    while True:
        client_socket, addr = s.accept()
        print(f"Connection from {addr} has been established.")
        handle_client_request(client_socket)


if __name__ == "__main__":
    start_server()
