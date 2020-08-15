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
    if request.POST:
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

def VisualizarCasa(request):
    id = request.GET.get('id')
    casa = None
    if id:
        casa = Casa.objects.get(id=id)

    dados  = {
        'titulo':'Visualizar casa',
        'casa': casa,
    }

    return render(request, 'casas/visualizar.html', dados)

def VoltarEtapa(request):
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))

def NovoComodo(request):
    id = request.GET.get('id')
    comodo_id = request.GET.get('comodo_id')

    casa = None
    comodo = None

    if id:
        casa = Casa.objects.get(id=id)
    if comodo_id:
        comodo = Comodo.objects.get(id=comodo_id)
    
    
    comodos = Comodo.objects.filter(casa=casa).order_by('nome')
    dados  = {
        'titulo':'Cadastro de comodo',
        'casa': casa,
        'comodos': comodos,
        'comodo': comodo
    }

    return render(request, 'casas/comodo.html',dados)

def AdicionarComodo(request):
    if request.POST:
        casa_id = request.POST.get('casa_id')
        casa = Casa.objects.filter(id=casa_id).first()

        comodo_id = request.POST.get('comodo_id')
        nome = request.POST.get('nome')
    
        if nome:
            if comodo_id:
                Comodo.objects.filter(id = comodo_id).update(nome = nome)
            else:
                Comodo.objects.create(
                    nome = nome,
                    casa = casa
                )

    return redirect('/cadastrar/novo/comodo/?id='+casa_id)

def DeleteComodo(request,id, casa_id):
    if id:
        item = Comodo.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/cadastrar/novo/comodo/?id={}'.format(casa_id))

def ListarComodoSaida(request):
    id = request.GET.get('id')

    if id:
        casa = Casa.objects.get(id=id)
    
    comodos = Comodo.objects.filter(casa=casa).order_by('nome')
    dados = {
        'titulo': 'Vincular comodo com terminais',
        'casa' : casa,
        'comodos': comodos
    }

    return render(request, 'casas/comodoSaida.html', dados)

def VincularSaida(request):
    comodo_id = request.GET.get('comodo_id')
    if comodo_id:
        comodo = Comodo.objects.get(id=comodo_id)
        terminais = ComodoSaida.objects.filter(comodo=comodo)
    
    lista = Saida.objects.all()#lista sao os terminais cadastrados
    dados = {
        'titulo': 'Vincular comodo com terminais',
        'comodo': comodo,
        'lista': lista,
        'terminais': terminais
    }
    return render(request, 'casas/vincularSaida.html', dados)

def AdicionarSaidaComodo(request):
    comodo_id = request.POST.get('comodo_id')
    saida_id = request.POST.get('terminal')
    qtde = request.POST.get('qtde')
    
    if comodo_id and saida_id and qtde:
        comodo = Comodo.objects.get(id = comodo_id)
        saida = Saida.objects.get(id = saida_id)

        comodoSaida = ComodoSaida.objects.filter(
            comodo=comodo,
            saida=saida
            )

        maior = 0
        if comodoSaida is not None:
            for item in comodoSaida:
                if item.apelido > maior:
                    maior = item.apelido
        
        for i in range(int(qtde)):
            apelido = (i+1) + maior
            ComodoSaida.objects.create(
                apelido = apelido,
                comodo = comodo,
                saida = saida
            )

    return redirect('/cadastrar/vincular/comodo/saida/?comodo_id={}'.format(comodo_id))

def DeleteSaidaComodo(request,id):
    comodo_id = None
    if id:
        item = ComodoSaida.objects.get(id=id)

        if item:
            comodo_id = item.comodo.id
            saida_id = item.saida.id
            apelido = item.apelido

            item.delete()

            #Fecha a lacuna caso exista
            comodo = Comodo.objects.get(id = comodo_id)
            saida = Saida.objects.get(id = saida_id)
            comodoSaida = ComodoSaida.objects.filter(
                comodo=comodo,
                saida=saida
                )

            maior = 0
            if comodoSaida is not None:
                for item in comodoSaida:
                    if item.apelido > maior:
                        maior = item.apelido
            
            if maior > apelido:
                ComodoSaida.objects.filter(
                    comodo=comodo,
                    saida=saida,
                    apelido=maior
                    ).update(apelido=apelido)


    return redirect('/cadastrar/vincular/comodo/saida/?comodo_id={}'.format(comodo_id))

def VincularEquipamento(request):
    global etapa
    global this
    etapa = 4
    this = True
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))
