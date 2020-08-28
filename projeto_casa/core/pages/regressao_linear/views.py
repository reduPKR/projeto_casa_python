from django.shortcuts import render, redirect
from core.models import *

casa = None
mes = None
def ListaCoeficientes(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        global casa
        global mes

        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

        energia = round(mes.energia/1000,2)
        agua = mes.agua

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'mes': mes,
        'energia': energia,
        'energia_min': round(energia/2, 2),
        'agua': agua,
        'agua_min': round(agua/2, 2),
        'coeficientes': None
    }

    return render(request, 'simulacao/regressao_linear/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def GerarCoeficientes(request):
    global casa
    global mes

    if casa and mes:
        print(casa)
        print(mes)

        energia = request.GET.get('energia')
        agua = request.GET.get('agua')
        
        print(energia)
        print(agua)


