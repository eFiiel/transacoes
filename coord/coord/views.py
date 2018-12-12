from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
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
        paramsPassagem = self.content.pop('qts')
        paramsHosps = {
            'ct': self.content['dst'],
            'qts': self.content['qts'],
            'ent': self.content['ida'],
            'sai': self.content['volta'],
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
        org = request.GET.get('org', None).rstrip("\n")
        dst = request.GET.get('dst', None).rstrip("\n")
        qts = int(request.GET.get('qts', None).rstrip("\n"))
        pep = int(request.GET.get('people', None).rstrip("\n"))
        ent = request.GET.get('ida', None).rstrip("\n")
        sai = request.GET.get('volta', None).rstrip("\n")
        out = []
        content ={
            'org': org,
            'dst': dst,
            'qts': qts,
            'qtd': pep,
            'ida': ent,
            'volta': sai
        }
        trans = Transaction(datetime.now().timestamp(), Status.Active, content)
        trans.log()
        ans = trans.desejaEfetivar()
        if ans:
            trans.status = Status.Done
        else:
            trans.status = Status.Aborted
        trans.log()
        trans.respond()

        diaent = int(ent.split("/")[0])
        diasai = int(sai.split("/")[0])

        for i in range(diaent, diasai, 1):
            temp = copy.deepcopy(rooms)
            print("Dps", temp[0])
            found = False
            auxd = ent.replace(str(diaent), str(i))
            for j in rooms:
                if j['local'] == dst:
                    if j['data'] == auxd:
                        if j['quartos'] >= qts:
                            out.append(j)
                            j['quartos'] -= qts
                            found = True
                            break
            if not found:
                print("Rooms", rooms[0])
                out = []
                break
        if not found:
            print("resetou")
            rooms = copy.deepcopy(temp)
            return jr([], safe=False)
        else:
            print('pegou hotel')
            gotHotel = True

        for i in tickets:
            if i['origem'].casefold() == org.casefold() and not idaFlag:
                if i['destino'].casefold() == dst.casefold():
                    if int(i['vagas']) > int(pep):
                        if i['data'] == ent:
                            i['vagas'] -= int(pep)
                            out.append(i)
                            print('pegou ida')
                            idaFlag = True
                            continue
        if sai and idaFlag:
            for i in tickets:
                if i['origem'].casefold() == dst.casefold() and not voltaFlag:
                    if i['destino'].casefold() == org.casefold():
                        if int(i['vagas']) > int(pep):
                            if i['data'] == sai:
                                i['vagas'] -= int(pep)
                                out.append(i)
                                print('pegou volta')
                                voltaFlag = True
                                break
        if idaFlag and voltaFlag:
            gotTicket = True
        if not (gotHotel and gotTicket):
            out = []
        return jr(out, safe=False)
    else:
        return rp('The method must be Get!')
