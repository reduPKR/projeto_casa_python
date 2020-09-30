from django.shortcuts import render, redirect
from core.models import *
from datetime import date
import random
import time

genes = 15000
percParada = 95
casa = None
mes = None
meta = None
listaComodos = []
listaSemana = []
listaFinalSemana = []


def Exibir(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        global casa
        global mes

        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

        metas = MetaTreino.objects.filter(
            casa = casa,
            mes = mes.mes
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
        'titulo':'Algoritmo genetico', 
        'casa': casa,
        'mes': mes,
        'metas': metas,
    }

    return render(request, 'simulacao/genetico/menu.html',dados)

def genetico(request):
    global casa
    global mes
    global listaComodos
    global meta

    if casa:
        listaComodos.clear()
        
        meta_id = request.POST.get('meta_id')
        acao = int(request.POST.get('acao'))

        meta = MetaTreino.objects.get(id=meta_id)

        if acao == 0:
            gerar1()
        else:
            gerar2(acao)
        
        gerarAnalise()
        executarGenetico()
        
    return redirect('/simular/meses/?id={}'.format(casa.id))

def sortearValor():
    lista = []
    i = 0

    misto = random.randint(0,10) #evita ter valores muito embaralhados
    while i < 5:
        if misto == 0 or i == 0:
            tipo = random.randint(0,100)
            val = random.randint(0,100)
       
        if val != 99:
            if tipo < 60:
                lista.append(random.random())
            elif tipo < 95:
                lista.append((random.random()*10))
            else:
                lista.append((random.random()*100))
        else:
            if tipo < 60:
                lista.append(random.random()*-1)
            elif tipo < 95:
                lista.append((random.random()*-10))
            else:
                lista.append((random.random()*-100))
        i += 1
    
    return {'acerto': 0, 'temperatura': lista[0] , 'umidade': lista[1] , 'vento': lista[2] , 'pressao': lista[3] , 'chuva': lista[4] }

def gerar1():
    global genes

    comodos = Comodo.objects.filter(casa=casa)
    pos = 0
    while pos < comodos.count():
        lista = []
        energia_semana = []
        energia_feriado = []
        agua_semana = []
        agua_feriado = []

        for i in range(genes):
            valores = sortearValor()

            energia_semana.append(valores)
            energia_feriado.append(valores)
            agua_semana.append(valores)
            agua_feriado.append(valores)
            
        listaComodos.append({
            'energia_semana': energia_semana,
            'energia_feriado': energia_feriado,
            'agua_semana': agua_semana,
            'agua_feriado': agua_feriado
        })

        pos += 1

def gerar2(qtde):
    global casa
    global meta
    global genes

    if casa:
        comodos = Comodo.objects.filter(casa=casa)
        pos = 0
        while pos < comodos.count():
            lista = []
            energia_semana = []
            energia_feriado = []
            agua_semana = []
            agua_feriado = []

            comodo = comodos[pos]

            grupos = GrupoCoeficiente.objects.filter(meta_treino = meta)
            for grupo in grupos:
                coeficientes = Coeficiente.objects.filter(comodo=comodo,grupo=grupo)

                for coeficiente in coeficientes:
                    if coeficiente.semana and coeficiente.energia:
                        energia_semana.append({'acerto': coeficiente.precisao, 'temperatura': coeficiente.temperatura , 'umidade': coeficiente.umidade , 'vento': coeficiente.vento , 'pressao': coeficiente.pressao , 'chuva': coeficiente.chuva })
                    elif coeficiente.semana and coeficiente.energia is False:
                        agua_semana.append({'acerto': coeficiente.precisao, 'temperatura': coeficiente.temperatura , 'umidade': coeficiente.umidade , 'vento': coeficiente.vento , 'pressao': coeficiente.pressao , 'chuva': coeficiente.chuva })
                    elif coeficiente.semana is False and coeficiente.energia:
                        energia_feriado.append({'acerto': coeficiente.precisao, 'temperatura': coeficiente.temperatura , 'umidade': coeficiente.umidade , 'vento': coeficiente.vento , 'pressao': coeficiente.pressao , 'chuva': coeficiente.chuva })
                    elif coeficiente.semana is False and coeficiente.energia is False:
                        agua_feriado.append({'acerto': coeficiente.precisao, 'temperatura': coeficiente.temperatura , 'umidade': coeficiente.umidade , 'vento': coeficiente.vento , 'pressao': coeficiente.pressao , 'chuva': coeficiente.chuva })

            energia_semana = sorted(energia_semana, key=lambda row:row['acerto'], reverse=True)
            agua_semana = sorted(agua_semana, key=lambda row:row['acerto'], reverse=True)
            energia_feriado = sorted(energia_feriado, key=lambda row:row['acerto'], reverse=True)
            agua_feriado = sorted(agua_feriado, key=lambda row:row['acerto'], reverse=True)

            while len(energia_semana) > qtde:
                energia_semana.pop()
                agua_semana.pop()
                energia_feriado.pop()
                agua_feriado.pop()
                
            dados = genes - len(energia_semana)
            for i in range(dados):
                valores = sortearValor()

                energia_semana.append(valores)
                energia_feriado.append(valores)
                agua_semana.append(valores)
                agua_feriado.append(valores)
            
            listaComodos.append({
                'energia_semana': energia_semana,
                'energia_feriado': energia_feriado,
                'agua_semana': agua_semana,
                'agua_feriado': agua_feriado
            })
            pos += 1

def getPosMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses.index(mes)

def gerarAnalise():
    global casa
    global meta
    global listaSemana
    global listaFinalSemana
    
    if casa:
        month = getPosMes(mes.mes) + 1
        clima = Clima.objects.filter(data__month=month)
        
        comodos = Comodo.objects.filter(casa=casa)
        for comodo in comodos:
            resultSemana = []
            resultFinalSemana = []
            resultados = ComodoValorY.objects.filter(comodo=comodo,data__month=month)
            for resultado in resultados:                
                for item in clima:
                    if resultado.data == item.data and resultado.hora == item.hora:
                        if resultado.data.weekday() < 5:
                            resultSemana.append({
                                'energia': resultado.meta_energia,
                                'agua': resultado.meta_agua,
                                'temperatura': item.temperatura,
                                'umidade': item.umidade,
                                'vento': item.vento ,
                                'pressao': item.pressao,
                                'chuva': item.chuva
                            })
                        else:
                           resultFinalSemana.append({
                                'energia': resultado.meta_energia,
                                'agua': resultado.meta_agua,
                                'temperatura': item.temperatura,
                                'umidade': item.umidade,
                                'vento': item.vento ,
                                'pressao': item.pressao,
                                'chuva': item.chuva
                            })
            listaSemana.append(resultSemana)
            listaFinalSemana.append(resultFinalSemana)

def executarGenetico():
    pos = 0 #comodo
    perc = 0 #media de acerto de todos comodos
    geracao = 0 #vezes executadas

    ini = time.time()
    while pos < len(listaComodos):
        calcularAptidao(listaComodos[pos],listaSemana[pos],listaFinalSemana[pos])
        pos += 1
    while perc < percParada and geracao < 200:
        if geracao % 20 != 0:
            x = .1 #mantem 20% da populacao
        else:
            x = .01 #mantem 1%

        pos = 0
        while pos < len(listaComodos):
            selecao(listaComodos[pos], x) 
            cruzamento(listaComodos[pos])
            calcularAptidao(listaComodos[pos],listaSemana[pos],listaFinalSemana[pos]) 
            pos += 1
        perc = percentualGeral(listaComodos)
        geracao += 1
        print("Geraçao {} Tx. acerto {}".format(geracao,perc))
    fim = time.time()
    salvarResultados(listaComodos,perc, (fim-ini))

def calcularAptidao(comodo,listaSemana,listaFinalSemana):
    total = len(listaSemana)

    if comodo['energia_semana'][0]['acerto'] < 99:
        for item in comodo['energia_semana']:
            perc = acerto = 0
            for semana in listaSemana:        
                resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
                if semana['energia'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc
    
    if comodo['agua_semana'][0]['acerto'] < 99:
        for item in comodo['agua_semana']:
            perc = acerto = 0
            for semana in listaSemana:        
                resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
                if semana['agua'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc

    total = len(listaFinalSemana)

    if comodo['energia_feriado'][0]['acerto'] < 99:
        for item in comodo['energia_feriado']:
            perc = acerto = 0
            for final in listaFinalSemana:        
                resp = item['temperatura'] * final['temperatura'] + item['umidade'] * final['umidade'] + item['vento'] * final['vento'] + item['pressao'] * final['pressao'] + item['chuva'] * final['chuva']
                if final['energia'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc
    
    if comodo['agua_feriado'][0]['acerto'] < 99:
        for item in comodo['agua_feriado']:
            perc = acerto = 0
            for  final in listaFinalSemana:        
                resp = item['temperatura'] * final['temperatura'] + item['umidade'] * final['umidade'] + item['vento'] * final['vento'] + item['pressao'] * final['pressao'] + item['chuva'] * final['chuva']
                if final['agua'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc

    # comodo['energia_semana'] = sorted(comodo['energia_semana'], key=lambda row:row['acerto'], reverse=True)
    # comodo['agua_semana'] = sorted(comodo['agua_semana'], key=lambda row:row['acerto'], reverse=True)
    # comodo['energia_feriado'] = sorted(comodo['energia_feriado'], key=lambda row:row['acerto'], reverse=True)
    # comodo['agua_feriado'] = sorted(comodo['agua_feriado'], key=lambda row:row['acerto'], reverse=True)

def selecao(comodo,perc):
    global genes 

    comodo['energia_semana'] = sorted(comodo['energia_semana'], key=lambda row:row['acerto'], reverse=True)
    comodo['agua_semana'] = sorted(comodo['agua_semana'], key=lambda row:row['acerto'], reverse=True)
    comodo['energia_feriado'] = sorted(comodo['energia_feriado'], key=lambda row:row['acerto'], reverse=True)
    comodo['agua_feriado'] = sorted(comodo['agua_feriado'], key=lambda row:row['acerto'], reverse=True)

    if comodo['energia_semana'][0]['acerto'] < 99 and comodo['agua_semana'][0]['acerto'] < 99 and comodo['energia_feriado'][0]['acerto'] < 99 and comodo['agua_feriado'][0]['acerto'] < 99:
        while len(comodo['energia_semana']) > genes * perc:
            comodo['energia_semana'].pop()
            comodo['agua_semana'].pop()
            comodo['energia_feriado'].pop()
            comodo['agua_feriado'].pop()
    else:
        if comodo['energia_semana'][0]['acerto'] < 99:
            while len(comodo['energia_semana']) > genes * perc:
                comodo['energia_semana'].pop()

        if comodo['agua_semana'][0]['acerto'] < 99:
            while len(comodo['agua_semana']) > genes * perc:
                comodo['agua_semana'].pop()

        if comodo['energia_feriado'][0]['acerto'] < 99:
            while len(comodo['energia_feriado']) > genes * perc:
                comodo['energia_feriado'].pop()
        
        if comodo['agua_feriado'][0]['acerto'] < 99:
            while len(comodo['agua_feriado']) > genes * perc:
                comodo['agua_feriado'].pop()
        
def cruzamento(comodo):
    global genes

    #Energia semana
    cromosomos = []
    if comodo['energia_semana'][0]['acerto'] < 99:             
        cromosomos = comodo['energia_semana'].copy()
        while len(comodo['energia_semana']) > 0:
            pos = random.randint(0,len(comodo['energia_semana'])-1)
            gene1 = comodo['energia_semana'].pop(pos)

            pos = random.randint(0,len(comodo['energia_semana'])-1)
            gene2 = comodo['energia_semana'].pop(pos)

            filho1 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .6) + (gene2['temperatura'] * .4),
                'umidade': (gene1['umidade'] * .6) + (gene2['umidade'] * .4),
                'vento': (gene1['vento'] * .6) + (gene2['vento'] * .4),
                'pressao': (gene1['pressao'] * .6) + (gene2['pressao'] * .4),
                'chuva': (gene1['chuva'] * .6) + (gene2['chuva'] * .4)}

            filho2 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .4) + (gene2['temperatura'] * .6),
                'umidade': (gene1['umidade'] * .4) + (gene2['umidade'] * .6),
                'vento': (gene1['vento'] * .4) + (gene2['vento'] * .6),
                'pressao': (gene1['pressao'] * .4) + (gene2['pressao'] * .6),
                'chuva': (gene1['chuva'] * .4) + (gene2['chuva'] * .6)}
            
            chance = random.randint(0,1000)
            if chance == 999:
                mutacao(filho1)
            elif chance == 998:
                mutacao(filho2)

            cromosomos.append(filho1)
            cromosomos.append(filho2)

        comodo['energia_semana'] = cromosomos.copy()

    #agua semana
    if comodo['agua_semana'][0]['acerto'] < 99:
        cromosomos.clear()
        cromosomos = comodo['agua_semana'].copy()
        while len(comodo['agua_semana']) > 0:
            pos = random.randint(0,len(comodo['agua_semana'])-1)
            gene1 = comodo['agua_semana'].pop(pos)

            pos = random.randint(0,len(comodo['agua_semana'])-1)
            gene2 = comodo['agua_semana'].pop(pos)

            filho1 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .6) + (gene2['temperatura'] * .4),
                'umidade': (gene1['umidade'] * .6) + (gene2['umidade'] * .4),
                'vento': (gene1['vento'] * .6) + (gene2['vento'] * .4),
                'pressao': (gene1['pressao'] * .6) + (gene2['pressao'] * .4),
                'chuva': (gene1['chuva'] * .6) + (gene2['chuva'] * .4)}

            filho2 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .4) + (gene2['temperatura'] * .6),
                'umidade': (gene1['umidade'] * .4) + (gene2['umidade'] * .6),
                'vento': (gene1['vento'] * .4) + (gene2['vento'] * .6),
                'pressao': (gene1['pressao'] * .4) + (gene2['pressao'] * .6),
                'chuva': (gene1['chuva'] * .4) + (gene2['chuva'] * .6)}

            chance = random.randint(0,1000)
            if chance == 999:
                mutacao(filho1)
            elif chance == 998:
                mutacao(filho2)


            cromosomos.append(filho1)
            cromosomos.append(filho2)

        comodo['agua_semana'] = cromosomos.copy()

    #Energia final de semana
    if comodo['energia_feriado'][0]['acerto'] < 99:
        cromosomos.clear() 
        cromosomos = comodo['energia_feriado'].copy()
        while len(comodo['energia_feriado']) > 0:
            pos = random.randint(0,len(comodo['energia_feriado'])-1)
            gene1 = comodo['energia_feriado'].pop(pos)

            pos = random.randint(0,len(comodo['energia_feriado'])-1)
            gene2 = comodo['energia_feriado'].pop(pos)

            filho1 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .6) + (gene2['temperatura'] * .4),
                'umidade': (gene1['umidade'] * .6) + (gene2['umidade'] * .4),
                'vento': (gene1['vento'] * .6) + (gene2['vento'] * .4),
                'pressao': (gene1['pressao'] * .6) + (gene2['pressao'] * .4),
                'chuva': (gene1['chuva'] * .6) + (gene2['chuva'] * .4)}

            filho2 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .4) + (gene2['temperatura'] * .6),
                'umidade': (gene1['umidade'] * .4) + (gene2['umidade'] * .6),
                'vento': (gene1['vento'] * .4) + (gene2['vento'] * .6),
                'pressao': (gene1['pressao'] * .4) + (gene2['pressao'] * .6),
                'chuva': (gene1['chuva'] * .4) + (gene2['chuva'] * .6)}

            chance = random.randint(0,1000)
            if chance == 999:
                mutacao(filho1)
            elif chance == 998:
                mutacao(filho2)

            cromosomos.append(filho1)
            cromosomos.append(filho2)

        comodo['energia_feriado'] = cromosomos.copy()

    #Agua final de semana
    if comodo['agua_feriado'][0]['acerto'] < 99:
        cromosomos.clear()
        cromosomos = comodo['agua_feriado'].copy()
        while len(comodo['agua_feriado']) > 0:
            pos = random.randint(0,len(comodo['agua_feriado'])-1)
            gene1 = comodo['agua_feriado'].pop(pos)

            pos = random.randint(0,len(comodo['agua_feriado'])-1)
            gene2 = comodo['agua_feriado'].pop(pos)

            filho1 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .6) + (gene2['temperatura'] * .4),
                'umidade': (gene1['umidade'] * .6) + (gene2['umidade'] * .4),
                'vento': (gene1['vento'] * .6) + (gene2['vento'] * .4),
                'pressao': (gene1['pressao'] * .6) + (gene2['pressao'] * .4),
                'chuva': (gene1['chuva'] * .6) + (gene2['chuva'] * .4)}

            filho2 = {'acerto': 0, 
                'temperatura': (gene1['temperatura'] * .4) + (gene2['temperatura'] * .6),
                'umidade': (gene1['umidade'] * .4) + (gene2['umidade'] * .6),
                'vento': (gene1['vento'] * .4) + (gene2['vento'] * .6),
                'pressao': (gene1['pressao'] * .4) + (gene2['pressao'] * .6),
                'chuva': (gene1['chuva'] * .4) + (gene2['chuva'] * .6)}

            chance = random.randint(0,1000)
            if chance == 999:
                mutacao(filho1)
            elif chance == 998:
                mutacao(filho2)

            cromosomos.append(filho1)
            cromosomos.append(filho2)

        comodo['agua_feriado'] = cromosomos.copy()

    completarPopulacao(comodo)

def completarPopulacao(comodo):
    global genes

    while len(comodo['energia_semana']) < genes and comodo['energia_semana'][0]['acerto'] < 99:
        valores = sortearValor()
        comodo['energia_semana'].append(valores)
    
    while len(comodo['agua_semana']) < genes and comodo['agua_semana'][0]['acerto'] < 99:
        valores = sortearValor()
        comodo['agua_semana'].append(valores)

    while len(comodo['energia_feriado']) < genes and comodo['energia_feriado'][0]['acerto'] < 99:
        valores = sortearValor()
        comodo['energia_feriado'].append(valores)
    
    while len(comodo['agua_feriado']) < genes and comodo['agua_feriado'] [0]['acerto'] < 99:
        valores = sortearValor()
        comodo['agua_feriado'].append(valores)

def percentualGeral(listaComodos):
    total = 0
    pos = 0
    while pos < len(listaComodos):
        comodo = listaComodos[pos]

        total += float(comodo['energia_semana'][0]['acerto'])
        total += float(comodo['agua_semana'][0]['acerto'])
        total += float(comodo['energia_feriado'][0]['acerto'])
        total += float(comodo['agua_feriado'][0]['acerto'])
        
        pos += 1
    
    return total / (len(listaComodos)*4)
        
def mutacao(filho):
    gene = random.randint(0,5)
    tipo = random.randint(0,10)


    if gene == 0:
        if tipo != 0:
            filho['temperatura'] = filho['temperatura'] + random.random()
        else:
            filho['temperatura'] = filho['temperatura'] - random.random()
    elif gene == 1:
        if tipo != 0:
            filho['umidade'] = filho['umidade'] + random.random()
        else:
            filho['umidade'] = filho['umidade'] - random.random()
    elif gene == 2:
        if tipo != 0:
            filho['vento'] = filho['vento'] + random.random()
        else:
            filho['vento'] = filho['vento'] - random.random()
    elif gene == 3:
        if tipo != 0:
            filho['pressao']  = filho['pressao'] + random.random()
        else:
            filho['pressao']  = filho['pressao'] - random.random()
    else:
        if tipo != 0:
            filho['chuva'] = filho['chuva'] + random.random()
        else:
            filho['chuva'] = filho['chuva'] - random.random()
        
def salvarResultados(listaComodos,perc,tempo):
    global meta
    global casa

    novo = GrupoCoeficiente.objects.create(
        meta_treino = meta,
        gerador = "Algoritmo genetico",
        precisao = perc,
        tempo_treino= tempo
    )
    
    comodos = Comodo.objects.filter(casa=casa)
    pos = 0
    for comodo in comodos:
        dados = listaComodos[pos]

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = novo,
            precisao = dados['energia_semana'][0]['acerto'],
            energia =True,
            semana = True,
            temperatura = dados['energia_semana'][0]['temperatura'],
            umidade = dados['energia_semana'][0]['umidade'],
            vento = dados['energia_semana'][0]['vento'],
            pressao = dados['energia_semana'][0]['pressao'],
            chuva = dados['energia_semana'][0]['chuva']
        )

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = novo,
            precisao = dados['agua_semana'][0]['acerto'],
            energia = False,
            semana = True,
            temperatura = dados['agua_semana'][0]['temperatura'],
            umidade = dados['agua_semana'][0]['umidade'],
            vento = dados['agua_semana'][0]['vento'],
            pressao = dados['agua_semana'][0]['pressao'],
            chuva = dados['agua_semana'][0]['chuva']
        )

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = novo,
            precisao = dados['energia_feriado'][0]['acerto'],
            energia =True,
            semana = False,
            temperatura = dados['energia_feriado'][0]['temperatura'],
            umidade = dados['energia_feriado'][0]['umidade'],
            vento = dados['energia_feriado'][0]['vento'],
            pressao = dados['energia_feriado'][0]['pressao'],
            chuva = dados['energia_feriado'][0]['chuva']
        )

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = novo,
            precisao = dados['agua_feriado'][0]['acerto'],
            energia = False,
            semana = False,
            temperatura = dados['agua_feriado'][0]['temperatura'],
            umidade = dados['agua_feriado'][0]['umidade'],
            vento = dados['agua_feriado'][0]['vento'],
            pressao = dados['agua_feriado'][0]['pressao'],
            chuva = dados['agua_feriado'][0]['chuva']
        )
        pos += 1

