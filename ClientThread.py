import socket
from threading import Lock

PAYLOAD = 1024


class ClientStruct:
    """
    База данных, состоящая из словаря клиентов вида {socket: (ip_address, port)} и введённых пользователями ников.
    Адрес и порт возвращаются методом socket.accept() вторым значением кортежа.
    ***
    Метод send_everyone отправляет сообщение, которое принимает как аргумент, всем клиентам чата, существующим в базе.
    ***
    Метод add_client обновляет словарь-базу данных, записывая туда нового клиента, защищая его как критическую секцию.
    """
    def __init__(self):
        self.clients = {}
        self.nicknames = set()
        self.mutex = Lock()

    def send_everyone(self, message):
        if message != "":
            for client in self.clients:
                client.send(bytes(message, "utf-8"))

    def add_client(self, client: socket.socket, client_address):
        self.mutex.acquire()
        self.clients[client] = client_address
        self.mutex.release()


class ClientThread:
    """
    Класс для описания потока взаимодействия с каждым клиентом.
    client_socket   ---     сокет клиента, полученный из модуля socket
    client_address  ---     адрес и порт клиента, полученные из socket.accept()
    home_struct     ---     общая структура строго типа Clientstruct, общая для клиентов одного чата, позволяющая им
                            принимать сообщения друг от друга
    """

    def __init__(self, client_socket: socket.socket, client_address, home_struct: ClientStruct):

        self.struct = home_struct

        self.clientSocket = client_socket
        self.clientAddress = client_address
        self.nickname = self.__set_nickname__()

        home_struct.add_client(client_socket, client_address)  # добавляем клиента в базу в самом конце __init__, чтобы
        #  не отвлекать его от инициализации сообщениями, приходящими в чат от других пользователей.

    def run(self):
        """
        В цикле сервер принимает ввод клиента и перенаправляет его остальным участникам чата.
        Если клиент хочет выйти из чата, это тоже обрабатывается в цикле.
        """
        print("Connection from: ", self.clientAddress[0] + ':' + str(self.clientAddress[1]))

        while True:
            data = self.clientSocket.recv(PAYLOAD)
            message = data.decode("utf-8")

            if message == "DISCONNECT":  # пользователь хочет уйти - удаляем всё связанное с ним из базы
                self.disconnect()
                return
            elif message != "":
                self.struct.send_everyone(self.nickname + ": " + message)

    def disconnect(self):
        """
        Отключить клиента от сервера и удалить все связанные с ним данные из базы
        """
        self.clientSocket.send(bytes("DISCONNECTED", "utf-8"))
        self.__clear__()

        self.struct.send_everyone(self.nickname + " has left the chat")

    def __set_nickname__(self):  # private-метод для инициализации имени пользователя в конструкторе.
        self.clientSocket.send(bytes("Hi! What is the name you go by?", "utf-8"))
        while True:
            input_name = self.clientSocket.recv(PAYLOAD).decode()

            # пользователь решил выйти во время ввода имени
            if input_name == "DISCONNECT":
                self.clientSocket.send(bytes("DISCONNECTED", "utf-8"))
                self.__clear__(at_login=True)
                exit()

            # Допустимо лишь незанятое имя
            elif input_name not in self.struct.nicknames:
                self.clientSocket.send(bytes(f"Welcome to the chat, {input_name}!"
                                             " Type \"DISCONNECT\" to leave this chat", "utf-8"))
                self.struct.nicknames.add(input_name)  # в множество ников из базы добавляется новое имя
                return input_name
            else:
                self.clientSocket.send(bytes(f"Name {input_name} is taken, try another one.", "utf-8"))

    def __clear__(self, at_login=False):
        """
        Функция с говорящим названиеем: база клиентов очищается от данных удаляемого пользователя.
        Закрывается сокет, привязанный к клиенту.
        Флаг at_login служит для цели применений в случае, если выйти нужно на этапе ввода имени
        """
        if not at_login:
            self.struct.clients.pop(self.clientSocket)
            self.struct.nicknames.remove(self.nickname)
        self.clientSocket.close()
