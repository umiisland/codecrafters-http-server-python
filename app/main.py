import socket


def main():
    print("Logs from your program will appear here!")

    server_host = "localhost"
    server_port = 4221
    server_socket = socket.create_server((server_host, server_port), reuse_port=True)
    print(f"Server listening on port {server_port}...")

    client_connection_socket, client_addr = server_socket.accept()  # wait for client
    print(f"Accepted connection from {client_addr}")
    handle_response(client_connection_socket)


def handle_response(client_connection_socket):
    request_data = client_connection_socket.recv(1024).decode("utf-8")  # receive the data from the client
    path = extract_path(request_data)
    response_header = ""

    if path == "/":
        response_header = "HTTP/1.1 200 OK\r\n\r\n"
        response_body = "<p>Hello World!</p>"
    else:
        response_header = "HTTP/1.1 400 Not Found\r\n\r\n"
        response_body = "<p>Page Not Found!</p>"

    response = response_header + response_body
    client_connection_socket.sendall(response.encode())  # sending Response to the client
    print(f"Sent response... \n{response}")
    client_connection_socket.close()


def extract_path(request):
    return request.split("\r\n")[0].split(" ")[1]


if __name__ == "__main__":
    main()
