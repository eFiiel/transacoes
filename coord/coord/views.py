from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import copy
import requests
from datetime import datetime
import json
import sys
sys.path.append("/home/efiiel/Dropbox/transactions")
import Transacoes

class Status:
    Active = 1
    Done = 2
    Aborted = 3


def CPpassagens(request):
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo os objetos encontrados
    """
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
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo todos os objetos da base de dados
    """
    if request.method == 'GET':
        response = requests.get("http://localhost:9000/LSpassagens/")
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def CPhosps(request):
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo os objetos encontrados
    """
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
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo todos os objetos da base de dados
    """
    if request.method == 'GET':
        response = requests.get("http://localhost:8500/LShospedagens/")
        return jr(response.json(), safe=False)
    else:
        return rp('The method must be Get!')


def CPpcks(request):
    """
    Método que instancia transação para realizar a busca de um pacote
    :param request:  Requisição recebida via WebService
    :return:
    """
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
        # transação criada
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
