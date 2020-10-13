import threading
import socket

PAYLOAD = 1024


class ClientStruct:
    """
    База данных, состоящая из словаря клиентов вида {socket: (ip_address, port)} и введённых пользователями ников.
    Адрес и порт возвращаются методом socket.accept() вторым значением кортежа.
    ***
    Метод send_everyone отправляет сообщение, которое принимает как аргумент, всем клиентам чата, существующим в базе.
    """
    def __init__(self):
        self.clients = {}
        self.nicknames = set()

    def send_everyone(self, message):
        if message != "":
            print(message)
            for client in self.clients:
                client.send(bytes(message, "utf-8"))


class ClientThread(threading.Thread):
    """
    Класс для каждого потока, выделенного под одного клиента.
    client_socket   ---  сокет клиента, полученный из модуля socket
    client_address  ---  адрес и порт клиента, полученные из модуля socket
    home_struct     ---  общая структура строго типа Clientstruct, разделяемая клиентами одного чата
    """

    def __init__(self, client_socket: socket.socket, client_address, home_struct: ClientStruct):
        threading.Thread.__init__(self)

        self.struct = home_struct

        self.clientSocket = client_socket
        self.clientAddress = client_address
        self.nickname = self.__set_nickname__()

        home_struct.clients[client_socket] = client_address  # добавляем клиента в базу в конце __init__, чтобы
        #  не отвлекать его от инициализации сообщениями, приходящими в чат от других пользователей.

    def __set_nickname__(self):  # private-метод для инициализации имени пользователя в конструкторе.
        self.clientSocket.send(bytes("Hi! What is the name you go by?", "utf-8"))
        while True:
            input_name = self.clientSocket.recv(PAYLOAD).decode()
            if input_name not in self.struct.nicknames:
                self.clientSocket.send(bytes(f"Welcome to the chat, {input_name}!"
                                             f" Type in \"DISCONNECT\" to leave this chat", "utf-8"))
                self.struct.nicknames.add(input_name)
                return input_name
            else:
                self.clientSocket.send(bytes(f"Name {input_name} is taken, try another one.", "utf-8"))

    def __clear__(self):
        """
        Функция с говорящим названиеем: база клиентов очищается от данных удаляемого пользователя.
        Закрывается сокет, привязанный к клиенту.
        """
        self.struct.clients.pop(self.clientSocket)
        self.struct.nicknames.remove(self.nickname)
        self.clientSocket.close()

    def run(self):
        """
        Оверрайд одноимённого метода из суперкласса Thread.
        В цикле сервер принимает ввод клиента и перенаправляет его остальным участникам чата.
        """
        print("Connection from: ", self.clientAddress[0] + ':' + str(self.clientAddress[1]))
        while True:
            data = self.clientSocket.recv(PAYLOAD)
            message = data.decode("utf-8")

            if message == "DISCONNECT":  # пользователь хочет уйти
                self.struct.send_everyone(self.nickname + " has left the chat")
                self.clientSocket.send(bytes("DISCONNECTED", "utf-8"))
                self.__clear__()
                return
            else:
                self.struct.send_everyone(self.nickname + ": " + message)
