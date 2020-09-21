from django.shortcuts import render, redirect
from core.models import *
from datetime import date
import random
import time

genes = 10
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

def gerarLista(request):
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
    repet = 0 #vezes executadas

    while perc < 90 and repet < 100:
        while pos < len(listaComodos):
            calcularAptidao(listaComodos[pos])
            selecao(listaComodos[pos]) #elimina 50% com piores reultados
            #cruzamento()

            pos += 1
        repet += 1

def calcularAptidao(comodo):
    global listaSemana
    global listaFinalSemana
    total = len(listaSemana)

    for item in comodo['energia_semana']:
        perc = acerto = 0
       
        if item['acerto'] >= 90:
            print(item)
            for semana in listaSemana:
                print(semana)
                resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
                print(round(resp))
            time.sleep(300)

        for semana in listaSemana:        
            resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
            if semana['energia'] == round(resp):
                acerto += 1
        perc = acerto * 100 / total
        item['acerto'] = perc
    
    for item in comodo['agua_semana']:
        perc = acerto = 0
        for semana in listaSemana:        
            resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
            if semana['energia'] == round(resp):
                acerto += 1
        perc = acerto * 100 / total
        item['acerto'] = perc

    for item in comodo['energia_feriado']:
        perc = acerto = 0
        for semana in listaSemana:        
            resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
            if semana['energia'] == round(resp):
                acerto += 1
        perc = acerto * 100 / total
        item['acerto'] = perc
    
    for item in comodo['agua_feriado']:
        perc = acerto = 0
        for semana in listaSemana:        
            resp = item['temperatura'] * semana['temperatura'] + item['umidade'] * semana['umidade'] + item['vento'] * semana['vento'] + item['pressao'] * semana['pressao'] + item['chuva'] * semana['chuva']
            if semana['energia'] == round(resp):
                acerto += 1
        perc = acerto * 100 / total
        item['acerto'] = perc
    

    # for item in comodo['energia_semana']:
    #     print(item)

    comodo['energia_semana'] = sorted(comodo['energia_semana'], key=lambda row:row['acerto'], reverse=True)
    comodo['agua_semana'] = sorted(comodo['agua_semana'], key=lambda row:row['acerto'], reverse=True)
    comodo['energia_feriado'] = sorted(comodo['energia_feriado'], key=lambda row:row['acerto'], reverse=True)
    comodo['agua_feriado'] = sorted(comodo['agua_feriado'], key=lambda row:row['acerto'], reverse=True)
 
    # for item in comodo['energia_semana']:
    #     print(item)
    # time.sleep(300)

def selecao(comodo):
    global genes

    while len(comodo['energia_semana']) > genes/2:
        comodo['energia_semana'].pop()
        comodo['agua_semana'].pop()
        comodo['energia_feriado'].pop()
        comodo['agua_feriado'].pop()
        
