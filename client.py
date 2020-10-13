import socket
from threading import Thread


SERVER = "127.0.0.1"
PORT = 13000
PAYLOAD = 1024
RUN = True  # переменная, которая должна быть общей для функций получения и отправки сообщений


def receive_process(client):
    global RUN
    while RUN:
        incoming = client.recv(PAYLOAD)

        if incoming == b"":  # проверка за флуд с сервера в случае его отключения. Да, приходят пустые штуки
            try:
                socket.socket().connect((SERVER, PORT)) # ЗАКРЫТЬ БЫ ЭТОТ СОКЕТ
            except ConnectionRefusedError:
                print("Server has just DIED!")
                RUN = False
        print(">>>" + incoming.decode())


def client_app_run():
    global RUN  # в этой функции глобальный флаг устанавливается в 0, если пользователь хочет отключиться
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))

    receive = Thread(target=receive_process, daemon=True, args=(client,))
    receive.start()

    while RUN:
        message = input()
        client.send(bytes(message, 'UTF-8'))
        if message == 'DISCONNECT':
            response = client.recv(PAYLOAD).decode()
            if response == "DISCONNECTED":
                break
            RUN = False


client_app_run()
