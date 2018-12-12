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

atual=None


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

def compraPass(org, dst, qtd, ida, tipo, volta=None):
    with open('passagens.json') as f:
        tickets = json.load(f)
    idaFlag = False
    voltaFlag = False
    out = []
    if tipo == 1:
        file = 'passagens.json'
    if tipo == 2:
        file = 'passagens.json.temp'
    for i in tickets:
        if i['origem'].casefold() == org.casefold() and not idaFlag:
            if i['destino'].casefold() == dst.casefold():
                if int(i['vagas']) > int(qtd):
                    if i['data'] == ida:
                        i['vagas'] -= int(qtd)
                        out.append(i)
                        idaFlag = True
                        continue
    if volta and idaFlag:
        for i in tickets:
            if i['origem'].casefold() == dst.casefold() and not voltaFlag:
                if i['destino'].casefold() == org.casefold():
                    if int(i['vagas']) > int(qtd):
                        if i['data'] == volta:
                            i['vagas'] -= int(qtd)
                            out.append(i)
                            voltaFlag = True
                            with open(file, 'w+') as file:
                                json.dump(tickets, file, indent=4)
                            return out
    if volta and not voltaFlag:
        out = []
    with open(file, 'w+') as file:
        json.dump(tickets, file, indent=4)
    return out


def CPpassagens(request):
    if request.method == 'GET':
        org = request.GET.get('org', None)
        dst = request.GET.get('dst', None)
        qtd = request.GET.get('qtd', None)
        ida = request.GET.get('ida', None)
        volta = request.GET.get('volta', None)

        out = compraPass(org, dst, qtd, ida, 1, volta)

        return jr(out, safe=False)
    else:
        return rp('The method must be Get!')


def LSpassagens(request):
    if request.method == 'GET':
        with open("passagens.json") as file:
            tickets = json.load(file)
        return jr(tickets, safe=False)
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
        result = compraPass(org, dst, qtd, ida, 2, volta)
        if not result == []:
            trans.status = Status.Done
        trans.log()
        atual = trans
        return jr(result, safe=False)
    else:
        return rp('The method must be Get!')


def done(request):
    if request.method == 'GET':
        with open("passagens.json.temp", 'r') as file:
            tickets = json.load(file)
        atual.status = Status.Done
        atual.log()
        with open("passagens.json", 'w') as file:
            file.write(json.dumps(tickets, indent=4))
        os.remove("passagens.json.temp")
        return rp("Ok")


def abort(request):
    if request.method == 'GET':
        os.remove("passagens.json.temp")
        atual.status = Status.Aborted
        atual.log()
        return rp("Ok")
