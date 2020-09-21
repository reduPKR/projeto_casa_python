from django.shortcuts import render, redirect
from core.models import *
from datetime import date

casa = None
mes = None

def Exibir(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        global casa
        global mes

        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

        data = date.today()
        data = data.replace(day=1)
        data = data.replace(year=2019)
        comodo = Comodo.objects.filter(casa=casa).first();
        comodoY = ComodoValorY.objects.filter(comodo=comodo,data=data).first()
        if comodoY == None:
            executar = True
        else:
            executar = False

        dados = {
            'titulo':'Algoritmo genetico', 
            'casa': casa,
            'mes': mes,
            'executar': executar
        }


    return render(request, 'simulacao/genetico/menu.html',dados)