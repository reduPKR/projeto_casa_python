from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }

    return render(request, 'simulacao/listarCasas.html', dados)

def ListarMeses(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        meses = ConsumoMes.objects.filter(casa=casa)

        for mes in meses:
            mes.energia = round((mes.energia/1000), 1)

    dados = {
        'titulo':'Meses cadastrados', 
        'casa':casa,
        'meses': meses
    }

    return render(request, 'simulacao/listarMeses.html',dados)

def Algoritmos(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

    dados = {
        'titulo':'Seleção de algoritmo', 
        'casa': casa,
        'mes': mes
    }

    return render(request, 'simulacao/algoritmos.html',dados)
