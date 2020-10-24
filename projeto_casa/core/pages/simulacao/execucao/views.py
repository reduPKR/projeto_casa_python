from django.shortcuts import render, redirect
from core.models import *
import math
from datetime import date
import time

casa = None
meta = None
tempo = None

def Executar(request):
    casa_id = request.GET.get('casa_id')
    meta_id = request.GET.get('meta_id')
    minutos = request.GET.get('tempo')

    if casa_id and meta_id and minutos:
        global casa
        global meta
        global tempo

        casa = casa_id
        meta = meta_id
        tempo = minutos

        dados = {
            'titulo': 'Simular com teporizador',
            'casa': casa,
            'tempo': tempo
        }

        return render(request, 'simulacao/execucao/temporizador.html', dados)

    return redirect("/simular/casas/")