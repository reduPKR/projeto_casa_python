from django.shortcuts import render, redirect
from core.models import *
from django.http import JsonResponse

casa = None
meta = None
tempo = None

def Executar(request):
    casa_id = request.GET.get('casa_id')
    meta_id = request.GET.get('meta_id')
    minutos = request.GET.get('tempo')

    if casa_id and meta_id and minutos:
        global casa
        global meta
        global tempo

        casa = Casa.objects.filter(id=casa_id).first()
        meta = MetaTreino.objects.filter(id=meta_id).first()
        tempo = minutos

        dados = {
            'titulo': 'Simular com teporizador',
            'casa': casa,
            'tempo': tempo
        }

        return render(request, 'simulacao/execucao/temporizador.html', dados)   

    return redirect("/simular/casas/")

def ler_dados(request):
    hora = request.GET.get("hora")
    dia = request.GET.get("dia")

    print("Dia {} Hora {}".format(dia, hora))

    return JsonResponse({"lista": 5}, status=200)
