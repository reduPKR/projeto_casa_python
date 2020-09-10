from django.shortcuts import render, redirect
from core.models import *

def MenuConfigurar(request):
    dados = {
        'titulo':'Menu de configurações'
    }
    return render(request, 'configuracoes/menu.html', dados)

def Configurar(request):
    categorias = Categoria.objects.all()
    consumos = TipoConsumo.objects.all() 
    tipoEquipamentos = TipoEquipamento.objects.all()
    dados = {
            'titulo':'Configurações', 
            'categorias': categorias,
            'consumos': consumos,
            'tipoEquipamentos': tipoEquipamentos
        }
    return render(request, 'configuracoes/configurar.html', dados)

def SaveCategorias(request):
    if request.POST:
        nome = request.POST.get('nome')
        if nome:
            Categoria.objects.create(nome = nome)
    
    return redirect('/configurar/')

def SaveRecursos(request):
    if request.POST:
        nome = request.POST.get('nome')
        if nome:
            TipoConsumo.objects.create(nome = nome)
    
    return redirect('/configurar/')

def SaveCategoriaEquipamento(request):
    if request.POST:
        nome = request.POST.get('nome')

        if nome:
            TipoEquipamento.objects.create(
                nome = nome
                )
    
    return redirect('/configurar/')

def DeleteCategorias(request,id):
    if id:
        item = Categoria.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/configurar/')

def DeleteRecursos(request,id):
    if id:
        item = TipoConsumo.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/configurar/')

def DeleteCategoriaEquipamento(request,id):
    if id:
        item = TipoEquipamento.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/configurar/')

def Equipamentos(request):
    equipamentos = Equipamento.objects.all().order_by('nome')
    consumos = TipoConsumo.objects.all() 
    tipoEquipamentos = TipoEquipamento.objects.all()

    id = request.GET.get('id')
    equipamento = None
    if id:
        equipamento = Equipamento.objects.get(id=id)
    dados = {
        'titulo':'Cadastro de equipamentos',
        'equipamentos': equipamentos,
        'equipamento': equipamento,
        'consumos': consumos,
        'tipoEquipamentos': tipoEquipamentos
    }
    
    return render(request, 'configuracoes/equipamento.html', dados)

def SaveEquipamentos(request):
    if request.POST:
        nome = request.POST.get('nome')
        consumo_energia = request.POST.get('energia')
        consumo_agua = request.POST.get('agua')
        descricao = request.POST.get('descricao')
        
        consumo_id = request.POST.get('consumo')
        tipo_consumo = TipoConsumo.objects.filter(id=consumo_id).first()
        equipamento_id = request.POST.get('tipoEquipamento')
        tipo_equipamento = TipoEquipamento.objects.filter(id=equipamento_id).first()
        
        if nome:
            id = request.POST.get('id')
            if id:
                Equipamento.objects.filter(id=id).update(
                    nome = nome,
                    consumo_energia = consumo_energia,
                    consumo_agua = consumo_agua,
                    descricao = descricao,
                    tipo_consumo = tipo_consumo,
                    tipo_equipamento = tipo_equipamento
                )
            else:
                Equipamento.objects.create(
                    nome = nome,
                    consumo_energia = consumo_energia,
                    consumo_agua = consumo_agua,
                    descricao = descricao,
                    tipo_consumo = tipo_consumo,
                    tipo_equipamento = tipo_equipamento
                )
    
    return redirect('/equipamentos/')

def DeleteEquipamentos(request,id):
    if id:
        item = Equipamento.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/equipamentos/')

def Saidas(request):
    consumos = TipoConsumo.objects.all()
    terminais = Saida.objects.all()

    lista = []
    for item in consumos:
        if item.id != 3:   #Valor direto
            lista.append(item)

    id = request.GET.get('id')
    terminal = None
    if id:
        terminal = Saida.objects.get(id=id)

    dados = {
        'titulo':'Cadastro de terminais', 
        'consumos':lista,
        'terminais':terminais,
        'terminal': terminal
    }

    return render(request, 'configuracoes/saida.html',dados)

def AdicionarSaida(request):
    if request.POST:
        nome = request.POST.get('nome')
        
        consumo_id = request.POST.get('consumo')
        tipo_consumo = TipoConsumo.objects.filter(id=consumo_id).first()

        if nome:
            id = request.POST.get('id')
            if id:
                Saida.objects.filter(id=id).update(
                    nome=nome,
                    tipo_consumo = tipo_consumo
                    )
            else:
                Saida.objects.create(
                    nome=nome, 
                    tipo_consumo = tipo_consumo
                    )
        return redirect('/configurar/saida/')

def DeleteSaida(request,id):
    if id:
        item = Saida.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/configurar/saida/')