from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }
    return render(request, 'casas/listar.html', dados)

etapa = 0
ctr = False
def Cadastrar(request):
    casas = Casa.objects.all().order_by('nome')
    
    id = request.GET.get('id')
    casa = None
    if id:
        casa = Casa.objects.get(id=id)
    dados = {
        'titulo':'Cadastrar nova casa',
        'casas':casas,
        'casa': casa
    }

    return render(request, 'casas/cadastrar.html', dados)

def AdicionarCasa(request):
    nome = request.POST.get('nome')
    
    if nome:
        id = request.POST.get('id')
        if id:
            Casa.objects.filter(id = id).update(nome = nome)
        else:
            Casa.objects.create(nome = nome)
        
    return redirect('/cadastrar/')

def DeleteCasa(request,id):
    if id:
        item = Casa.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/cadastrar/')


def VoltarEtapa(request):
    global etapa
    global ctr

    etapa = 0
    ctr = True

    return redirect('/cadastrar/')

def NovoComodo(request):
    global etapa
    global ctr

    etapa = 1
    ctr = True

    return redirect('/cadastrar/')

def NovaSaida(request):
    global etapa
    global ctr

    etapa = 2
    ctr = True

    return redirect('/cadastrar/')

def NovoVinculo(request):
    global etapa
    global ctr

    etapa = 3
    ctr = True

    return redirect('/cadastrar/')
