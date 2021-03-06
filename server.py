#!/usr/bin/env python3

import socket
import threading

from ClientThread import ClientThread, ClientStruct

HOST = "0.0.0.0"
PORT = 8080
ClientsDatabase = ClientStruct()


def handle_client(client_socket, client_address):
    client_thread = ClientThread(client_socket, client_address, ClientsDatabase)
    client_thread.run()


def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    try:
        while True:
            server.listen(10)
            client_socket, client_address = server.accept()

            threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()
    except (KeyboardInterrupt, EOFError):
        exit()


if __name__ == '__main__':
    run()
