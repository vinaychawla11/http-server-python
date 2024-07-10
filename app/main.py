# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    response = b"HTTP/1.1 200 OK\r\n\r\n"
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connect, address = server_socket.accept() # wait for client
    while connect:
        data = connect.recv(1024).decode().split("\r\n");
        method, path  = data[0].split()
        if method == "GET":
            if path == "/":
                connect.sendall(response)
        else:
            connect.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

if __name__ == "__main__":
    main()
