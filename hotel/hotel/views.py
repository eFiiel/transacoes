from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import json
import copy
import requests
from datetime import datetime
import os
import sys
sys.path.append("/home/ewerton.fiel/Dropbox/codes/transacoes")
import Transacoes

atual = None


class Status:
    Active = 1
    Done = 2
    Aborted = 3


"""
class Transaction:
    idCounter = 0

    def __init__(self, timestamp, status, content, uid=None):
        
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
            'trans': self

        }

        ticks = requests.get("http://localhost:9000/rcvTrans", params=paramsPassagem).json()
        room = requests.get("http://localhost:8500/rcvTrans", params=paramsHosps).json()
        if not (ticks == [] or room == []):
            return ticks.extend(room)
        else:
            return False

    def respond(self):
        if self.status == Status.Done:
            ticks = requests.get("http://localhost:9000/done")
            hosps = requests.get("http://localhost:8500/done")
        elif self.status == Status.Aborted:
            ticks = requests.get("http://localhost:9000/abort")
            hosps = requests.get("http://localhost:8500/abort")
"""


def compraHosps(ct, qts, ent, sai, tipo):

    with open('hotel.json') as f:
        rooms = json.load(f)
    if tipo == 1:
        file = 'hotel.json'
    if tipo == 2:
        file = 'hotel.json.temp'

    out = []
    try:
        diaent = int(ent.split("/")[0])
        diasai = int(sai.split("/")[0])
    except:
        return []
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
        global atual
        org = request.GET.get('org', None).rstrip("\n")
        dst = request.GET.get('dst', None).rstrip("\n")
        qtd = int(request.GET.get('qtd', None).rstrip("\n"))
        ida = request.GET.get('ida', None).rstrip("\n")
        volta = request.GET.get('volta', None).rstrip("\n")
        qts = int(request.GET.get('qts', None).rstrip("\n"))
        uid = int(request.GET.get('id', None))

        content = {
            'org': org,
            'dst': dst,
            'qts': qts,
            'qtd': qtd,
            'ida': ida,
            'volta': volta
        }

        trans = Transacoes.Transaction(datetime.now().timestamp(), Status.Active, content, uid)
        trans.log()

        result = compraHosps(dst, qts, ida, volta, 2)
        if not result == []:
            trans.status = Status.Done

        trans.log()
        atual = trans
        return jr(result, safe=False)
    else:
        return rp('The method must be Get!')


def done(request):
    if request.method == 'GET':
        with open("hotel.json.temp", 'r') as file:
            tickets = json.load(file)

        with open("hotel.json", 'w') as file:
            file.write(json.dumps(tickets, indent=4))
        os.remove("hotel.json.temp")
        return rp("Ok")


def abort(request):
    if request.method == 'GET':
        os.remove("hotel.json.temp")
        return rp("Ok")
