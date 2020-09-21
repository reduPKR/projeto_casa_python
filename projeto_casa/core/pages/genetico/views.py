from django.shortcuts import render, redirect
from core.models import *
from datetime import date
import random

casa = None
mes = None
grupo = None
listaComodos = []
resultados = []
clima = []

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
            'titulo':'Algoritmo genetico', 
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
        
    return redirect('/genetico/?casa_id=1&mes_id=1')

def gerar1():
    comodos = Comodo.objects.filter(casa=casa)
    pos = 0
    while pos < comodos.count():
        lista = []
        energia_semana = []
        energia_feriado = []
        agua_semana = []
        agua_feriado = []

        for i in range(1000):
            valores = {'acerto': 0, 'temperatura': random.random() * 1000 , 'umidade': random.random() * 1000 , 'vento': random.random() * 1000 , 'pressao': random.random() * 1000 , 'chuva': random.random() * 1000 }
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
                valores = {'acerto': coeficiente.precisao, 'temperatura': coeficiente.temperatura , 'umidade': coeficiente.umidade , 'vento': coeficiente.vento , 'pressao': coeficiente.pressao , 'chuva': coeficiente.chuva }

                if coeficiente.semana and coeficiente.energia:
                    energia_semana.append(valores)
                elif coeficiente.semana and coeficiente.energia is False:
                    agua_semana.append(valores)
                elif coeficiente.semana is False and coeficiente.energia:
                    energia_feriado.append(valores)
                elif coeficiente.semana is False and coeficiente.energia is False:
                    agua_feriado.append(valores)

            energia_semana = sorted(energia_semana, key=lambda row:row['acerto'])
            agua_semana = sorted(agua_semana, key=lambda row:row['acerto'])
            energia_feriado = sorted(energia_feriado, key=lambda row:row['acerto'])
            agua_feriado = sorted(agua_feriado, key=lambda row:row['acerto'])

            total = energia_semana.count()
            #antes de continuar excluir dados ate o total ficar igual a qtde

            # dados = 1000 - total
            # for i in range(dados):
            #     valores = {'acerto': 0, 'temperatura': random.random() * 1000 , 'umidade': random.random() * 1000 , 'vento': random.random() * 1000 , 'pressao': random.random() * 1000 , 'chuva': random.random() * 1000 }
            #     energia_semana.append(valores)
            #     energia_feriado.append(valores)
            #     agua_semana.append(valores)
            #     agua_feriado.append(valores)

            # listaComodos.append({
            #     'energia_semana': energia_semana,
            #     'energia_feriado': energia_feriado,
            #     'agua_semana': agua_semana,
            #     'agua_feriado': agua_feriado
            # })
            pos += 1
