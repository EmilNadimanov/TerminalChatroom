import socket
from threading import Thread


SERVER = "127.0.0.1"
PORT = 13000
PAYLOAD = 1024


def receive_process(client):
    while 1:
        incoming = client.recv(PAYLOAD)
        print(">>>" + incoming.decode())


def client_app_run():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    Thread(target=receive_process, daemon=True, args=(client,)).start()
    while 1:
        message = input()
        client.sendall(bytes(message, 'UTF-8'))
        if message == 'bye':
            break

    client.close()


client_app_run()
