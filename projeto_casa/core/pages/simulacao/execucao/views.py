from django.shortcuts import render, redirect
from core.models import *
from django.http import JsonResponse
from datetime import date, timedelta

tempo = None
comodos = None

def Executar(request):
    casa_id = request.GET.get('casa_id')
    grupo_id = request.GET.get('grupo_id')
    minutos = request.GET.get('tempo')

    if casa_id and minutos and grupo_id:
        global tempo
        global comodos

        casa = Casa.objects.filter(id=casa_id).first()
        grupo = GrupoCoeficiente.objects.filter(id=grupo_id).first()
        tempo = minutos

        comodos = Comodo.objects.filter(casa=casa)
        getComodos(comodos, grupo)

        consumos = {
            'titulos': tituloComodos(comodos),
            'gastos': calcularConsumo(getSemana(1), 0)
        }

        dados = {
            'titulo': 'Simular com teporizador',
            'casa': casa,
            'tempo': tempo,
            'consumos': consumos
        }

        return render(request, 'simulacao/execucao/temporizador.html', dados)   

    return redirect("/simular/casas/")

def getComodos(comodos, grupo):
    for comodo in comodos:
        comodo.energia_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=True).first()
        comodo.agua_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=True).first()
        comodo.energia_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=False).first()
        comodo.agua_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=False).first()

def getSemana(dia):
    data = convert_data(int(dia))
    semana = data.weekday()

    print("data {} semana {}".format(data, (semana < 5)))

    return semana < 5

def tituloComodos(comodos):
    lista = []
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

    consumo = calcularConsumo(getSemana(dia), hora)

    return JsonResponse({"consumo": 5}, status=200)

def calcularConsumo(semana, hora):
    return []