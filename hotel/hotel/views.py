from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import json
import copy
import requests
from datetime import datetime
import os
import sys
sys.path.append("/home/efiiel/Dropbox/transactions")
import Transacoes


class Status:
    Active = 1
    Done = 2
    Aborted = 3


def compraHosps(ct, qts, ent, sai, tipo):
    """

    :param org: Cidade de origem
    :param dst: Cidade de Destino
    :param qtd: Quantidade de Passagens
    :param ida: Data de Ida
    :param tipo: Tipo da compra: Passagem ou Pacote
    :param volta: Data da volta, se existente
    :return: Lista contendo as passagens compradas, se encontradas, senão apenas uma lista vazia
    """

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
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo os objetos encontrados
    """
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
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo todos os objetos da base de dados
    """
    if request.method == 'GET':
        with open('hotel.json') as file:
            rooms = json.load(file)
        return jr(rooms, safe=False)
    else:
        return rp('The method must be Get!')


def rcvTrans(request):
    """
    Método que recebe a transação contendo a requisição para do servidor coordenador
    :param request: Requisição recebida via WebService
    :return:    Lista representando a resposta do pedido de transação,
                Lista vazia para Não e Lista preenchida pra Sim
    """
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
        else:
            trans.status = Status.Aborted

        trans.log()
        return jr(result, safe=False)
    else:
        return rp('The method must be Get!')


def done(request):
    """
    Método que recebe a confirmação de efetivação da transação
    :param request: Requisição recebida via WebService
    :return: None
    """

    if request.method == 'GET':
        with open("hotel.json.temp", 'r') as file:
            tickets = json.load(file)

        with open("hotel.json", 'w') as file:
            file.write(json.dumps(tickets, indent=4))
        os.remove("hotel.json.temp")
        return rp("Ok")


def abort(request):
    """
    Método que recebe
    :param request: Requisição recebida via WebService
    :return:
    """

    if request.method == 'GET':
        os.remove("hotel.json.temp")
        return rp("Ok")
