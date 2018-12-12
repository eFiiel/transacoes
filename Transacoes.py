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
        :param status:
        :type status: int
        :param content:
        :type content: dict
        """
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
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'status': self.status,
            'content': self.content
        }

    def log(self):
        with open('transactions.log', "r") as log:
            temp = json.load(log)

        temp[self.id] = self.getTrans()
        with open('transactions.log', 'w') as log:
            log.write(json.dumps(temp, indent=4))

    def desejaEfetivar(self):
        """
        paramsHosps = {
            'ct': self.content['dst'],
            'qts': self.content['qts'],
            'ent': self.content['ida'],
            'sai': self.content['volta'],
            'trans': self
        }
        paramsPassagem = {
            'org':self.content['org'],
            'dst': self.content['dst'],
            'qtd': self.content['qtd'],
            'ida': self.content['ida'],
            'volta': self.content['volta'],
            'id': self.id,


        }
        """
        params = self.content.copy()
        params['id'] = self.id

        ticks = requests.get("http://localhost:9000/rcvTrans", params=params).json()
        room = requests.get("http://localhost:8500/rcvTrans", params=params).json()
        print(ticks+room)
        if not (ticks == [] or room == []):
            return ticks + room
        else:
            return []

    def respond(self):
        if self.status == Status.Done:
            ticks = requests.get("http://localhost:9000/done")
            hosps = requests.get("http://localhost:8500/done")
        elif self.status == Status.Aborted:
            ticks = requests.get("http://localhost:9000/abort")
            hosps = requests.get("http://localhost:8500/abort")
