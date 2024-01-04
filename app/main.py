from socket import create_server
from threading import Thread
from os import path as os_path
import sys


def run_server(directory=None):
    print("Logs from your program will appear here!")

    server_host = "localhost"
    server_port = 4221
    try:
        server_socket = create_server((server_host, server_port), reuse_port=True)
        '''
            NOTE:
            The socket.create_server() is a convenience function to automatically: 
            1. creates a SOCK_STREAM type socket (a TCP socket)
            2. bind to *address* (a 2-tuple (host, port))
            3. call sock.listen()
            Otherwise, using socket.socket() to create a socket would have to do all of the above manually
        '''
        print(f"Server listening on port {server_port}...")

        while True:
            client_connection_socket, client_addr = server_socket.accept()
            '''
                NOTE:
                stalls the execution thread until a client connects and returns a tuple of (conn, address), 
                where address = a tuple of the client's IP address and port, 
                and conn = a new socket object which shares a connection with the client and can be used to communicate with it.
    
                server_socket.accept() creates a new socket to communicate with the client 
                instead of binding the listening socket to the client's address and using it for the communication, 
                because the listening socket needs to listen to further connections from other clients, 
                otherwise it would be blocked.
            '''
            print(f"Accepted connection from {client_addr}")
            handle_response_thread = Thread(target=handle_response, args=[client_connection_socket, client_addr, directory], daemon=True)
            handle_response_thread.start()
            print(handle_response_thread.name)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()


def handle_response(client_connection_socket, client_addr, directory):
    try:
        request_data = client_connection_socket.recv(1024).decode("utf-8")
        '''
            NOTE:
            The recv() method receives the specified number of bytes from the client. 
            1024 bytes is just a common convention for the size of the payload, 
            as it’s a power of two which is potentially better for optimization purposes than some other arbitrary value.
            
            decode() is used to transformed the data which is a sequence of bytes received from the client into a string
        '''
        path = extract_path(request_data)
        request_method = extract_http_method(request_data)

        if request_method == "GET" and path == "/":
            response_header = "HTTP/1.1 200 OK\r\n\r\n"
            response_body = "<p>Hello World!</p>"

        elif request_method == "GET" and path == "/user-agent":
            response_body = extract_user_agent(request_data)
            response_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n"

        elif request_method == "GET" and "/echo/" in path:
            response_body = path[6:]
            response_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n"

        elif request_method == "GET" and "/files/" in path:
            file_name = path[7:]
            is_file_exist = os_path.isfile(directory+file_name)
            if is_file_exist:
                with open(os_path.join(directory, file_name), "r") as target_file:
                    response_body = target_file.read()
                    response_header = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(response_body)}\r\n\r\n"
            else:
                response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
                response_body = "<p>File Not Found!</p>"
        elif request_method == "POST" and "/files/" in path and directory:
            file_name = path[7:]
            file_contents = extract_request_body(request_data)
            with open(os_path.join(directory, file_name), 'w') as file_to_write:
                file_to_write.write(file_contents)
                response_header = "HTTP/1.1 201 Created\r\n\r\n"
                response_body = f"File Created at {directory+file_name}"
        else:
            response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
            response_body = "<p>Page Not Found!</p>"

        response = response_header + response_body
        client_connection_socket.sendall(response.encode())  # sending Response to the client
        print(f"Sent response... \n{response}")
    except Exception as e:
        print(f"Error when handling client: {e}")
    finally:
        client_connection_socket.close()
        print(f"Connection to client ({client_addr[0]}:{client_addr[1]}) closed")


def extract_path(request):
    return request.split("\r\n")[0].split(" ")[1]


def extract_http_method(request):
    return request.split("\r\n")[0].split(" ")[0]


def extract_user_agent(request):
    for line in request.split("\r\n"):
        if "User-Agent:" in line:
            return line.split("User-Agent: ")[1]


def extract_request_body(request):
    request_sections = request.split("\r\n")
    if len(request_sections >= 2):
        return request_sections[1]


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) >= 3 and arguments[1] == "--directory":
        directory = arguments[2]
    else:
        directory = None
    run_server(directory)
