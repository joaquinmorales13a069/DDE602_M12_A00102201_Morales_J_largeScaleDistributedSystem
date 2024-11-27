import socket
import threading
import pickle

# Dictionaries to store information about connected peers and their files
PEERS = {}  # {address: connection object}
FILES = {}  # {address: list of files available}

def handle_peer(conn, addr):
    """
    Handles communication with a connected peer.
    Registers, searches, and unregisters files based on peer requests.
    """
    global PEERS, FILES
    try:
        while True:
            # Receive and deserialize data from the peer
            data = conn.recv(1024)
            if not data:
                break

            message = pickle.loads(data)

            # Handle registration of peer and its files
            if message['type'] == 'register':
                PEERS[addr] = conn
                FILES[addr] = message['files']
                conn.sendall(pickle.dumps({'status': 'registered'}))

            # Handle file search requests
            elif message['type'] == 'search':
                filename = message['filename']
                for peer, files in FILES.items():
                    if filename in files:
                        conn.sendall(pickle.dumps({'peer': peer}))
                        break
                else:
                    conn.sendall(pickle.dumps({'peer': None}))

            # Handle peer unregistration
            elif message['type'] == 'unregister':
                PEERS.pop(addr, None)
                FILES.pop(addr, None)
                conn.sendall(pickle.dumps({'status': 'unregistered'}))

    except Exception as e:
        print(f"Error handling peer {addr}: {e}")
    finally:
        # Cleanup after disconnection
        conn.close()
        PEERS.pop(addr, None)
        FILES.pop(addr, None)

def main():
    """
    Main function to start the master server.
    Listens for incoming connections from peers.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))  # Bind to a well-known port
    server.listen(5)  # Allow up to 5 pending connections
    print("Master is running on port 5000")

    while True:
        # Accept new connections from peers
        conn, addr = server.accept()
        print(f"Peer connected: {addr}")
        threading.Thread(target=handle_peer, args=(conn, addr)).start()

if __name__ == '__main__':
    main()
