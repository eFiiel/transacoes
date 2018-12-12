from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import json
import copy
import requests
from datetime import datetime
import os

atual=None

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
        qtd = request.GET.get('qtd', None).rstrip("\n")
        ida = request.GET.get('ida', None).rstrip("\n")
        volta = request.GET.get('volta', None).rstrip("\n")
        trans = request.GET.get('trans', None)  # type:Transaction

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
        return rp("Ok")


def abort(request):
    if request.method == 'GET':
        os.remove("passagens.json.temp")
        atual.status = Status.Aborted
        atual.log()
        return rp("Ok")
