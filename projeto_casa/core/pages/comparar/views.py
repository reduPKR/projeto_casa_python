from django.shortcuts import render, redirect
from core.models import *
from datetime import date
import random
import time


def Exibir(request):
    casa_id = request.GET.get('casa_id')

    if casa_id:
        casa = Casa.objects.get(id=casa_id)

        metas = MetaTreino.objects.filter(
            casa = casa
        )

        for item in metas:
            item.reduzir_energia_semana = round(item.reduzir_energia_semana /1000) #converto para Kwh
            item.reduzir_energia_feriado = round(item.reduzir_energia_feriado /1000)
            
            grupo = GrupoCoeficiente.objects.filter(meta_treino = item, gerador = "Algoritmo genetico").first()
            
            if grupo is None:
                item.treino = False
            else:
                item.treino = True

    dados = {
        'titulo':'Comparacoes', 
        'casa': casa,
        'metas': metas,
    }

    return render(request, 'simulacao/comparar/menu.html',dados)

def Selecionar(request):
    casa_id = request.GET.get('casa_id')
    meta_id = request.GET.get('meta_id')

    if casa_id:
        casa = Casa.objects.get(id=casa_id)
        meta = MetaTreino.objects.get(id = meta_id)

        regressao = GrupoCoeficiente.objects.filter(meta_treino=meta, gerador = "Regresão linear").first()
        genetico = GrupoCoeficiente.objects.filter(meta_treino=meta, gerador = "Algoritmo genetico") 
        print(regressao)

    dados = {
        'titulo':'Comparações', 
        'casa': casa,
        'meta': meta,
        'regressao': regressao,
        'genetico': genetico
    }

    return render(request, 'simulacao/comparar/selecionar.html',dados)