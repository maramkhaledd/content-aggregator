import socket
import pickle  # Pickle is a Python module used for serializing and deserializing Python object structures.
import tkinter as tk
from tkinter import messagebox

print("Client started")

#def show_articles(articles):
"""
 This function displays the articles in the articles list.
 """
    


# triggered when user clicks "Submit" button
def submit_domains():
    """
    This function is triggered when the user clicks the "Submit" button.
    It retrieves the domains from the text input, serializes them, and sends them to the server.
    """
    domains = text.get("1.0", tk.END).strip().splitlines()
    if not domains:
        messagebox.showerror("Error", "Please enter at least one domain.")
        return
    # Use pickle to convert list of domains into binary format(bytes).
    serialized_domains = pickle.dumps(domains)
    client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5050))
    #Gets the number of bytes in the serialized domain list.
    data_length = len(serialized_domains)
    #Send the length of the serialized domain list to the server.
    client_socket.sendall(data_length.to_bytes(4, byteorder="big"))
    #Send the serialized domain list to the server. 
    client_socket.sendall(serialized_domains)
    # Wait to receive 4 bytes from the server(length of response)
    data_length_bytes = client_socket.recv(4)
    # Convert the 4 bytes to an integer.
    data_length = int.from_bytes(data_length_bytes, 'big')
    #Initialize empty bytes object to hold incoming data
    data = b""
    while len(data) < data_length:
        data += client_socket.recv(min(4096, data_length - len(data)))
    try:
        #Deserialize the response
        response = pickle.loads(data)
        print(response)
        show_articles(response)
    except Exception as e:
        print(f"Error during deserialization: {e}")
        messagebox.showerror("Error", "Failed to retrieve articles from server.")
    client_socket.close()

# triggered when user clicks "Back" button
def reset_to_query():
    articles_list.delete(
        0, tk.END
    )  # Clear the articles list; 0-> index of first item, tk.END-> index of last item
    text.delete("1.0", tk.END)  # Clear input text
    articles_frame.pack_forget()  # hide articles display frame.
    query_frame.pack(fill="both", expand=True)  # make the query_frame visible again


root = tk.TK()  # initialize tkinter app (create main window)
root.configure(bg="maroon")  # set background color of main window
root.title("News Content Aggregator")
root.geometry("700x500")  # sets size of main window

# create frame for querying
query_frame = tk.Frame(
    root, bg="maroon"
)  # frame widget: a container to hold other widgets
query_frame.pack(fill="both", expand=True)
# create widgets for frame
label = tk.Label(
    query_frame,
    text="Enter Website Domains (One Per Line):",
    bg="maroon",
    fg="white",
    font=("Arial", 12, "bold"),
)
label.place(
    x=202, y=100
)  # uses absolute positioning (instead of layout managers like pack() or grid())
text = tk.Text(query_frame, width=60, height=10)  # width in chars, height in lines
text.place(x=100, y=175)
submit_button = tk.Button(
    query_frame, text="Submit", command=submit_domains, font=("Arial", 10), bg="white"
)
submit_button.place(x=320, y=410)

# create another frame to display news articles
articles_frame = tk.Frame(root, bg="maroon")
# widgets:
# Listbox widget: show a list of articles (like a scrollable list)
articles_list = tk.Listbox(
    articles_frame, font=("Arial", 12), width=70, height=20, bg="maroon", fg="white"
)
articles_list.place(x=30, y=30)
# back button widget
back_button = tk.Button(
    articles_frame, text="Back", command=reset_to_query, font=("Arial", 10), bg="white"
)
back_button.place(x=320, y=430)

# start main loop of GUI; keeps the application running and waits for user interactions
root.mainloop()
