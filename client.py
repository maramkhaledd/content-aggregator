import socket
import pickle
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from datetime import datetime
import webbrowser
import re

print("Client started")


class NewsAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News Content Aggregator")
        self.root.geometry("1000x800")

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme as base

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
        self.style.configure("Custom.TLabel",
                             background=self.bg_color,
                             font=("Helvetica", 12),
                             foreground=self.text_color)
        self.style.configure("Title.TLabel",
                             background=self.bg_color,
                             font=("Helvetica", 24, "bold"),
                             foreground=self.accent_color)
        self.style.configure("Subtitle.TLabel",
                             background=self.bg_color,
                             font=("Helvetica", 14),
                             foreground=self.text_color)
        self.style.configure("Custom.TButton",
                             font=("Helvetica", 12, "bold"),
                             background=self.button_color,
                             foreground="white",
                             padding=10)
        self.style.map("Custom.TButton",
                       background=[("active", self.button_hover)],
                       foreground=[("active", "white")])

        # Configure root
        self.root.configure(bg=self.bg_color)

        # Create main container with padding
        self.main_container = ttk.Frame(root, style="Custom.TFrame")
        self.main_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Create query frame
        self.query_frame = ttk.Frame(
            self.main_container, style="Custom.TFrame")
        self.query_frame.pack(fill="both", expand=True)

        # Title with icon
        self.title_label = ttk.Label(
            self.query_frame,
            text="📰 News Content Aggregator",
            style="Title.TLabel"
        )
        self.title_label.pack(pady=(0, 30))

        # Instructions with better formatting
        self.instructions = ttk.Label(
            self.query_frame,
            text="Enter website domains (one per line):",
            style="Subtitle.TLabel"
        )
        self.instructions.pack(pady=(0, 15))

        # Text area with modern styling
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
            highlightcolor=self.accent_color
        )
        self.scrollbar = ttk.Scrollbar(
            self.text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        self.text.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        # Submit button with modern styling
        self.submit_button = ttk.Button(
            self.query_frame,
            text="🔍 Fetch Articles",
            command=self.submit_domains,
            style="Custom.TButton"
        )
        self.submit_button.pack(pady=25)

        # Create articles frame
        self.articles_frame = ttk.Frame(
            self.main_container, style="Custom.TFrame")

        # Articles title with icon
        self.articles_title = ttk.Label(
            self.articles_frame,
            text="📋 Fetched Articles",
            style="Title.TLabel"
        )
        self.articles_title.pack(pady=(0, 30))

        # Articles list with modern styling
        self.list_frame = ttk.Frame(self.articles_frame, style="Custom.TFrame")
        self.list_frame.pack(fill="both", expand=True, pady=15)

        # Create a Text widget with modern styling
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
            highlightcolor=self.accent_color
        )
        self.articles_text.tag_configure("link",
                                         foreground=self.link_color,
                                         underline=1,
                                         font=("Helvetica", 12))
        self.articles_text.tag_configure("title",
                                         font=("Helvetica", 13, "bold"),
                                         foreground=self.accent_color)
        self.articles_text.tag_bind("link", "<Button-1>", self.open_link)
        self.articles_text.tag_bind(
            "link", "<Enter>", lambda e: self.articles_text.config(cursor="hand2"))
        self.articles_text.tag_bind(
            "link", "<Leave>", lambda e: self.articles_text.config(cursor="arrow"))

        self.list_scrollbar = ttk.Scrollbar(
            self.list_frame, orient="vertical", command=self.articles_text.yview)
        self.articles_text.configure(yscrollcommand=self.list_scrollbar.set)

        self.articles_text.pack(side=tk.LEFT, fill="both", expand=True)
        self.list_scrollbar.pack(side=tk.RIGHT, fill="y")

        # Back button with modern styling
        self.back_button = ttk.Button(
            self.articles_frame,
            text="← Back to Search",
            command=self.reset_to_query,
            style="Custom.TButton"
        )
        self.back_button.pack(pady=25)

        # Loading indicator with modern styling
        self.loading_label = ttk.Label(
            self.query_frame,
            text="",
            style="Subtitle.TLabel"
        )
        self.loading_label.pack(pady=15)

        # Status bar with modern styling
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            root,
            textvariable=self.status_var,
            style="Custom.TLabel",
            relief=tk.FLAT,
            anchor=tk.W,
            padding=(10, 5)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Store links for reference
        self.links = {}

    def open_link(self, event):
        index = self.articles_text.index(f"@{event.x},{event.y}")
        line = int(float(index))
        if line in self.links:
            webbrowser.open(self.links[line])
            self.status_var.set(f"Opening: {self.links[line]}")

    def submit_domains(self):
        domains = self.text.get("1.0", tk.END).strip().splitlines()

        if not domains:
            messagebox.showerror("Error", "Please enter at least one domain.")
            return

        self.submit_button.configure(state="disabled")
        self.loading_label.configure(text="⏳ Fetching articles...")
        self.status_var.set("Connecting to server...")
        self.root.update()

        threading.Thread(target=self.fetch_articles,
                         args=(domains,), daemon=True).start()

    def fetch_articles(self, domains):
        try:
            serialized_domains = pickle.dumps(domains)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 5050))

            self.status_var.set("Sending request...")
            data_length = len(serialized_domains)
            client_socket.sendall(data_length.to_bytes(4, 'big'))
            client_socket.sendall(serialized_domains)

            self.status_var.set("Receiving data...")
            data_length_bytes = client_socket.recv(4)
            data_length = int.from_bytes(data_length_bytes, 'big')
            data = b""
            while len(data) < data_length:
                data += client_socket.recv(min(4096, data_length - len(data)))

            response = pickle.loads(data)
            self.root.after(0, lambda: self.show_articles(response))

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(
                0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
        finally:
            client_socket.close()
            self.root.after(0, self.reset_loading_state)

    def reset_loading_state(self):
        self.submit_button.configure(state="normal")
        self.loading_label.configure(text="")
        self.status_var.set("Ready")

    def show_articles(self, articles):
        self.query_frame.pack_forget()
        self.articles_frame.pack(fill="both", expand=True)

        self.articles_text.delete("1.0", tk.END)
        self.links.clear()

        if not articles:
            self.articles_text.insert(tk.END, "No articles found.", "title")
            return

        for idx, (title, link) in enumerate(articles, start=1):
            # Insert title with custom styling
            self.articles_text.insert(tk.END, f"{idx}. {title}\n", "title")

            # Insert link if available
            if link and link != "No link available":
                line = int(self.articles_text.index("end-1c").split('.')[0])
                self.links[line] = link
                self.articles_text.insert(
                    tk.END, f"    🔗 Link: {link}\n", "link")
            else:
                self.articles_text.insert(tk.END, "    ❌ No link available\n")

            # Add spacing
            self.articles_text.insert(tk.END, "\n")

        self.status_var.set(f"✅ Found {len(articles)} articles")

    def reset_to_query(self):
        self.articles_text.delete("1.0", tk.END)
        self.text.delete("1.0", tk.END)
        self.articles_frame.pack_forget()
        self.query_frame.pack(fill="both", expand=True)
        self.status_var.set("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsAggregatorApp(root)
    root.mainloop()
