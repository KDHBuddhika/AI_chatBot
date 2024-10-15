import tkinter as tk
from tkinter import scrolledtext, PhotoImage
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime

# Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",     # Replace with your MySQL server host
    user="root",          # Replace with your MySQL username
    password="Mysql119",  # Replace with your MySQL password
    database="chatbot_db" # Replace with your MySQL database name
)
cursor = conn.cursor()

# Ensure chatbot training table exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS chatbot_training (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) UNIQUE,
    response VARCHAR(255)
)
''')
conn.commit()

# Chatbot response logic
def chatbot_response(user_input):
    user_input = user_input.lower()

    # Check if the user input is a known question in the database
    cursor.execute("SELECT response FROM chatbot_training WHERE question = %s", (user_input,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Return the response from the database
    else:
        return "Sorry, I don't understand that. Please ask something else or use 'train' mode to teach me."

# Function to train the chatbot
def train_chatbot(question, response):
    try:
        cursor.execute("INSERT INTO chatbot_training (question, response) VALUES (%s, %s)", (question, response))
        conn.commit()
        return "Training successful! I have learned something new."
    except mysql.connector.IntegrityError:
        return "I already know the answer to that question."

# Function to handle user input and chatbot response
def handle_user_input():
    user_input = entry.get().strip().lower()
    
    if user_input == "":
        return

    if mode.get() == "Chat":
        # Chat Mode
        response = chatbot_response(user_input)
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, "You: " + user_input + "\n", "user")
        chat_window.insert(tk.END, "ChatBot: " + response + "\n\n", "bot")
        chat_window.yview(tk.END)

    elif mode.get() == "Train":
        # Train Mode
        question = entry_question.get().strip().lower()
        response = entry_response.get().strip()
        if question and response:
            result = train_chatbot(question, response)
            chat_window.config(state=tk.NORMAL)
            chat_window.insert(tk.END, result + "\n\n")
            chat_window.yview(tk.END)
        else:
            chat_window.config(state=tk.NORMAL)
            chat_window.insert(tk.END, "Please provide both a question and a response.\n\n")
            chat_window.yview(tk.END)

    # Clear input fields
    entry.delete(0, tk.END)
    entry_question.delete(0, tk.END)
    entry_response.delete(0, tk.END)

# Function to retrieve and display the chat history
def show_history():
    chat_window.config(state=tk.NORMAL)
    chat_window.delete(1.0, tk.END)  # Clear the current chat window

    # Fetch chat history from the MySQL database
    cursor.execute('SELECT user_input, bot_response, timestamp FROM chat_history ORDER BY id')
    rows = cursor.fetchall()

    # Display the chat history
    for row in rows:
        user_input, bot_response, timestamp = row
        chat_window.insert(tk.END, f"{timestamp}\nYou: {user_input}\nChatBot: {bot_response}\n\n")

    chat_window.config(state=tk.DISABLED)

# Setting up the GUI with Tkinter
root = tk.Tk()
root.title("KAPRUKA")

# Set window icon
try:
    icon_img = Image.open("images.jpeg")  # Replace with the patho your icon
    icon = ImageTk.PhotoImage(icon_img)
    root.iconphoto(True, icon)
except Exception as e:
    messagebox.showerror("Error", "Could not load icon image.")

# Add a header image (logo or icon)
try:
    header_path = "C:/Users/asus/Desktop/python Ai/.venv/chatbot/ChatbotDatabase/Kapruka-H-Logo.jpg"  # Replace with your header image path
    header_img = Image.open(header_path)
    header_img = header_img.resize((100, 100), Image.Resampling.LANCZOS)  # Replace ANTIALIAS with Resampling.LANCZOS
    header_photo = ImageTk.PhotoImage(header_img)
    header_label = tk.Label(root, image=header_photo, bg='#ADD8E6')
    header_label.pack(pady=10)
except Exception as e:
    messagebox.showerror("Error", f"Could not load header image: {e}")

# Set background colors
root.configure(bg='#ffffff')  # White background

# Set geometry (size of the window)
root.geometry("600x700")  # Adjusted the size to better fit the screen

# Make the window resizable
root.resizable(True, True)

# Font configurations
label_font = ("Arial", 14, "bold")
entry_font = ("Arial", 12)
button_font = ("Arial", 12, "bold")

# Create a chat display window (ScrolledText widget)
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, bg='#F0F8FF', fg='black', font=entry_font, bd=2, relief=tk.SUNKEN)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Dropdown to select mode (Chat or Train)
mode = tk.StringVar(value="Chat")
tk.Label(root, text="Mode:", bg='#ADD8E6', font=label_font).pack()
mode_menu = tk.OptionMenu(root, mode, "Chat", "Train")
mode_menu.config(font=label_font, bg='#20B2AA', fg='white')  # Styling the dropdown menu
mode_menu.pack(pady=5)

# Entry field for user input in Chat mode
entry = tk.Entry(root, font=entry_font, bd=2, relief=tk.SUNKEN)
entry.pack(padx=10, pady=5, fill=tk.X)

# For Train mode: entries for question and response
train_frame = tk.Frame(root, bg='#ADD8E6')  # Set background color for train frame
tk.Label(train_frame, text="Question (for training):", bg='#ADD8E6', font=label_font).pack(anchor="w")
entry_question = tk.Entry(train_frame, font=entry_font, bd=2, relief=tk.SUNKEN)
entry_question.pack(padx=10, pady=5, fill=tk.X)

tk.Label(train_frame, text="Response (for training):", bg='#ADD8E6', font=label_font).pack(anchor="w")
entry_response = tk.Entry(train_frame, font=entry_font, bd=2, relief=tk.SUNKEN)
entry_response.pack(padx=10, pady=5, fill=tk.X)

train_frame.pack(padx=10, pady=10, fill=tk.X)

# Create a button to submit user input or train chatbot
submit_button = tk.Button(root, text="Send", command=handle_user_input, font=button_font, bg='#20B2AA', fg='white', bd=2, relief=tk.RAISED)
submit_button.pack(pady=5)

# Create a button to view chat history
history_button = tk.Button(root, text="View History", command=show_history, font=button_font, bg='#20B2AA', fg='white', bd=2, relief=tk.RAISED)
history_button.pack(pady=5)

# Allow pressing 'Enter' to submit the input
entry.bind("<Return>", lambda event: handle_user_input())

# Text styling for chat
chat_window.tag_config("user", foreground="blue", font=("Arial", 12, "bold"))
chat_window.tag_config("bot", foreground="green", font=("Arial", 12))

# Run the Tkinter event loop
root.mainloop()

# Close the MySQL connection when the application exits
conn.close()
