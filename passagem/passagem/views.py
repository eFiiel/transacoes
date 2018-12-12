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


def compraPass(org, dst, qtd, ida, tipo, volta=None):
    """

    :param org: Cidade de origem
    :param dst: Cidade de Destino
    :param qtd: Quantidade de Passagens
    :param ida: Data de Ida
    :param tipo: Tipo da compra: Passagem ou Pacote
    :param volta: Data da volta, se existente
    :return: Lista contendo as passagens compradas, se encontradas, senão apenas uma lista vazia
    """
    # coleta os dados de passagens
    with open('passagens.json') as f:
        tickets = json.load(f)
    #flags de confirmação
    idaFlag = False
    voltaFlag = False
    out = []
    if tipo == 1:
        file = 'passagens.json'
    if tipo == 2:
        file = 'passagens.json.temp'
    # Verificação da existencia da passagem
    for i in tickets:
        if i['origem'].casefold() == org.casefold() and not idaFlag:
            if i['destino'].casefold() == dst.casefold():
                if int(i['vagas']) > int(qtd):
                    if i['data'] == ida:
                        i['vagas'] -= int(qtd)
                        # adiciona a passgem encontrada em uma lista
                        out.append(i)
                        idaFlag = True
                        continue
    # Verifica a existencia da passagem de volta
    if volta and idaFlag:
        for i in tickets:
            if i['origem'].casefold() == dst.casefold() and not voltaFlag:
                if i['destino'].casefold() == org.casefold():
                    if int(i['vagas']) > int(qtd):
                        if i['data'] == volta:
                            i['vagas'] -= int(qtd)
                            # adiciona a passgem encontrada em uma lista
                            out.append(i)
                            voltaFlag = True

                            # Atualiza o arquivo
                            with open(file, 'w+') as file:
                                json.dump(tickets, file, indent=4)
                            return out
    if volta and not voltaFlag:
        out = []
    with open(file, 'w+') as file:
        json.dump(tickets, file, indent=4)
    # retorna a lista com a resposta
    return out


def CPpassagens(request):
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo os objetos encontrados
    """
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
    """

    :param request: Requisição recebida via WebService
    :return: Uma lista contendo todos os objetos da base de dados
    """
    if request.method == 'GET':
        with open("passagens.json") as file:
            tickets = json.load(file)
        return jr(tickets, safe=False)
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
        result = compraPass(org, dst, qtd, ida, 2, volta)
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
        with open("passagens.json.temp", 'r') as file:
            tickets = json.load(file)
        atual.status = Status.Done
        atual.log()
        with open("passagens.json", 'w') as file:
            file.write(json.dumps(tickets, indent=4))
        os.remove("passagens.json.temp")
        return rp("Ok")


def abort(request):
    """
    Método que recebe
    :param request: Requisição recebida via WebService
    :return:
    """
    if request.method == 'GET':
        os.remove("passagens.json.temp")
        atual.status = Status.Aborted
        atual.log()
        return rp("Ok")
