from django.shortcuts import render, redirect
from core.models import *

def ListaCoeficientes(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    casa = None
    mes = None
    if casa_id and mes_id:
        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'mes': mes,
        'coeficientes': []
    }

    return render(request, 'simulacao/regressao_linear/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def GerarCoefficientes(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    casa = None
    mes = None
    if casa_id and mes_id:
        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

        
