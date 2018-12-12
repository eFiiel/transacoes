from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import json
import copy
import requests
from datetime import datetime
import os

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
        self.timestamp = datetime.now().timestamp()
        temp[self.id] = self.getTrans()
        with open('transactions.log', 'w') as log:
            log.write(json.dumps(temp, indent=4))

    def desejaEfetivar(self):
        paramsPassagem = self.content.pop('qts')
        paramsHosps = {
            'ct': self.content['dst'],
            'qts': self.content['qts'],
            'ent': self.content['ida'],
            'sai': self.content['volta'],
            'trans': self
        }

        ticks = requests.get("http://localhost:9000/rcvTrans", params=paramsPassagem)
        rooms = requests.get("http://localhost:8500/rcvTrans", params=paramsHosps)


def compraHosps(ent, sai, ct, qts, tipo):

    with open('hotel.json') as f:
        rooms = json.load(f)
    if tipo == 1:
        file = 'hotel.json'
    if tipo == 2:
        file = 'hotel.json.temp'

    out = []
    diaent = int(ent.split("/")[0])
    diasai = int(sai.split("/")[0])
    auxd = ent
    for i in range(diaent, diasai, 1):
        found = False
        auxd = ent.replace(str(diaent), str(i))
        for j in rooms:
            if j['local'] == ct:
                if j['data'] == auxd:
                    if j['quartos'] >= qts:
                        out.append(j)
                        j['quartos'] -= qts
                        found = True
                        break
        if not found:
            out = []
            break
    if found:
        with open(file, 'w') as file:
            json.dump(rooms, file, indent=4)
    return out

def CPhosps(request):
    if request.method == 'GET':
        ct = request.GET.get('city', None).rstrip("\n")
        qts = int(request.GET.get('qts', None).rstrip("\n"))
        ent = request.GET.get('in', None).rstrip("\n")
        sai = request.GET.get('out', None).rstrip("\n")
        out = compraHosps(ent, sai, ct, qts, 1)
        return jr(out, safe=False)
    else:
        return rp('The method must be Get!')


def LShosps(request):
    if request.method == 'GET':
        with open('hotel.json') as file:
            rooms = json.load(file)
        return jr(rooms, safe=False)
    else:
        return rp('The method must be Get!')


def rcvTrans(request):
    if request.method == 'GET':
        ct = request.GET.get('ct', None).rstrip("\n")
        qts = request.GET.get('qts', None).rstrip("\n")
        ent = request.GET.get('ent', None).rstrip("\n")
        sai = request.GET.get('sai', None).rstrip("\n")
        trans = request.GET.get('trans', None)  # type:Transaction

        result = compraHosps(ct, qts, ent, sai, 2)
        if not result == []:
            trans.status = Status.Done

        trans.log()
        return jr(result, safe=False)
    else:
        return rp('The method must be Get!')


def done(request):
    if request.method == 'GET':
        with open("hotel.json.temp", 'r') as file:
            tickets = json.load(file)

        with open("hotel.json", 'w') as file:
            file.write(json.dumps(tickets, indent=4))
        return rp("Ok")


def abort(request):
    if request.method == 'GET':
        os.remove("hotel.json.temp")
        return rp("Ok")
