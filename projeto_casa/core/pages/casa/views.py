from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }
    return render(request, 'casas/listar.html', dados)

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

#alternacia entre as telas
etapa = 0
#quem chamou
this = False

def VisualizarCasa(request):
    global etapa
    global this

    if this is False:
        etapa = 0
    else:
        this = False

    id = request.GET.get('id')
    casa = None
    if id:
        casa = Casa.objects.get(id=id)

    comodos = Comodo.objects.all().order_by('nome')

    dados  = {
        'titulo':'Visualizar casa',
        'etapa': etapa,
        'casa': casa,
        'comodos': comodos
    }

    return render(request, 'casas/visualizar.html', dados)

def VoltarEtapa(request):
    global etapa
    etapa = 0
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))

def NovoComodo(request):
    global etapa
    global this
    etapa = 1
    this = True
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))

def AdicionarComodo(request):
    casa_id = request.POST.get('casa_id')
    casa = Casa.objects.filter(id=casa_id).first()

    id = request.POST.get('id')
    nome = request.POST.get('comodo')

    if nome:
        if id:
            pass
        else:
            Comodo.objects.create(
                nome = nome,
                casa = casa
            )

    global this
    this = True
    return redirect('/visualizar/casa/?id='+casa_id)

def NovaSaida(request):
    global etapa
    global this
    etapa = 2
    this = True
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))

def NovoVinculo(request):
    global etapa
    global this
    etapa = 3
    this = True
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))

def VincularEquipamento(request):
    global etapa
    global this
    etapa = 4
    this = True
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))
