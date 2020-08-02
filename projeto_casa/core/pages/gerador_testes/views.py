from django.shortcuts import render
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {'titulo':'Lista de casas', 'casas':casas}
    return render(request, 'gerador_testes/listar.html', dados)

def Configurar(request):
    return render(request, 'gerador_testes/configurar.html')

def Cadastrar(request):
    return render(request, 'gerador_testes/cadastrar.html')