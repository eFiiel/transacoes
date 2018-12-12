from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import copy
import requests
from datetime import datetime
import json
import sys
sys.path.append("/home/ewerton.fiel/Dropbox/codes/transacoes")
import Transacoes

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


def CPpassagens(request):
    if request.method == 'GET':
        params = {
            'org': request.GET.get('org', None).rstrip("\n"),
            'dst': request.GET.get('dst', None).rstrip("\n"),
            'qtd': request.GET.get('qtd', None).rstrip("\n"),
            'ida': request.GET.get('ida', None).rstrip("\n"),
            'volta': request.GET.get('volta', None).rstrip("\n")
        }
        response = requests.get("http://localhost:9000/CPpassagens/", params=params)
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def LSpassagens(request):
    if request.method == 'GET':
        response = requests.get("http://localhost:9000/LSpassagens/")
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def CPhosps(request):
    if request.method == 'GET':
        params = {
            'ct': request.GET.get('city', None).rstrip("\n"),
            'qts': int(request.GET.get('qts', None).rstrip("\n")),
            'ent': request.GET.get('in', None).rstrip("\n"),
            'sai': request.GET.get('out', None).rstrip("\n")
        }

        response = requests.get("http://localhost:8500/CPhospedagens/", params=params)
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def LShosps(request):
    if request.method == 'GET':
        response = requests.get("http://localhost:8500/LShospedagens/")
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def CPpcks(request):
    if request.method == 'GET':
        global rooms
        global tickets
        idaFlag = False
        voltaFlag = False
        gotHotel = False
        gotTicket = False
        try:
            org = request.GET.get('org', None).rstrip("\n")
            dst = request.GET.get('dst', None).rstrip("\n")
            qts = int(request.GET.get('qts', None).rstrip("\n"))
            pep = int(request.GET.get('people', None).rstrip("\n"))
            ent = request.GET.get('ida', None).rstrip("\n")
            sai = request.GET.get('volta', None).rstrip("\n")
        except:
            return jr([], safe=False)
        out = []
        content ={
            'org': org,
            'dst': dst,
            'qts': qts,
            'qtd': pep,
            'ida': ent,
            'volta': sai
        }
        trans = Transacoes.Transaction(datetime.now().timestamp(), Status.Active, content)
        trans.log()
        ans = trans.desejaEfetivar()
        if not ans == []:
            trans.status = Status.Done
        else:
            trans.status = Status.Aborted
        trans.log()
        trans.respond()

        print(ans)
        #out = []
        return jr(ans, safe=False)
    else:
        return rp('The method must be Get!')
