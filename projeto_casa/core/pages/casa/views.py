from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {'titulo':'Lista de casas', 'casas':casas}
    return render(request, 'casas/listar.html', dados)

etapa = 0
ctr = False
def Cadastrar(request):
    global etapa
    global ctr

    if ctr is False:
        etapa = 0
    else:
        ctr = False

    dados = {
        'titulo':'Cadastrar nova casa',
        'etapa': etapa
    }
    
    return render(request, 'casas/cadastrar.html', dados)

def AvancarEtapa(request):
    global etapa
    global ctr

    etapa = etapa + 1
    ctr = True

    return redirect('/cadastrar/')

def VoltarEtapa(request):
    global etapa
    global ctr

    etapa = etapa-1
    ctr = True

    return redirect('/cadastrar/')
