from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import json
import copy


def CPpassagens(request):
    if request.method == 'GET':
        with open('passagens.json') as file:
            tickets = json.load(file)
        idaFlag = False
        voltaFlag =False
        org = request.GET.get('org', None)
        dst = request.GET.get('dst', None)
        qtd = request.GET.get('qtd', None)
        ida = request.GET.get('ida', None)
        volta = request.GET.get('volta', None)
        out = []
        if not (org and dst and ida and qtd):
            return rp('Faltou parâmetros')
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
                                break
        with open('passagens.json', 'w') as file:
            json.dump(tickets, file, indent=4)

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


