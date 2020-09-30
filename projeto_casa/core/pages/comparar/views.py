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

    dados = {
        'titulo':'Comparações', 
        'casa': casa,
        'meta': meta,
        'regressao': regressao,
        'genetico': genetico
    }

    return render(request, 'simulacao/comparar/selecionar.html',dados)

def Comparar(request):
    casa_id = request.GET.get('casa_id')
    meta_id = request.GET.get('meta_id')
    mlr_id = request.GET.get('mlr_id')
    genetico_id = request.GET.get('genetico_id')

    casa = Casa.objects.get(id=casa_id)
    meta = MetaTreino.objects.get(id = meta_id)
    
    mlr_precisao = []
    mlr_tempo = []
    reg = GrupoCoeficiente.objects.get(id=mlr_id)
    analise(casa,meta, reg,mlr_precisao, mlr_tempo)

    gen_precisao = []
    gen_tempo = []
    gen = GrupoCoeficiente.objects.get(id=genetico_id)
    analise(casa,meta, gen,gen_precisao, gen_tempo)

    regressao = []
    genetico = []
    i = 0
    while i < 12:
        mes = getMes(i)
        regressao.append({"mes": mes, "precisao": mlr_precisao[i], "tempo": mlr_tempo[i]})
        genetico.append({"mes": mes, "precisao": gen_precisao[i], "tempo": gen_tempo[i]})
    
    dados = {
        'titulo':'Comparações', 
        'casa': casa,
        'meta': meta,
        'regressao': regressao,
        'genetico': genetico
    }
    return render(request, 'simulacao/comparar/resultados.html', dados)

def analise(casa,meta,grupo,precisao,tempo):

    if casa:
        month = 0
        comodos = Comodo.objects.filter(casa=casa)
        for comodo in comodos:
            comodo.energia_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=True).first()
            comodo.agua_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=True).first()
            comodo.energia_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=False).first()
            comodo.agua_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=False).first()

        while month < 12:
            clima = Clima.objects.filter(data__month=(month+1))
            for comodo in comodos:
                comodo.resultados = ComodoValorY.objects.filter(comodo=comodo,data__month=month)
                print(comodo.resultados)
            total = 0
            acerto = 0
            ini = time.time()
            print("\n\n\n")
            for comodo in comodos:
                print(comodo)
                for resultado in comodo.resultados:    
                    print(resultado)            
                    for item in clima:
                        print(item) 
                        if resultado.data == item.data and resultado.hora == item.hora:
                            if resultado.data.weekday() < 5:
                                energia = (item.temperatura * comodo.energia_semana.temperatura) + (item.umidade * comodo.energia_semana.umidade) + (item.vento * comodo.energia_semana.vento) + (item.pressao * comodo.energia_semana.pressao) + (item.chuva * comodo.energia_semana.chuva)
                                agua = (item.temperatura * comodo.agua_semana.temperatura) + (item.umidade * comodo.agua_semana.umidade) + (item.vento * comodo.agua_semana.vento) + (item.pressao * comodo.agua_semana.pressao) + (item.chuva * comodo.agua_semana.chuva)                                
                            else:
                                energia = (item.temperatura * comodo.energia_fim_semana.temperatura) + (item.umidade * comodo.energia_fim_semana.umidade) + (item.vento * comodo.energia_fim_semana.vento) + (item.pressao * comodo.energia_fim_semana.pressao) + (item.chuva * comodo.energia_fim_semana.chuva)
                                agua = (item.temperatura * comodo.agua_fim_semana.temperatura) + (item.umidade * comodo.agua_fim_semana.umidade) + (item.vento * comodo.agua_fim_semana.vento) + (item.pressao * comodo.agua_fim_semana.pressao) + (item.chuva * comodo.agua_fim_semana.chuva)

                            total += 2
                            if resultado.meta_energia == round(energia):
                                acerto += 1
                            if resultado.meta_agua == round(agua):
                                acerto += 1
                            print(total) 
                            print(acerto) 
            
            fim = time.time()
            precisao.append((acerto*100)/total)
            tempo.append(fim-ini)
            month += 1

def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]