import socket
import pickle
import threading
import os

MASTER_ADDRESS = ('localhost', 5001)  # Address of the master node
FILES = {}  # Dictionary to store files available for sharing

def register_to_master(files, port):

# Registers the slave and its available files with the master including the file-sharing port.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to master at {MASTER_ADDRESS}")
            s.connect(MASTER_ADDRESS)
            message = {'type': 'register', 'files': files, 'port': port}
            print(f"Registering with master: {message}")
            s.sendall(pickle.dumps(message))
            response = pickle.loads(s.recv(1024))
            print("Registered:", response)
    except Exception as e:
        print(f"Error registering with master: {e}")

def search_file(filename):
# Searches for a file in the P2P network via the master
    try:
        filename = filename.strip().lower()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to master to search for: {filename}")
            s.connect(MASTER_ADDRESS)
            message = {'type': 'search', 'filename': filename}
            print(f"Sending search request: {message}")
            s.sendall(pickle.dumps(message))
            response = pickle.loads(s.recv(1024))
            print(f"Search response received: {response}")
            return response.get('peer')
    except Exception as e:
        print(f"Error searching file: {e}")
        return None

def download_file(peer, filename):
# Downloads a file from another peer
    try:
        peer_address, peer_port = peer
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_address, peer_port))
            s.sendall(filename.encode())
            with open(filename, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"Downloaded {filename} from {peer}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def serve_files(port):
# Starts a server to share files with other peers on a specific port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', port))
    server.listen(5)
    print(f"Serving files on port {port}")

    def handle_download(conn):
        """
        Handles file requests from peers.
        """
        filename = conn.recv(1024).decode().strip().lower()
        print(f"Request for file: {filename}")
        if filename in FILES:
            with open(filename, 'rb') as f:
                conn.sendfile(f)
            print(f"Sent file: {filename}")
        else:
            print(f"File not found: {filename}")
        conn.close()

    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr} for file download")
        threading.Thread(target=handle_download, args=(conn,)).start()

if __name__ == '__main__':
    # Prompt the user for the port to serve files on
    my_port = int(input("Enter port for serving files: "))
    # List files in the current directory and register them
    FILES = {file.strip().lower(): my_port for file in os.listdir()}
    print(f"Files to be registered: {FILES}")
    threading.Thread(target=serve_files, args=(my_port,)).start()
    register_to_master(FILES, my_port)

    # Loop to handle user actions
    while True:
        action = input("Search or exit? (search/exit): ").strip()
        if action == 'search':
            filename = input("Enter filename to search: ").strip()
            peer = search_file(filename)
            if peer:
                print(f"File found at: {peer}")
                download_file(peer, filename)
            else:
                print("File not found.")
        elif action == 'exit':
            break
