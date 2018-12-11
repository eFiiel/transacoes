from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import copy
import requests
import json


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
        response = requests.request('GET', "http://localhost:9000/LSpassagens/")
        return jr(json.loads(response.text), safe=False)
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

        response = requests.get("http://localhost:8500/CPhosps/", params=params)
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def LShosps(request):
    if request.method == 'GET':
        response = requests.get("http://localhost:8500/LShosps/")
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
