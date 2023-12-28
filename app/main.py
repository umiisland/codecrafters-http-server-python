import socket


def main():
    print("Logs from your program will appear here!")

    server_host = "localhost"
    server_port = 4221
    server_socket = socket.create_server((server_host, server_port), reuse_port=True)
    print(f"Server listening on port {server_port}...")

    while True:
        client_connection_socket, client_addr = server_socket.accept() # wait for client
        print(f"Accepted connection from {client_addr}")
        handle_response(client_connection_socket)


def handle_response(client_connection_socket):
    requst_data = client_connection_socket.recv(1024).decode("utf-8")  # Receive the data from the client
    response_header = "HTTP/1.1 200 OK\r\n\r\n<p>Hello World!</p>"
    client_connection_socket.sendall(response_header.encode())  # Sending Response to the client


if __name__ == "__main__":
    main()
