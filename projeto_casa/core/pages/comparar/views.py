from django.shortcuts import render
from core.models import *
import json
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

def SelecionarExecucao(request):
    casa_id = request.GET.get('casa_id')
    meta_id = request.GET.get('meta_id')

    if casa_id:
        casa = Casa.objects.get(id=casa_id)
        meta = MetaTreino.objects.get(id = meta_id)

        lista = GrupoCoeficiente.objects.filter(meta_treino=meta)

    dados = {
        'titulo':'Simular em execução',
        'casa': casa,
        'meta': meta,
        'lista': lista
    }

    return render(request, 'simulacao/execucao/selecionar.html',dados)

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
    comodos = getComodos(casa,reg)
    analise(meta,mlr_precisao, mlr_tempo, comodos)
    #analisarConsumo(comodos)

    gen_precisao = []
    gen_tempo = []
    gen = GrupoCoeficiente.objects.get(id=genetico_id)
    comodos = getComodos(casa,gen)
    analise(meta,gen_precisao, gen_tempo, comodos)

    lista_mlr = []
    lista_gen = []
    i = 0
    while i < 12:
        mes = getMes(i)
        lista_mlr.append({"mes": mes, "precisao": mlr_precisao[i], "tempo": mlr_tempo[i]})
        lista_gen.append({"mes": mes, "precisao": gen_precisao[i], "tempo": gen_tempo[i]})
        i += 1
    lista_mlr.append({"mes": "Media", "precisao": mlr_precisao[i], "tempo": mlr_tempo[i]})
    lista_gen.append({"mes": "Media", "precisao": gen_precisao[i], "tempo": gen_tempo[i]})

    regressao = {"treino": converter(reg.tempo_treino), "lista": lista_mlr}
    genetico = {"treino": converter(gen.tempo_treino), "lista": lista_gen}
    
    dados = {
        'titulo':'Comparações', 
        'casa': casa,
        'meta': meta,
        'regressao': regressao,
        'genetico': genetico,
        'grafico_comp_regressao': json.dumps(mlr_precisao),
        'grafico_comp_generico': json.dumps(gen_precisao),
        'meses': json.dumps(['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'])
    }
    return render(request, 'simulacao/comparar/resultado.html', dados)

def getComodos(casa, grupo):
    comodos = Comodo.objects.filter(casa=casa)
    for comodo in comodos:
        comodo.energia_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=True).first()
        comodo.agua_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=True).first()
        comodo.energia_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=False).first()
        comodo.agua_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=False).first()
    
    return comodos

def analise(meta,precisao,tempo, comodos):
    if comodos:
        month = 0
        
        media_tempo = 0
        media_precisao = 0
        while month < 12:
            climas = Clima.objects.filter(data__month=(month+1))
            for comodo in comodos:
                comodo.resultados = ComodoValorY.objects.filter(comodo=comodo,meta=meta,data__month=(month+1))
            total = 0
            acerto = 0
            ini = time.time()
            for comodo in comodos:
                for resultado in comodo.resultados: 
                    clima = filter(lambda clima: resultado.data == clima.data and resultado.hora == clima.hora, climas)
                    for item in clima:
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
            
            fim = time.time()
            precisao.append(round((acerto*100)/total,2))
            tempo.append(round(fim-ini,2))
            media_precisao += ((acerto*100)/total)
            media_tempo += fim-ini

            month += 1
        precisao.append(round(media_precisao/12,2)) 
        tempo.append(round(media_tempo/12,2))

def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]

def converter(tempo):
    if tempo < 1:
        return "00:00:00:{}".format(round(tempo,2))
    elif tempo < 60:
        seg = int(tempo)
        ms = int(tempo*100%100)
        return "00:00:{}:{}".format(seg,ms)
    elif tempo < 3600:
        tempo /= 60
        minutos = int(tempo)

        tempo *= 100
        seg = int(tempo%100)
        
        tempo -= seg
        ms = int(tempo*100%100)
        return "00:{}:{}:{}".format(minutos,seg,ms)