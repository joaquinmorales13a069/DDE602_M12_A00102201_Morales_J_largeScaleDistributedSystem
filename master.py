import socket
import threading
import pickle

PEERS = {}  # {address: (connection object, serving port)}
FILES = {}  # {filename: (peer_address, serving_port)}

def handle_peer(conn, addr):

# Handles communication with a connected peer.

    global PEERS, FILES
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = pickle.loads(data)
            print(f"Message received from {addr}: {message}")

            if message['type'] == 'register':
                # Register the peer and its files
                file_sharing_port = message['port']
                PEERS[addr] = (conn, file_sharing_port)

                # Update the global FILES dictionary
                for file in message['files']:
                    FILES[file.strip().lower()] = (addr[0], file_sharing_port)
                print(f"Files registered: {FILES}")
                conn.sendall(pickle.dumps({'status': 'registered'}))

            elif message['type'] == 'search':
                # Search for a file
                filename = message['filename'].strip().lower()
                print(f"Searching for file: {filename}")
                if filename in FILES:
                    peer_address, peer_port = FILES[filename]
                    print(f"File {filename} found at {peer_address}:{peer_port}")
                    conn.sendall(pickle.dumps({'peer': (peer_address, peer_port)}))
                else:
                    print(f"File {filename} not found.")
                    conn.sendall(pickle.dumps({'peer': None}))
    except Exception as e:
        print(f"Error handling peer {addr}: {e}")
    finally:
        conn.close()
        PEERS.pop(addr, None)

def main():

# Main function to start the master server.

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5001))  # Bind to a well-known port
    server.listen(5)  # Allow up to 5 pending connections
    print("Master is running on port 5001")

    while True:
        # Accept new connections from peers
        conn, addr = server.accept()
        print(f"Peer connected: {addr}")
        threading.Thread(target=handle_peer, args=(conn, addr)).start()

if __name__ == '__main__':
    main()
