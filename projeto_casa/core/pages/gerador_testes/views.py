from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }

    return render(request, 'gerador_testes/listar.html', dados)