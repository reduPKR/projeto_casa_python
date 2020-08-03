from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {'titulo':'Lista de casas', 'casas':casas}
    return render(request, 'gerador_testes/listar.html', dados)

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

def Equipamentos(request):
    equipamentos = Equipamento.objects.all()
    consumos = TipoConsumo.objects.all() 
    tipoEquipamentos = TipoEquipamento.objects.all()

    dados = {
        'titulo':'Cadastro de equipamentos',
        'equipamentos': equipamentos,
        'consumos': consumos,
        'tipoEquipamentos': tipoEquipamentos
    }
    return render(request, 'gerador_testes/equipamento.html', dados)

def SaveEquipamentos(request):
    if request.POST:
        nome = request.POST.get('nome')
        consumo_energia = request.POST.get('energia')
        consumo_agua = request.POST.get('agua')
        tempo_uso_min = request.POST.get('tempo_min')
        tempo_uso_max = request.POST.get('tempo_max')
        descricao = request.POST.get('descricao')
        tipo_consumo = request.POST.get('consumo')
        tipo_equipamnto = request.POST.get('tipoEquipamento')

        if nome:
            Equipamento.objects.create(
                nome = nome,
                consumo_energia = consumo_energia,
                consumo_agua = consumo_agua,
                tempo_uso_min = tempo_uso_min,
                tempo_uso_max = tempo_uso_max,
                descricao = descricao,
                tipo_consumo = tipo_consumo,
                tipo_equipamnto = tipo_equipamnto
            )
    
    return redirect('/equipamentos/')

def Cadastrar(request):
    dados = {'titulo':'Cadastrar nova casa'}
    return render(request, 'gerador_testes/cadastrar.html', dados)