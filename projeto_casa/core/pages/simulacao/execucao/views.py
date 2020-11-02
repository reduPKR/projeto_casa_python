from django.shortcuts import render, redirect
from core.models import *
from django.http import JsonResponse
from datetime import date, timedelta
import math
import random

tempo = None
comodos = None
meta = None

def Executar(request):
    casa_id = request.GET.get('casa_id')
    grupo_id = request.GET.get('grupo_id')
    meta_id = request.GET.get('meta_id')
    minutos = request.GET.get('tempo')

    if casa_id and minutos and grupo_id:
        global tempo
        global comodos
        global meta

        casa = Casa.objects.filter(id=casa_id).first()
        comodos = preencherComodos(casa, grupo_id)
        meta = MetaTreino.objects.filter(id=meta_id).first()
        tempo = minutos

        lista = []
        lista.append(gerarConsumo(1, 0))
        consumos = {
            'titulos': tituloComodos(comodos),
            'gastos': lista
        }

        dados = {
            'titulo': 'Simular com teporizador',
            'casa': casa,
            'tempo': tempo,
            'consumos': consumos
        }

        return render(request, 'simulacao/execucao/temporizador.html', dados)   

    return redirect("/simular/casas/")

def preencherComodos(casa, grupo_id):
    grupo = GrupoCoeficiente.objects.filter(id=grupo_id).first()

    comodos = Comodo.objects.filter(casa=casa)
    getComodos(comodos, grupo)
    getTerminais(comodos)
    return comodos

def getComodos(comodos, grupo):
    for comodo in comodos:
        comodo.energia_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=True).first()
        comodo.agua_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=True).first()
        comodo.energia_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=False).first()
        comodo.agua_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=False).first()

def getTerminais(comodos):
    for comodo in comodos:
        comodo.comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)


def getSemana(dia):
    data = convert_data(int(dia))
    semana = data.weekday()

    return semana < 5

def tituloComodos(comodos):
    lista = []
    lista.append("Data")
    lista.append("Hora")
    for item in comodos:
        lista.append(item.nome)
    return lista

def convert_data(dia):
    #nao achei nada pronto, fiz da maneira raiz
    data = date(2019,1,1)

    dia = dia - 1
    while dia > 0:
        data = data + timedelta(days=1)
        dia = dia - 1
    return data

def ler_dados(request):
    hora = request.GET.get("hora")
    dia = request.GET.get("dia")

    consumo = gerarConsumo(dia, hora)

    return JsonResponse({"consumo": 5}, status=200)

def gerarConsumo(dia, hora):
    global comodos
    semana = getSemana(dia)
    data = convert_data(int(dia))

    consumos = []
    consumos.append(data)
    consumos.append("{}:00".format(hora))
    for comodo in comodos:
        registradas = []

        consumoAgua = consumoEnergia = 0
        for terminal in comodo.comodoSaidas:
            if terminal.comodo_equipamento and terminal.comodo_equipamento.equipamento:
                if terminal.comodo_equipamento not in registradas:
                    if semana < 5:
                        min = math.ceil(terminal.tempo_min_semana / 5)
                        max = math.ceil(terminal.tempo_max_semana / 5)
                    else:
                        min = math.ceil(terminal.tempo_min_feriado / 2)
                        max = math.ceil(terminal.tempo_max_feriado / 2)

                    qtde = math.ceil(((min + max) / 2) / 60)
                    if qtde == 0:
                        qtde = 1
                    min = math.ceil(min / qtde)
                    max = math.ceil(max / qtde)

                    x = random.randint(0, 100)
                    if terminal.comodo_equipamento.equipamento.tipo_equipamento.id == 4:  # Valor direto (Iluminação)
                        # luz acessa ate 0 horas depois as 6 da manha
                        if hora > 0 and hora < 6:
                            probabilidade = 5
                        elif hora > 6 and hora < 19:
                            probabilidade = 2
                        else:
                            probabilidade = 93
                    else:
                        probabilidade = ((qtde * 100) / 24)
                        if hora > 0 and hora < 6:
                            probabilidade = probabilidade / 2
                        else:
                            probabilidade = probabilidade * 2

                    if x <= probabilidade:
                        tempo = abs(random.randint(min, max))

                        qtde = qtde - 1

                        if terminal.comodo_equipamento.equipamento.tipo_consumo.id == 1:
                            consumoAgua += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, tempo)
                        elif terminal.comodo_equipamento.equipamento.tipo_consumo.id == 2:
                            consumoEnergia += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, tempo)
                        else:
                            consumoAgua += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, tempo)
                            consumoEnergia += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, tempo)


        consumos.append(index(consumoEnergia,semana,True))
        # consumos.append(index(consumoAgua, semana, False))

    return consumos

def calcularConsumo(consumoHora, tempo):
    return (consumoHora / 60) * tempo

def index(consumo, semana, energia):
    global meta

    if energia:
        if semana:
            energia = meta.reduzir_energia_semana
        else:
            energia = meta.reduzir_energia_feriado

        return categorias((consumo*100)/energia)
    else:
        if semana:
            agua = meta.reduzir_agua_semana
        else:
            agua = meta.reduzir_agua_feriado
        return categorias((consumo * 100) / agua)

def categorias(valor):
    if valor == 0:
        return 0
    if valor < 35:
        return 1
    elif valor < 70:
        return 2
    elif valor < 105:
        return 3
    elif valor < 140:
        return 4
    else:
        return 5

