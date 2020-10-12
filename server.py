#!/usr/bin/env python3

import socket

from ClientThread import ClientThread, ClientStruct

HOST = "127.0.0.1"
PORT = 13000
ClientsDatabase = ClientStruct()


def handle_client(client_socket, client_address):
    ClientThread(client_socket, client_address, ClientsDatabase).start()


def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    while True:
        server.listen(10)
        client_socket, client_address = server.accept()
        handle_client(client_socket, client_address)


if __name__ == '__main__':
    run()
