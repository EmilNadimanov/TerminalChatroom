import socket
from threading import Thread


class Client:

    def __init__(self, client_socket: socket.socket, server: str, port: int, payload=1024):
        self.RUN = True  # переменная, которая прерывает процесс получения и отправки сообщений, будучи False
        self.client = client_socket
        self.SERVER = server
        self.PORT = port
        self.PAYLOAD = payload

    def client_run(self):
        self.client.connect((self.SERVER, self.PORT))

        receive = Thread(target=self.receive_process, daemon=True)
        receive.start()

        while self.RUN is True:
            message = self.__get_prompt__()

            if message == "DISCONNECT":
                self.disconnect()
            elif message != "":
                self.client.send(bytes(message, "utf-8"))

    def server_is_alive(self):
        s = socket.socket()
        result = True
        try:
            s.connect((self.SERVER, self.PORT))
        except ConnectionRefusedError:
            result = False

        s.close()
        return result

    def receive_process(self):
        while self.RUN is True:
            incoming = self.client.recv(self.PAYLOAD)

            # Проверяем, жив ли сервер. Если он умер, пользователя заливает пустыми байтами.
            # Тут сразу два условия, чтобы не спамить запросами на сервер
            if incoming == b"" and self.server_is_alive() is False:
                print("Server has just DIED!")
                self.RUN = False
            else:
                print(">>>" + incoming.decode())

                if incoming == b'DISCONNECTED':
                    print("You were disconnected. Press Ctrl+C.")
                    self.RUN = False
                    exit()

    def __get_prompt__(self):
        message = ""

        try:
            message = input()
        except KeyboardInterrupt:
            message = "DISCONNECT"

        return message

    def disconnect(self):
        self.client.send(bytes("DISCONNECT", "utf-8"))


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = Client(s, server='127.0.0.1', port=13000)
    client.client_run()


if __name__ == '__main__':
    main()
