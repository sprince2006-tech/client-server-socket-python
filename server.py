import socket
import threading
import sqlite3

HOST = '0.0.0.0'  # Listen on all interfaces (simulate WAN)
PORT = 6000

# Initialize and setup SQLite DB
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Handle client requests
def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                break
            print(f"[{addr}] Command received: {data}")

            response = process_command(data, cursor, conn)
            client_socket.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        client_socket.close()
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def process_command(command, cursor, conn):
    parts = command.split()
    if len(parts) == 0:
        return "Invalid command.\n"

    cmd = parts[0].upper()

    try:
        if cmd == "GET":
            if len(parts) == 1:
                # Return all users
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
                if rows:
                    return '\n'.join([f"ID:{r[0]} Name:{r[1]} Email:{r[2]}" for r in rows]) + '\n'
                else:
                    return "No users found.\n"
            elif len(parts) == 3 and parts[1].upper() == "USER":
                user_id = parts[2]
                cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
                row = cursor.fetchone()
                if row:
                    return f"ID:{row[0]} Name:{row[1]} Email:{row[2]}\n"
                else:
                    return "User not found.\n"
            else:
                return "Invalid GET command format.\n"

        elif cmd == "ADD":
            # Format: ADD USER <name> <email>
            if len(parts) >= 4 and parts[1].upper() == "USER":
                name = parts[2]
                email = parts[3]
                cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
                conn.commit()
                return f"User '{name}' added successfully.\n"
            else:
                return "Invalid ADD command format.\n"

        elif cmd == "UPDATE":
            # Format: UPDATE USER <id> <new_email>
            if len(parts) == 4 and parts[1].upper() == "USER":
                user_id = parts[2]
                new_email = parts[3]
                cursor.execute("UPDATE users SET email=? WHERE id=?", (new_email, user_id))
                conn.commit()
                if cursor.rowcount == 0:
                    return "User not found.\n"
                return f"User ID {user_id} updated successfully.\n"
            else:
                return "Invalid UPDATE command format.\n"

        elif cmd == "DELETE":
            # Format: DELETE USER <id>
            if len(parts) == 3 and parts[1].upper() == "USER":
                user_id = parts[2]
                cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    return "User not found.\n"
                return f"User ID {user_id} deleted successfully.\n"
            else:
                return "Invalid DELETE command format.\n"

        elif cmd == "EXIT":
            return "Goodbye!\n"

        else:
            return "Unknown command.\n"
    except sqlite3.IntegrityError:
        return "Error: Email must be unique.\n"
    except Exception as e:
        return f"Error processing command: {str(e)}\n"

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()

