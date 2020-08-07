from django.shortcuts import render, redirect
from core.models import *

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
    return render(request, 'gerador_testes/configurar.html', dados)

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
        essencial = request.POST.get('essencial')

        if essencial:
            essencial = True
        else:
            essencial = False

        if nome:
            TipoEquipamento.objects.create(
                nome = nome,
                essencial = essencial
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
    
    return render(request, 'gerador_testes/equipamento.html', dados)

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
