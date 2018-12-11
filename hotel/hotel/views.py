from django.http import HttpResponse as rp
from django.http import JsonResponse as jr
import json
import copy

def CPhosps(request):
    if request.method == 'GET':
        with open('hotel.json') as file:
            rooms = json.load(file)
        ct = request.GET.get('city', None).rstrip("\n")
        qts = int(request.GET.get('qts', None).rstrip("\n"))
        #pep = int(request.GET.get('people', None).rstrip("\n"))
        ent = request.GET.get('in', None).rstrip("\n")
        sai = request.GET.get('out', None).rstrip("\n")
        out = []
        diaent =int(ent.split("/")[0])
        diasai =int(sai.split("/")[0])
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
            with open('hotel.json', 'w') as file:
                json.dump(rooms, file, indent=4)

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
