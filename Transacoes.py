import copy
import requests
from datetime import datetime
import json


class Status:
    Active = 1
    Done = 2
    Aborted = 3


class Transaction:
    idCounter = 0

    def __init__(self, timestamp, status, content, uid=None):
        """

        :param uid: id da transação
        :type uid: int
        :param timestamp: momento de criação da transação
        :type timestamp: float
        :param status: status que a transação se encontra
        :type status: int
        :param content: conteúdo da requisição da transação
        :type content: dict
        """

        # caso o uid seja recebido, reinstância uma transação, caso não seja, cria um nova
        if uid == None:
            self.id = Transaction.idCounter
            Transaction.idCounter += 1
        else:
            self.id = uid
        self.timestamp = timestamp
        self.status = status
        self.content = content

        try:
            with open('transactions.log', "r") as f:
                pass
        except FileNotFoundError:
            with open('transactions.log', "w+") as f:
                f.write("{}")

    def getTrans(self):
        """

        :return: Dict Obj com as informações da transação
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'status': self.status,
            'content': self.content
        }

    def log(self):
        """
        Realiza a escrita do log da transação
        :return: None
        """
        with open('transactions.log', "r") as log:
            temp = json.load(log)
        self.timestamp = datetime.now().timestamp()
        temp[self.id] = self.getTrans()
        with open('transactions.log', 'w') as log:
            log.write(json.dumps(temp, indent=4))

    def desejaEfetivar(self):
        """

        :return: Lista contendo os objetos encontrados, caso encontrados, senão, lista vazia
        """

        params = self.content.copy()
        params['id'] = self.id

        ticks = requests.get("http://localhost:9000/rcvTrans", params=params).json()
        room = requests.get("http://localhost:8500/rcvTrans", params=params).json()
        #print(ticks+room)
        if not (ticks == [] or room == []):
            return ticks + room
        else:
            return []

    def respond(self):
        """
        Responde aos servidores participantes se a transação foi efetivada ou não
        :return:
        """
        if self.status == Status.Done:
            ticks = requests.get("http://localhost:9000/done")
            hosps = requests.get("http://localhost:8500/done")
        elif self.status == Status.Aborted:
            ticks = requests.get("http://localhost:9000/abort")
            hosps = requests.get("http://localhost:8500/abort")
