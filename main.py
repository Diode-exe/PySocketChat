#!/usr/bin/env python3

"""
    Track 1: Client-Server Chat System.

    Implement a client-server chat system in Python
    using socket programming.
    The server must be able to handle multiple clients simultaneously
    and must allow users to send
    and receive messages in a shared chatroom.
    The client must allow users to connect to the server,
    send messages to the chatroom,
    and receive messages from other users.
"""

import threading
from time import sleep

from client import Client
from server import Server
from config import Settings

if __name__ == "__main__":    
    # Checks if some settings values are wrong and corrects them.
    if Settings.NUMBER_OF_CLIENTS == 0:
        pass
    elif Settings.NUMBER_OF_CLIENTS < 2:
        Settings.NUMBER_OF_CLIENTS = 2
    elif Settings.NUMBER_OF_CLIENTS > Settings.MAX_NUMBER_OF_CLIENTS:
        Settings.NUMBER_OF_CLIENTS = Settings.MAX_NUMBER_OF_CLIENTS
        
    if Settings.BUFFER_SIZE < 0:
        Settings.BUFFER_SIZE = 1024

    # Start the Server Thread.
    threading.Thread(target=Server).start()
    
    # Start the Client Threads.
    for _ in range(Settings.NUMBER_OF_CLIENTS):
        threading.Thread(target=Client.startClientGUI).start()
        sleep(0.1)
