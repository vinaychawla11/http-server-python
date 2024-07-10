import socket
import threading
import sys
import os
import gzip

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        connect, address = server_socket.accept() # wait for client
        client_thread = threading.Thread(target=handle_client, args=(connect,))
        client_thread.start()

def send_response(connect, status_code, encoding, content_type, content):
    response = f"HTTP/1.1 {status_code}\r\n"
    if encoding == "gzip":
        response += f"Content-Encoding: {encoding}\r\n"
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
            key,value = line.split(": ")
            headers[key] = value
        body = data[-1]
        encoding = headers.get("Accept-Encoding", "")
        encoded = encoding.split(", ")
        if method == "GET":
            if path == "/":
                send_response(connect, "200 OK",encoding, "text/plain", "Hello, this is the root.")
            elif path.startswith("/echo/"):
                pathArr = path.split("/")[-1]
                if "gzip" in encoded:
                    send_response(connect, "200 OK","gzip", "text/plain" , gzip.compress(pathArr.encode()))
                else:
                    send_response(connect, "200 OK",encoding, "text/plain" , pathArr)
            elif path == "/user-agent":
                userAgent = headers["User-Agent"]
                send_response(connect, "200 OK",encoding, "text/plain", userAgent)
            elif path.startswith("/files/"):
                filename = path.split("/")[-1]
                directory = sys.argv[2]
                filePath = os.path.join(directory, filename)
                try:
                    with open(filePath, 'r') as file:
                        contents = file.read()
                    send_response(connect, "200 OK", encoding,"application/octet-stream", contents)
                except FileNotFoundError:
                    send_response(connect, "404 Not Found", encoding, "text/plain", "File not found.")
            else:
                send_response(connect, "404 Not Found", encoding, "text/plain", "Endpoint not found.")
        
        elif method == "POST":
            if path.startswith("/files/"):
                filename = path.split("/")[-1]
                directory = sys.argv[2]
                filePath = os.path.join(directory, filename)
                reqBody = data[-1]
                
                with open(filePath, 'w') as file:
                    file.write(reqBody)
                send_response(connect, "201 Created", encoding, "text/plain", "File created successfully.")
            else:
                send_response(connect, "404 Not Found", encoding, "text/plain", "Endpoint not found.")
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connect.close()

if __name__ == "__main__":
    main()
