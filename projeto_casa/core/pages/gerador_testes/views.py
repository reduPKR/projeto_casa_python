from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all()
    dados = {'titulo':'Lista de casas', 'casas':casas}
    return render(request, 'gerador_testes/listar.html', dados)

def Configurar(request):
    categorias = Categoria.objects.all()
    consumos = TipoConsumo.objects.all() 
    equipamentos = TipoEquipamento.objects.all()
    dados = {
            'titulo':'Configurações', 
            'categorias': categorias,
            'consumos': consumos,
            'equipamentos': equipamentos
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
    dados = {'titulo':'Cadastro de equipamentos'}
    return render(request, 'gerador_testes/equipamento.html', dados)

def Cadastrar(request):
    dados = {'titulo':'Cadastrar nova casa'}
    return render(request, 'gerador_testes/cadastrar.html', dados)