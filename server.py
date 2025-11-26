#!/usr/bin/env python3

import socket
import threading
import logging
from collections import deque

from config import Settings

class Server:
    connections: list[socket.socket] = [] # Clients' Socket List.
    serverSocket: socket.socket = None # Server's Socket.
    _shutdown = False  # Add shutdown flag

    def __init__(self) -> None:
        '''
            Initializes the Server.
        '''
                
        try:
            logging.basicConfig(level=logging.NOTSET, format='[SERVER - %(levelname)s] %(message)s') # Initialize Logging.

            # Create the Server's Socket and bind it to an address and a port.
            # Then give a maximum of simultaneous connections.
            Server.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Server.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
            Server.serverSocket.bind((Settings.SERVER_ADDRESS, Settings.SERVER_PORT))
            Server.serverSocket.listen(Settings.MAX_NUMBER_OF_CLIENTS)

            logging.info('Server started!')

            # Accepting Clients infinite loop.
            while not Server._shutdown:
                try:
                    serverConnection, address = Server.serverSocket.accept()
                    Server.connections.append((serverConnection, address))

                    # Broadcast the entry message.
                    entryMessage = f'[{address[0]}:{address[1]}] has entered the server.'
                    Server.broadcast(entryMessage, serverConnection)
                    logging.info(entryMessage)

                    last_messages = Server.getLastLines()
                    for line in last_messages:
                        try:
                            serverConnection.send(f"[HISTORY] {line}\n".encode(Settings.MESSAGE_ENCODING))
                        except Exception as e:
                            logging.error(f'Error sending message history: {e}')

                    # Start Client management.                
                    threading.Thread(target=Server.manageClient, args=[serverConnection, address], daemon=True).start()
                except OSError as e:
                    if not Server._shutdown:  # Only log if not intentionally shutdown
                        logging.error(f'Error accepting connection: {e}')
                    break
        except RuntimeError as e:
            logging.error(f'Error occurred when creating user thread: {e}.', exc_info=Settings.EXCEPTIONS_INFO)
        except Exception as e:
            logging.error(f'Error occurred when creating socket: {e}.', exc_info=Settings.EXCEPTIONS_INFO)
        finally:
            Server.shutdown()

    @staticmethod
    def shutdown():
        '''
            Properly shutdown the server.
        '''
        Server._shutdown = True
        
        # Close all client connections
        if Server.connections:
            for conn, addr in Server.connections[:]:  # Use slice copy to avoid modification during iteration
                Server.removeClient(conn, addr, broadcast=False)  # Don't broadcast during shutdown
        
        # Close server socket
        if Server.serverSocket:
            try:
                Server.serverSocket.close()
                logging.info('Server closed!')
            except:
                pass

    @staticmethod
    def manageClient(connection: socket.socket, address: str) -> None:
        '''
            Send and receive messages from all the users.
        '''
        
        # Clients messages handling infinite loop.
        while not Server._shutdown:
            try:
                receivedMessage = connection.recv(Settings.BUFFER_SIZE)
                if receivedMessage:
                    msg = receivedMessage.decode(Settings.MESSAGE_ENCODING, errors="replace")
                    sendingMessage = f'[{address[0]}:{address[1]}] {msg}'
                    logging.info(sendingMessage)
                    Server.broadcast(sendingMessage, connection)
                    Server.writeToFile(sendingMessage)  # Log the message
                else:
                    # Client disconnected gracefully
                    Server.removeClient(connection, address)
                    break
            except Exception as e:
                if not Server._shutdown:  # Only log if not intentionally shutdown
                    logging.error(f'Error occurred while handling client {address} connection: {e}.', exc_info=Settings.EXCEPTIONS_INFO)
                Server.removeClient(connection, address)
                break

    @staticmethod
    def writeToFile(message: str):
        '''
            Write message to log file.
        '''
        try:
            with open("msgLog.txt", "a") as file:
                file.write(f"{message}\n")
        except Exception as e:
            logging.error(f'Error writing to log file: {e}')
    
    @staticmethod
    def getLastLines():
        try:
            with open("msgLog.txt", "r") as file:
                last_five = deque(file, maxlen=5)  # Only keeps last 5 lines in memory
                return [line.strip() for line in last_five]  # Add this return statement
        except FileNotFoundError:
            return []  # Return empty list if file doesn't exist
        except Exception as e:
            logging.error(f'Error reading message history: {e}')
            return []  # Return empty list on error

    @staticmethod
    def broadcast(message: str, sender_connection: socket.socket) -> None:
        '''
            Send message to all clients except sender.
        '''
        
        # Send a broadcast message, cycling through all clients.
        for clientConnection, addr in Server.connections[:]:  # Use slice copy
            if clientConnection != sender_connection:  # Don't send back to sender
                try:
                    clientConnection.send(message.encode(Settings.MESSAGE_ENCODING))
                except Exception as e:
                    logging.error(f'Error occurred while broadcasting message to client {addr}: {e}.', exc_info=Settings.EXCEPTIONS_INFO)
                    Server.removeClient(clientConnection, addr)


    @staticmethod
    def removeClient(connection: socket.socket, address: str, broadcast: bool = True) -> None:
        '''
            Remove client from the connection list.
        '''
        
        # Removes the selected client from the connections list,
        # then send a broadcast message with that information.
        try:
            connection.close()
        except:
            pass
            
        # Remove from connections list
        Server.connections = [(c, addr) for c, addr in Server.connections if c != connection]
        
        if broadcast and not Server._shutdown:
            leavingMessage: str = f'[{address[0]}:{address[1]}] has left the server.'
            Server.broadcast(leavingMessage, connection)
            logging.info(leavingMessage)

if __name__ == "__main__":
    try:
        Server()
    except KeyboardInterrupt:
        logging.info('Server interrupted by user')
        Server.shutdown()