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
        mes.energia = round(mes.energia/1000,2)
        mes.energia_semana = round(mes.energia_semana/1000) #converto para Kwh
        mes.energia_feriado = round(mes.energia_feriado/1000)

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'mes': mes,
        'coeficientes': None,
        "agua_semana": round(mes.agua_semana/2,2),
        "agua_feriado": round(mes.agua_feriado/2,2),
        "energia_semana": round(mes.energia_semana/2), # energia kWh /2
        "energia_feriado": round(mes.energia_feriado/2)
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


