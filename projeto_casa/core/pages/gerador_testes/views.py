from django.shortcuts import render
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {'titulo':'Lista de casas', 'casas':casas}
    return render(request, 'gerador_testes/listar.html', dados)

def Cadastrar(request):
    return render(request, 'gerador_testes/cadastrar.html')