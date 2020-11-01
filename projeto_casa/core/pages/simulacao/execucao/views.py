from django.shortcuts import render, redirect
from core.models import *
from django.http import JsonResponse

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

        dados = {
            'titulo': 'Simular com teporizador',
            'casa': casa,
            'tempo': tempo
        }

        return render(request, 'simulacao/execucao/temporizador.html', dados)   

    return redirect("/simular/casas/")

def getComodos(comodos, grupo):
    for comodo in comodos:
        comodo.energia_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=True).first()
        comodo.agua_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=True).first()
        comodo.energia_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=False).first()
        comodo.agua_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=False).first()

def ler_dados(request):
    hora = request.GET.get("hora")
    dia = request.GET.get("dia")

    


    return JsonResponse({"lista": 5}, status=200)
