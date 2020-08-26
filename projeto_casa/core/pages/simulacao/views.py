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