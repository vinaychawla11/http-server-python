import socket
import threading
import sys
import os
import gzip

def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        connect, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(connect,))
        client_thread.start()

def send_response(connect, status_code, encoding, content_type, content):
    response = f"HTTP/1.1 {status_code}\r\n"
    if encoding == "gzip":
        compressed_content = gzip.compress(content.encode())
        response += f"Content-Encoding: {encoding}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(compressed_content)}\r\n\r\n"
        connect.sendall(response.encode() + compressed_content)
    else:
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(content)}\r\n\r\n"
        response += content
        connect.sendall(response.encode())

def handle_client(connect):
    try:
        data = connect.recv(1024).decode().split("\r\n")
        method, path, _  = data[0].split()
        headers = {}
        for line in data[1:-2]:
            if not line:
                break
            key, value = line.split(": ")
            headers[key] = value
        body = data[-1]
        
        encoding = headers.get("Accept-Encoding", "")
        encoded = encoding.split(", ")
        
        if method == "GET":
            if path == "/":
                send_response(connect, "200 OK", encoding, "text/plain", "Hello, this is the root.")
            elif path.startswith("/echo/"):
                path_arr = path.split("/")[-1]
                if "gzip" in encoded:
                    send_response(connect, "200 OK", "gzip", "text/plain", path_arr)
                else:
                    send_response(connect, "200 OK", "not-gzip", "text/plain", path_arr)
            elif path == "/user-agent":
                user_agent = headers.get("User-Agent", "")
                send_response(connect, "200 OK", encoding, "text/plain", user_agent)
            elif path.startswith("/files/"):
                filename = path.split("/")[-1]
                directory = sys.argv[2]  # Ensure to handle directory correctly
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r') as file:
                        contents = file.read()
                    send_response(connect, "200 OK", encoding, "application/octet-stream", contents)
                except FileNotFoundError:
                    send_response(connect, "404 Not Found", encoding, "text/plain", "File not found.")
            else:
                send_response(connect, "404 Not Found", encoding, "text/plain", "Endpoint not found.")
        
        elif method == "POST":
            if path.startswith("/files/"):
                filename = path.split("/")[-1]
                directory = sys.argv[2]  # Ensure to handle directory correctly
                file_path = os.path.join(directory, filename)
                req_body = data[-1]
                with open(file_path, 'w') as file:
                    file.write(req_body)
                send_response(connect, "201 Created", encoding, "text/plain", "File created successfully.")
            else:
                send_response(connect, "404 Not Found", encoding, "text/plain", "Endpoint not found.")
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connect.close()

if __name__ == "__main__":
    main()
