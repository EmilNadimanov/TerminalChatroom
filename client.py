import socket
from threading import Thread
import sys


class Client:
    """
    Класс для описания процесса взаимодействия клиента с сервером.
    RUN         --- переменная, отвечающая за процесс получения и отправки сообщений. Прерывается его, будучи False.
    SERVER_IP   --- IP-адрес сервера.
    PORT        --- Порт, к которому нужно подключиться.
    PAYLOAD     --- Объём пакета, передаваемого по TCP.
    client      --- Сокет клиента, который и обслуживается в классе.
    """
    def __init__(self, client_socket: socket.socket, server_ip: str, port: int, payload=1024):
        self.RUN = True
        self.client = client_socket
        self.SERVER_IP = server_ip
        self.PORT = port
        self.PAYLOAD = payload

    def client_run(self):
        """
        Основной метод. Подключается к серверу, запускает в потоке процесс обработки получаемых данных.
        В цикле обрабатывает ввод пользователя и направляет его на сервер.
        """
        self.client.connect((self.SERVER_IP, self.PORT))

        receive = Thread(target=self.receive_process, daemon=True)
        receive.start()

        while self.RUN is True:
            message = self.__get_prompt__()

            if message != "" and self.RUN is True:
                self.client.send(bytes(message, "utf-8"))

    def server_is_alive(self):
        """
        Проверка, жив ли сервер. Выполняется попытка подключиться к нему из одноразового сокета.
        """
        s = socket.socket()
        result = True
        try:
            s.connect((self.SERVER_IP, self.PORT))
        except ConnectionRefusedError:
            result = False

        s.close()
        return result

    def receive_process(self):
        """
        Процедура, которая в цикле принимает данные от сервера и обрабатывает особые случаи: крах сервера и
        отключение от сервера
        """
        while self.RUN is True:
            incoming = self.client.recv(self.PAYLOAD)

            # Проверяем, жив ли сервер. Если он умер, пользователя заливает пустыми байтами.
            # Тут сразу два условия, чтобы не спамить запросами на сервер
            if incoming == b"" and self.server_is_alive() is False:
                print("Server has just DIED!")
                self.RUN = False
            else:
                print(incoming.decode())

                if incoming == b'DISCONNECTED':
                    print("You were disconnected. Press Ctrl+C.")
                    self.RUN = False
                    exit()

    @staticmethod
    def __get_prompt__():
        """
        Ввод из консоли с защитой от исключения в случае, если нажаты Ctrl+C или Ctrl+D
        """
        try:
            message = input()
        except (EOFError, KeyboardInterrupt):
            message = "DISCONNECT"

        return message


def main():
    if len(sys.argv) != 3:
        print("Launch as \"python client.py ip-address port-number\", e.g. \"python client.py 127.0.0.1 8080\"")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip_address, port_number = sys.argv[1], int(sys.argv[2])
    client = Client(s, server_ip=ip_address, port=port_number)
    client.client_run()


if __name__ == '__main__':
    main()
