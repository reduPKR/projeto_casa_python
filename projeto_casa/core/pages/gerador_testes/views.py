from django.shortcuts import render
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {'titulo':'Lista de casas', 'casas':casas}
    return render(request, 'gerador_testes/listar.html', dados)

def Configurar(request):
    dados = {'titulo':'Configurações'}
    return render(request, 'gerador_testes/configurar.html', dados)

def Equipamentos(request):
    dados = {'titulo':'Cadastro de equipamentos'}
    return render(request, 'gerador_testes/equipamento.html', dados)

def Cadastrar(request):
    dados = {'titulo':'Cadastrar nova casa'}
    return render(request, 'gerador_testes/cadastrar.html', dados)