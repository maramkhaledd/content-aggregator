import socket
import pickle
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from datetime import datetime
import webbrowser
import re


class NewsAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News Content Aggregator")
        self.root.geometry("1000x800")
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.preset_domains = ["bbc.com", "cnn.com", "theguardian.com"]

        # Colors
        self.bg_color = "#f8f9fa"
        self.accent_color = "#4a90e2"
        self.text_color = "#2c3e50"
        self.link_color = "#3498db"
        self.button_color = "#4a90e2"
        self.button_hover = "#357abd"
        self.success_color = "#2ecc71"
        self.error_color = "#e74c3c"

        # Configure styles
        self.style.configure("Custom.TFrame", background=self.bg_color)
        self.style.configure("Custom.TLabel", background=self.bg_color, font=("Helvetica", 12), foreground=self.text_color)
        self.style.configure("Title.TLabel", background=self.bg_color, font=("Helvetica", 24, "bold"), foreground=self.accent_color)
        self.style.configure("Subtitle.TLabel", background=self.bg_color, font=("Helvetica", 14), foreground=self.text_color)
        self.style.configure("Custom.TButton", font=("Helvetica", 12, "bold"), background=self.button_color, foreground="white", padding=10)
        self.style.map("Custom.TButton", background=[("active", self.button_hover)], foreground=[("active", "white")])

        self.root.configure(bg=self.bg_color)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=40, pady=40)

        # Homepage tab - UPDATED to show latest news list, no keyword search
        self.homepage_frame = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.homepage_frame, text="🏠 Homepage")

        self.home_title = ttk.Label(self.homepage_frame, text="🏡 Welcome to News Aggregator", style="Title.TLabel")
        self.home_title.pack(pady=(20, 10))

        self.home_subtitle = ttk.Label(
            self.homepage_frame,
            text="Here are the latest trending news from top sources:",
            style="Subtitle.TLabel",
            wraplength=800,
            justify="center"
        )
        self.home_subtitle.pack(pady=(0, 20))

        # Text widget + scrollbar for homepage news display
        self.home_news_frame = ttk.Frame(self.homepage_frame, style="Custom.TFrame")
        self.home_news_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.home_news_text = tk.Text(
            self.home_news_frame,
            font=("Helvetica", 12),
            bg="white",
            fg=self.text_color,
            wrap=tk.WORD,
            padx=20,
            pady=20,
            relief=tk.FLAT,
            height=25,
            cursor="arrow"
        )
        self.home_news_text.pack(side=tk.LEFT, fill="both", expand=True)

        self.home_news_text.tag_configure("link", foreground=self.link_color, underline=1)
        self.home_news_text.tag_configure("title", font=("Helvetica", 13, "bold"), foreground=self.accent_color)
        self.home_news_text.tag_bind("link", "<Button-1>", self.open_home_link)
        self.home_news_text.tag_bind("link", "<Enter>", lambda e: self.home_news_text.config(cursor="hand2"))
        self.home_news_text.tag_bind("link", "<Leave>", lambda e: self.home_news_text.config(cursor="arrow"))

        self.home_scrollbar = ttk.Scrollbar(self.home_news_frame, orient="vertical", command=self.home_news_text.yview)
        self.home_news_text.configure(yscrollcommand=self.home_scrollbar.set)
        self.home_scrollbar.pack(side=tk.RIGHT, fill="y")

        # Dictionary for homepage links by line number
        self.home_links = {}

        # Search tab (unchanged)
        self.search_frame = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.search_frame, text="🔎 Search")

        # Create query frame
        self.query_frame = ttk.Frame(self.search_frame, style="Custom.TFrame")
        self.query_frame.pack(fill="both", expand=True)

        self.title_label = ttk.Label(self.query_frame, text="📰 News Content Aggregator", style="Title.TLabel")
        self.title_label.pack(pady=(0, 30))

        self.instructions = ttk.Label(
            self.query_frame,
            text="Enter website domains (one per line):",
            style="Subtitle.TLabel",
        )
        self.instructions.pack(pady=(0, 15))

        # --- ADD BUTTONS FRAME ---
        self.button_frame = ttk.Frame(self.query_frame, style="Custom.TFrame")
        self.button_frame.pack(pady=(0, 15))  # space below buttons

        for domain in self.preset_domains:
            button = tk.Button(
                self.button_frame,
                text=domain,
                font=("Helvetica", 12, "bold"),
                bg="#e3f2fd",
                fg="#0d47a1",
                relief="flat",
                bd=0,
                padx=15,
                pady=6,
                cursor="hand2",
                highlightbackground="#bbdefb",
                highlightthickness=1,
                command=lambda d=domain: self.insert_domain(d)
            )
            button.pack(side=tk.LEFT, padx=5)

        # The existing text input frame and text widget follows
        self.text_frame = ttk.Frame(self.query_frame, style="Custom.TFrame")
        self.text_frame.pack(fill="both", expand=True, pady=15)

        self.text = tk.Text(
            self.text_frame,
            width=60,
            height=10,
            font=("Helvetica", 12),
            wrap=tk.WORD,
            bg="white",
            fg=self.text_color,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            highlightthickness=1,
            highlightbackground="#e0e0e0",
            highlightcolor=self.accent_color,
        )
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        self.text.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self.submit_button = ttk.Button(self.query_frame, text="🔍 Fetch Articles", command=self.submit_domains, style="Custom.TButton")
        self.submit_button.pack(pady=25)

        # Create articles frame
        self.articles_frame = ttk.Frame(self.search_frame, style="Custom.TFrame")

        self.articles_title = ttk.Label(self.articles_frame, text="📋 Fetched Articles", style="Title.TLabel")
        self.articles_title.pack(pady=(0, 30))

        self.list_frame = ttk.Frame(self.articles_frame, style="Custom.TFrame")
        self.list_frame.pack(fill="both", expand=True, pady=15)

        self.articles_text = tk.Text(
            self.list_frame,
            font=("Helvetica", 12),
            bg="white",
            fg=self.text_color,
            wrap=tk.WORD,
            cursor="arrow",
            padx=20,
            pady=20,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#e0e0e0",
            highlightcolor=self.accent_color,
        )
        
        self.articles_text.tag_configure("link", foreground=self.link_color, underline=1, font=("Helvetica", 12))
        self.articles_text.tag_configure("title", font=("Helvetica", 13, "bold"), foreground=self.accent_color)
        self.articles_text.tag_bind("link", "<Button-1>", self.open_link)
        self.articles_text.tag_bind("link", "<Enter>", lambda e: self.articles_text.config(cursor="hand2"))
        self.articles_text.tag_bind("link", "<Leave>", lambda e: self.articles_text.config(cursor="arrow"))

        self.list_scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.articles_text.yview)
        self.articles_text.configure(yscrollcommand=self.list_scrollbar.set)

        self.articles_text.pack(side=tk.LEFT, fill="both", expand=True)
        self.list_scrollbar.pack(side=tk.RIGHT, fill="y")

        self.back_button = ttk.Button(
            self.articles_frame,
            text="← Back to Search",
            command=self.reset_to_query,
            style="Custom.TButton",
        )
        self.back_button.pack(pady=25)

        self.loading_label = ttk.Label(self.query_frame, text="", style="Subtitle.TLabel")
        self.loading_label.pack(pady=15)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            root,
            textvariable=self.status_var,
            style="Custom.TLabel",
            relief=tk.FLAT,
            anchor=tk.W,
            padding=(10, 5),
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.links = {}

        # Fetch latest news for homepage at startup
        self.load_latest_news_on_homepage()

    def insert_domain(self, domain):
        # Clear existing text and insert the clicked domain
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, domain + "\n")

    def open_home_link(self, event):
        index = self.home_news_text.index(f"@{event.x},{event.y}")
        line = int(float(index))
        if line in self.home_links:
            webbrowser.open(self.home_links[line])
            self.status_var.set(f"Opening: {self.home_links[line]}")

    def load_latest_news_on_homepage(self):
        news_domains = [
            "bbc.com/news",
            "cnn.com",
            "reuters.com",
            "nytimes.com",
            "theguardian.com/international"
        ]

        def fetch():
            try:
                serialized_domains = pickle.dumps(news_domains)
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(("localhost", 5050))

                client_socket.sendall(len(serialized_domains).to_bytes(4, "big"))
                client_socket.sendall(serialized_domains)

                response_length_bytes = client_socket.recv(4)
                response_length = int.from_bytes(response_length_bytes, "big")
                data = b""
                while len(data) < response_length:
                    data += client_socket.recv(min(4096, response_length - len(data)))

                articles = pickle.loads(data)
                self.root.after(0, lambda: self.display_homepage_news(articles))
            except Exception as e:
                self.root.after(0, lambda: self.home_news_text.insert(tk.END, f"Failed to load latest news: {e}"))
            finally:
                client_socket.close()

        threading.Thread(target=fetch, daemon=True).start()

    def display_homepage_news(self, articles):
        self.home_news_text.delete("1.0", tk.END)
        self.home_links.clear()

        if not articles:
            self.home_news_text.insert(tk.END, "No latest news found.", "title")
            return

        for idx, (title, link) in enumerate(articles, start=1):
            self.home_news_text.insert(tk.END, f"{idx}. {title}\n", "title")
            if link and link != "No link available":
                line = int(self.home_news_text.index("end-1c").split(".")[0])
                self.home_links[line] = link
                self.home_news_text.insert(tk.END, f"    🔗 {link}\n", "link")
            else:
                self.home_news_text.insert(tk.END, "    ❌ No link available\n")
            self.home_news_text.insert(tk.END, "\n")

    def submit_domains(self):
        domains_input = self.text.get("1.0", tk.END).strip()
        if not domains_input:
            messagebox.showwarning("Input needed", "Please enter one or more website domains.")
            return

        domains = [line.strip() for line in domains_input.splitlines() if line.strip()]
        # Simple domain validation
        domain_pattern = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
        for d in domains:
            if not domain_pattern.match(d):
                messagebox.showerror("Invalid domain", f"The domain '{d}' is not valid.")
                return

        self.loading_label.config(text="Loading articles...")
        self.status_var.set("Fetching articles...")
        self.submit_button.config(state=tk.DISABLED)

        threading.Thread(target=self.fetch_articles_thread, args=(domains,), daemon=True).start()

    def fetch_articles_thread(self, domains):
        try:
            serialized_domains = pickle.dumps(domains)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", 5050))

            client_socket.sendall(len(serialized_domains).to_bytes(4, "big"))
            client_socket.sendall(serialized_domains)

            response_length_bytes = client_socket.recv(4)
            response_length = int.from_bytes(response_length_bytes, "big")
            data = b""
            while len(data) < response_length:
                data += client_socket.recv(min(4096, response_length - len(data)))

            articles = pickle.loads(data)
            self.root.after(0, lambda: self.display_articles(articles))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch articles: {e}"))
            self.root.after(0, self.reset_to_query)
        finally:
            client_socket.close()

    def display_articles(self, articles):
        self.query_frame.pack_forget()
        self.articles_frame.pack(fill="both", expand=True)

        self.articles_text.delete("1.0", tk.END)
        self.links.clear()

        if not articles:
            self.articles_text.insert(tk.END, "No articles found for the given domains.", "title")
            return

        for idx, (title, link) in enumerate(articles, start=1):
            self.articles_text.insert(tk.END, f"{idx}. {title}\n", "title")
            if link and link != "No link available":
                line = int(self.articles_text.index("end-1c").split(".")[0])
                self.links[line] = link
                self.articles_text.insert(tk.END, f"    🔗 {link}\n", "link")
            else:
                self.articles_text.insert(tk.END, "    ❌ No link available\n")
            self.articles_text.insert(tk.END, "\n")

        self.loading_label.config(text="")
        self.status_var.set("Ready")
        self.submit_button.config(state=tk.NORMAL)

    def reset_to_query(self):
        self.articles_frame.pack_forget()
        self.query_frame.pack(fill="both", expand=True)
        self.status_var.set("Ready")
        self.loading_label.config(text="")
        self.submit_button.config(state=tk.NORMAL)

    def open_link(self, event):
        index = self.articles_text.index(f"@{event.x},{event.y}")
        line = int(float(index))
        if line in self.links:
            webbrowser.open(self.links[line])
            self.status_var.set(f"Opening: {self.links[line]}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsAggregatorApp(root)
    root.mainloop()
