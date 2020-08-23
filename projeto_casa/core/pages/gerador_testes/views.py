from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta  

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }

    return render(request, 'gerador_testes/listar.html', dados)

def Gerar(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
    
    dados = {
        'titulo':'Gerar teste', 
        'casa':casa
    }

    return render(request, 'gerador_testes/gerar.html',dados)

def GerarTestes(request):
    id = request.GET.get('id')
    if id:
        inicio = date.today()
        today = date.today()#vai finalizar quando chegar no mesmo dia

        for dia in range(366):
            if inicio.year == today.year:
                for hora in range(24):
                    print("{} {}:00".format(inicio, hora))
            elif inicio.month < today.month:
                for hora in range(24):
                    print("{} {}:00".format(inicio, hora))
            elif inicio.day <= today.day:
                for hora in range(24):
                    print("{} {}:00".format(inicio, hora))
            inicio = inicio + timedelta(days=1)
        
    return redirect('/gerar-testes/gerar/?id={}'.format(id))