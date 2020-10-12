import threading

PAYLOAD = 1024


class ClientStruct:
    def __init__(self):
        self.clients = {}
        self.nicknames = set()

    def send_everyone(self, message):
        for client in self.clients:
            client.send(bytes(message, "utf-8"))


class ClientThread(threading.Thread):
    """
    Класс для описания каждого потока, выделенного под одного клиента
    client_socket   ---  сокет клиента, полученный из модуля socket
    client_address  ---  адрес и порт клиента, полученные из модуля socket
    home_struct     ---  общая структура строго типа Clientstruct, разделяемая клиентами одного чата
    """
    def __init__(self, client_socket, client_address, home_struct: ClientStruct):
        threading.Thread.__init__(self)

        self.struct = home_struct

        self.clientSocket = client_socket
        self.clientAddress = client_address
        self.nickname = self.__set_nickname__()

        home_struct.clients[client_socket] = client_address  # добавляем клиента в базу в конце, чтобы не отвлекать
                                                             # его от инициализации


    def __set_nickname__(self):
        self.clientSocket.send(bytes("Hi! What is the name you go by?", "utf-8"))
        while True:
            input_name = self.clientSocket.recv(PAYLOAD).decode()
            if input_name not in self.struct.nicknames:
                self.clientSocket.send(bytes(f"Welcome to the chat, {input_name}!", "utf-8"))
                self.struct.nicknames.add(input_name)
                return input_name
            else:
                self.clientSocket.send(bytes(f"Name {input_name} is taken, try another one.", "utf-8"))

    def run(self):
        print("Connection from: ", self.clientAddress[0] + ':' + str(self.clientAddress[1]))
        while True:
            data = self.clientSocket.recv(PAYLOAD)
            message = data.decode("utf-8")
            self.struct.send_everyone(self.nickname + ": " + message)

    def __del__(self):
        self.struct.clients.pop(self.clientSocket)
        self.struct.nicknames.remove(self.nickname)

        self.struct.send_everyone(bytes(f"{self.nickname} has left the chatroom.", "utf-8"))
