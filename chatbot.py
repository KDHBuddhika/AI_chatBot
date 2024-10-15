import tkinter as tk
from tkinter import scrolledtext
import mysql.connector
from datetime import datetime


conn = mysql.connector.connect(
    host="localhost",     
    user="root",         
    password="Mysql119",  
    database="chatbot_db" 
)
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS chatbot_training (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) UNIQUE,
    response VARCHAR(255)
)
''')
conn.commit()


def chatbot_response(user_input):
    user_input = user_input.lower()


    cursor.execute("SELECT response FROM chatbot_training WHERE question = %s", (user_input,))
    result = cursor.fetchone()

    if result:
        return result[0]  
    else:
        return "Sorry, I don't understand that. Please ask something else or use 'train' mode to teach me."


def train_chatbot(question, response):
    try:
        cursor.execute("INSERT INTO chatbot_training (question, response) VALUES (%s, %s)", (question, response))
        conn.commit()
        return "Training successful! I have learned something new."
    except mysql.connector.IntegrityError:
        return "I already know the answer to that question."


def handle_user_input():
    user_input = entry.get().strip().lower()
    
    if user_input == "":
        return

    if mode.get() == "Chat":
       
        response = chatbot_response(user_input)
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, "You: " + user_input + "\n")
        chat_window.insert(tk.END, "ChatBot: " + response + "\n\n")
        chat_window.yview(tk.END)

    elif mode.get() == "Train":
       
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

  
    entry.delete(0, tk.END)
    entry_question.delete(0, tk.END)
    entry_response.delete(0, tk.END)


def show_history():
    chat_window.config(state=tk.NORMAL)
    chat_window.delete(1.0, tk.END)  

    cursor.execute('SELECT user_input, bot_response, timestamp FROM chat_history ORDER BY id')
    rows = cursor.fetchall()

    for row in rows:
        user_input, bot_response, timestamp = row
        chat_window.insert(tk.END, f"{timestamp}\nYou: {user_input}\nChatBot: {bot_response}\n\n")

    chat_window.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Trainable ChatBot with MySQL")
root.geometry("600x700")

chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)


mode = tk.StringVar(value="Chat")
tk.Label(root, text="Mode:").pack()
mode_menu = tk.OptionMenu(root, mode, "Chat", "Train")
mode_menu.pack(pady=5)

entry = tk.Entry(root, font=("Arial", 12))
entry.pack(padx=10, pady=5, fill=tk.X)

train_frame = tk.Frame(root)
tk.Label(train_frame, text="Question (for training):").pack(anchor="w")
entry_question = tk.Entry(train_frame, font=("Arial", 12))
entry_question.pack(padx=10, pady=5, fill=tk.X)

tk.Label(train_frame, text="Response (for training):").pack(anchor="w")
entry_response = tk.Entry(train_frame, font=("Arial", 12))
entry_response.pack(padx=10, pady=5, fill=tk.X)

train_frame.pack(padx=10, pady=10, fill=tk.X)

submit_button = tk.Button(root, text="Send", command=handle_user_input)
submit_button.pack(pady=5)

history_button = tk.Button(root, text="View History", command=show_history)
history_button.pack(pady=5)

entry.bind("<Return>", lambda event: handle_user_input())

root.mainloop()

conn.close()
