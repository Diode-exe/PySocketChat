#!/usr/bin/env python3

import socket
import threading
import logging
from datetime import datetime

from tkinter import *
from tkinter import ttk, scrolledtext, messagebox

from config import Settings

'''
    Main process that start client connection to the server 
    and handle it's input messages
'''
class Client:
    clientSocket: socket.socket = None # Client's Socket.

    def __init__(self, root: Tk) -> None:
        '''
            Initializes the Client and creates its GUI.
        '''

        try:
            logging.basicConfig(level=logging.NOTSET, format='[CLIENT - %(levelname)s] %(message)s') # Initialize Logging.

            # Connects the Client to the Server.
            self.clientSocket = socket.socket()
            self.clientSocket.connect((Settings.SERVER_ADDRESS, Settings.SERVER_PORT))

            # Create the GUI Window.
            # Set it not resizable and the action on close button pressed.
            self.root = root
            self.root.title(Settings.SERVER_NAME)

            # Create the Message Box.
            self.mainWindow = ttk.Frame(self.root, padding=10)
            self.mainWindow.grid(row=0, column=0, columnspan=2, sticky=(N, S, E, W))

            # Create the Users Message Area.
            self.messageArea = scrolledtext.ScrolledText(self.mainWindow, wrap='word', state='disabled')
            self.messageArea.grid(row=0, column=0, columnspan=2, sticky=(N, S, E, W))

            # Create the Message Entry.
            self.inputArea = ttk.Entry(self.mainWindow, width=50)
            self.inputArea.grid(row=1, column=0, sticky=(E, W))
            self.inputArea.bind('<Return>', self.sendMessage)

            # Create the Send Message.
            self.sendButton = ttk.Button(self.mainWindow, text="Send", command=self.sendMessage)
            self.sendButton.grid(row=1, column=1, sticky=(E, W))

            self.root.resizable(False, False)
            self.root.protocol("WM_DELETE_WINDOW", self.closeConnection)

            # Starts the manageMessage thread.
            threading.Thread(target=self.manageMessage, args=[self.clientSocket], daemon=True).start()

            logging.info('Connected to chat')

        except Exception as e:
            logging.error(f'Error connecting to server socket: {e}', exc_info=Settings.EXCEPTIONS_INFO)
            messagebox.showerror("Error", f'Error connecting to server socket: {e}')
            self.clientSocket.close()
            root.destroy()

    def getCurrentTime(self):
        '''
            Get current time formatted for messages.
        '''
        current_time = datetime.now()
        return current_time.strftime("%I:%M:%S %p")  # 03:30:45 PM

    def manageMessage(self, connection: socket.socket):
        '''
            Retrieve messages from the server.
        '''
        
        # Message Management infinite loop.
        while True:
            try:
                msg = connection.recv(Settings.BUFFER_SIZE)
                if msg:
                    self.displayMessage(msg.decode(Settings.MESSAGE_ENCODING))
                else:
                    connection.close()
                    break
            except Exception as e:
                logging.error(f'Error handling message from server: {e}', exc_info=Settings.EXCEPTIONS_INFO)
                messagebox.showerror("Error", f'Error handling message from server: {e}')
                connection.close()
                break

    def displayMessage(self, msg: str):
        '''
            Display received messages to the client's GUI.
        '''
        
        # Add the message to the text area.
        self.messageArea.configure(state='normal')
        self.messageArea.insert(END, msg + '\n')
        self.messageArea.configure(state='disabled')
        self.messageArea.yview(END)

    def sendMessage(self, event=None):
        '''
            Send message to the server with timestamp.
        '''
        
        # Get the message entry
        user_message = self.inputArea.get().strip()
        
        if not user_message:
            return
            
        try:
            # Create timestamped message
            timestamp = self.getCurrentTime()
            # Format: [timestamp] user_message
            timestamped_message = f"[{timestamp}] {user_message}"
            
            # Send the timestamped message to server
            self.clientSocket.send(timestamped_message.encode(Settings.MESSAGE_ENCODING))
            
            # Clear input field
            self.inputArea.delete(0, END)

            self.displayMessage(timestamped_message)
            
        except Exception as e:
            logging.error(f'Error occurred when sending message: {e}', exc_info=Settings.EXCEPTIONS_INFO)
            messagebox.showerror("Error", f'Error occurred when sending message: {e}')

    def closeConnection(self, event: None = None):
        '''
            Close client's connection to the server.
        '''
        
        try:
            self.clientSocket.close()
        except Exception as e:
            logging.error(f'Error occurred while closing socket: {e}', exc_info=Settings.EXCEPTIONS_INFO)
            messagebox.showerror("Error", f'Error occurred while closing socket: {e}')

        self.root.quit()

    @staticmethod
    def startClientGUI():
        '''
            Starts the client's GUI.
        '''
            
        root = Tk()
        Client(root)
        root.mainloop()

if __name__ == "__main__":
    Client.startClientGUI()