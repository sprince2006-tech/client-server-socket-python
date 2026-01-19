import socket

SERVER_IP = input("Enter server IP (e.g. 127.0.0.1): ").strip()
SERVER_PORT = 6000

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        print("Commands available:\n"
              "GET                  - Get all users\n"
              "GET USER <id>        - Get user by ID\n"
              "ADD USER <name> <email> - Add new user\n"
              "UPDATE USER <id> <new_email> - Update user's email\n"
              "DELETE USER <id>     - Delete user by ID\n"
              "EXIT                 - Disconnect\n")

        while True:
            command = input("Enter command: ").strip()
            if not command:
                continue

            client.sendall(command.encode('utf-8'))

            if command.upper() == "EXIT":
                print("Disconnected from server.")
                break

            response = client.recv(4096).decode('utf-8')
            print("Response:\n" + response)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()

