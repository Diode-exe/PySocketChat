# config.py - Complete configuration file

class Settings:
    # Server Configuration
    SERVER_ADDRESS = "192.168.0.109"  # Change this to your server's IP
    SERVER_PORT = 12500                # Change this to your desired port
    SERVER_NAME = "PySocket Chat"
    MAX_NUMBER_OF_CLIENTS = 10        # Maximum simultaneous clients
    
    # Message Configuration
    BUFFER_SIZE = 1024
    MESSAGE_ENCODING = "utf-8"
    
    # Debug Configuration
    EXCEPTIONS_INFO = True
