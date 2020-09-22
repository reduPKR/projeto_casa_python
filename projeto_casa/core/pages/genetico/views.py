from django.shortcuts import render, redirect
from core.models import *
from datetime import date
import random
import time

genes = 1000
percParada = 90
casa = None
mes = None
grupo = None
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

        data = date.today()
        data = data.replace(day=1)
        data = data.replace(year=2019)
        comodo = Comodo.objects.filter(casa=casa).first();
        comodoY = ComodoValorY.objects.filter(comodo=comodo,data=data).first()
        if comodoY == None:
            executar = True
        else:
            executar = False

        grupos = GrupoCoeficiente.objects.filter(casa=casa)
        for grupo in grupos:
            grupo.reduzir_energia_semana = round(grupo.reduzir_energia_semana/1000,2)
            grupo.reduzir_energia_feriado = round(grupo.reduzir_energia_feriado /1000,2)

        dados = {
            'titulo':'Algoritmo genético', 
            'casa': casa,
            'mes': mes,
            'executar': executar,
            'grupos': grupos
        }


    return render(request, 'simulacao/genetico/menu.html',dados)

def genetico(request):
    global casa
    global mes
    global listaComodos
    global grupo

    if casa:
        listaComodos.clear()
        
        grupo_id = request.POST.get('grupo_id')
        acao = int(request.POST.get('acao'))

        grupo = GrupoCoeficiente.objects.get(id=grupo_id)
        if acao == 0:
            gerar1()
        else:
            gerar2(acao)
        
        gerarAnalise()
        ini = time.time()
        executarGenetico()
        fim = time.time()
        print("Tempo {}".format(fim-ini))

    return redirect('/genetico/?casa_id=1&mes_id=1')

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
            tipo = random.randint(0,10)

            if tipo < 5:
                valores = {'acerto': 0, 'temperatura': random.random() , 'umidade': random.random() , 'vento': random.random() , 'pressao': random.random() , 'chuva': random.random() }
            elif tipo < 8:
                valores = {'acerto': 0, 'temperatura': random.random() * 10 , 'umidade': random.random() * 10 , 'vento': random.random() * 10 , 'pressao': random.random() * 10 , 'chuva': random.random() * 10 }
            else:
                valores = {'acerto': 0, 'temperatura': random.random() * 100 , 'umidade': random.random() * 100 , 'vento': random.random() * 100 , 'pressao': random.random() * 100 , 'chuva': random.random() * 100 }

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
    global grupo
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
                tipo = random.randint(0,10)
                if tipo < 5:
                    valores = {'acerto': 0, 'temperatura': random.random(), 'umidade': random.random(), 'vento': random.random() , 'pressao': random.random() , 'chuva': random.random()}
                elif tipo < 8:
                    valores = {'acerto': 0, 'temperatura': random.random() * 10 , 'umidade': random.random() * 10 , 'vento': random.random() * 10 , 'pressao': random.random() * 10 , 'chuva': random.random() * 10 }
                else:
                    valores = {'acerto': 0, 'temperatura': random.random() * 100 , 'umidade': random.random() * 100 , 'vento': random.random() * 100 , 'pressao': random.random() * 100 , 'chuva': random.random() * 100 }

                
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
    global grupo
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

    while perc < percParada and geracao < 100:
        while pos < len(listaComodos):
            calcularAptidao(listaComodos[pos],listaSemana[pos],listaFinalSemana[pos])
            selecao(listaComodos[pos]) #elimina 50% com piores reultados
            cruzamento(listaComodos[pos])

            pos += 1
        perc = percentualGeral(listaComodos)
        geracao += 1
        pos = 0
        print("Geraçao {} Tx. acerto{}".format(geracao,perc))

def calcularAptidao(comodo,listaSemana,listaFinalSemana):
    total = len(listaSemana)
    if comodo['energia_semana'][0]['acerto'] > percParada:
        for item in comodo['energia_semana']:
            perc = acerto = 0

            for semana in listaSemana:        
                resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
                if semana['energia'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc
    
    if comodo['agua_semana'][0]['acerto'] > percParada:
        for item in comodo['agua_semana']:
            perc = acerto = 0
            for semana in listaSemana:        
                resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
                if semana['agua'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc

    total = len(listaFinalSemana)

    if comodo['energia_feriado'][0]['acerto'] > percParada:
        for item in comodo['energia_feriado']:
            perc = acerto = 0
            for final in listaFinalSemana:        
                resp = item['temperatura'] * final['temperatura'] + item['umidade'] * final['umidade'] + item['vento'] * final['vento'] + item['pressao'] * final['pressao'] + item['chuva'] * final['chuva']
                if semana['energia'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc
    
    if comodo['agua_feriado'][0]['acerto'] > percParada:
        for item in comodo['agua_feriado']:
            perc = acerto = 0
            for  final in listaFinalSemana:        
                resp = item['temperatura'] * final['temperatura'] + item['umidade'] * final['umidade'] + item['vento'] * final['vento'] + item['pressao'] * final['pressao'] + item['chuva'] * final['chuva']
                if semana['agua'] == round(resp):
                    acerto += 1
            perc = acerto * 100 / total
            item['acerto'] = perc

    comodo['energia_semana'] = sorted(comodo['energia_semana'], key=lambda row:row['acerto'], reverse=True)
    comodo['agua_semana'] = sorted(comodo['agua_semana'], key=lambda row:row['acerto'], reverse=True)
    comodo['energia_feriado'] = sorted(comodo['energia_feriado'], key=lambda row:row['acerto'], reverse=True)
    comodo['agua_feriado'] = sorted(comodo['agua_feriado'], key=lambda row:row['acerto'], reverse=True)

def selecao(comodo):
    global genes

    while len(comodo['energia_semana']) > genes * .4:
        comodo['energia_semana'].pop()
        comodo['agua_semana'].pop()
        comodo['energia_feriado'].pop()
        comodo['agua_feriado'].pop()
        
def cruzamento(comodo):
    global genes

    cromosomos = comodo['energia_semana'].copy()
    #Energia semana
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

        cromosomos.append(filho1)
        cromosomos.append(filho2)

    comodo['energia_semana'] = cromosomos.copy()

    #agua semana
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

        cromosomos.append(filho1)
        cromosomos.append(filho2)

    comodo['agua_semana'] = cromosomos.copy()

    #Energia final de semana
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

        cromosomos.append(filho1)
        cromosomos.append(filho2)

    comodo['energia_feriado'] = cromosomos.copy()

    #Agua final de semana
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

        cromosomos.append(filho1)
        cromosomos.append(filho2)

    comodo['agua_feriado'] = cromosomos.copy()

    while len(comodo['energia_semana']) < genes:
        tipo = random.randint(0,10)

        if tipo < 5:
            valores = {'acerto': 0, 'temperatura': random.random() , 'umidade': random.random() , 'vento': random.random() , 'pressao': random.random() , 'chuva': random.random() }
        elif tipo < 8:
            valores = {'acerto': 0, 'temperatura': random.random() * 10 , 'umidade': random.random() * 10 , 'vento': random.random() * 10 , 'pressao': random.random() * 10 , 'chuva': random.random() * 10 }
        else:
            valores = {'acerto': 0, 'temperatura': random.random() * 100 , 'umidade': random.random() * 100 , 'vento': random.random() * 100 , 'pressao': random.random() * 100 , 'chuva': random.random() * 100 }

        comodo['energia_semana'].append(valores)
        comodo['agua_semana'].append(valores)
        comodo['energia_feriado'].append(valores)
        comodo['agua_feriado'].append(valores)

def percentualGeral(listaComodos):
    total = 0
    pos = 0
    while pos < len(listaComodos):
        comodo = listaComodos[pos]

        total += comodo['energia_semana'][0]['acerto']
        total += comodo['agua_semana'][0]['acerto']
        total += comodo['energia_feriado'][0]['acerto']
        total += comodo['agua_feriado'][0]['acerto']
        
        pos += 1
    
    return total / (len(listaComodos)*4)
        