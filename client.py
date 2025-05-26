import socket
import pickle  #Pickle is a Python module used for serializing and deserializing Python object structures.
import tkinter as tk
from tkinter import messagebox


#def submit_domains:

#triggered when user clicks "Back" button
def reset_to_query():
  articles_list.delete(0,tk.END) #Clear the articles list; 0-> index of first item, tk.END-> index of last item
  text.delete("1.0", tk.END) #Clear input text
  articles_frame.pack_forget() #hide articles display frame.
  query_frame.pack(fill="both", expand=True) #make the query_frame visible again


  
   







root=tk.TK()  #initialize tkinter app (create main window) 
root.configure(bg="maroon") #set background color of main window
root.title("News Content Aggregator")
root.geometry("700x500") #sets size of main window

#create frame for querying 
query_frame = tk.Frame(root, bg="maroon") #frame widget: a container to hold other widgets
query_frame.pack(fill="both", expand=True)
#create widgets for frame 
label = tk.Label(query_frame, text="Enter Website Domains (One Per Line):", bg="maroon", fg="white", font=("Arial", 12, "bold"))
label.place(x=202, y=100)  #uses absolute positioning (instead of layout managers like pack() or grid())
text = tk.Text(query_frame, width=60, height=10) #width in chars, height in lines
text.place(x=100, y=175)
submit_button = tk.Button(query_frame, text="Submit", command=submit_domains, font=("Arial", 10), bg="white")
submit_button.place(x=320, y=410)

#create another frame to display news articles
articles_frame = tk.Frame(root, bg="maroon")
#widgets:
#Listbox widget: show a list of articles (like a scrollable list)
articles_list = tk.Listbox(articles_frame, font=("Arial", 12), width=70, height=20, bg="maroon", fg="white")
articles_list.place(x=30, y=30)
#back button widget
back_button = tk.Button(articles_frame, text="Back", command=reset_to_query, font=("Arial", 10), bg="white")
back_button.place(x=320, y=430)

#start main loop of GUI; keeps the application running and waits for user interactions
root.mainloop()