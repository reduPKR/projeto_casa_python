from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import random 
import math
import time
import requests
import json

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }

    return render(request, 'gerador_testes/listar.html', dados)

def Gerar(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        meses = ConsumoMes.objects.filter(casa=casa)

        for mes in meses:
            mes.energia = round((mes.energia/1000), 1)

    dados = {
        'titulo':'Gerar teste', 
        'casa':casa,
        'meses': meses
    }

    return render(request, 'gerador_testes/gerar.html',dados)

def GerarManual(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        comodos = Comodo.objects.filter(casa=casa)
        for comodo in comodos:
            lista = []
            vinculados = []
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            for terminal in terminais:
                if terminal.comodo_equipamento is not None:
                    if terminal.comodo_equipamento not in vinculados:
                        lista.append(terminal)
            comodo.terminais = lista
        casa.comodos = comodos

    dados = {
        'titulo':'Cadastro manual', 
        'casa':casa
        }

    return render(request, 'gerador_testes/manual/gerar.html',dados)

def GerarManualSelecionar(request):
    casa_id = request.GET.get('casa_id')
    comodo_id = request.GET.get('comodo_id')
    terminal_id = request.GET.get('terminal_id')
    
    if casa_id:
        casa = Casa.objects.get(id=casa_id)
        comodo = Comodo.objects.get(id=comodo_id)
        terminal = ComodoSaida.objects.get(id=terminal_id)

        casa.comodo = comodo
        casa.terminal = terminal

    dados = {
        'titulo':'Cadastro manual', 
        'casa':casa,
        'dados': []
        }

    return render(request, 'gerador_testes/manual/selecionado.html',dados)

def GerarManualCadastrar(request):
    casa_id = request.POST.get('casa_id')
    lista = request.POST.get('lista')
    print(lista)

    return redirect('/gerar-testes/gerar/manual/?id={}'.format(casa_id))

def GerarAutomatico(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        #ConsumoMes.objects.filter(casa=casa).delete()
        for i in range(12):
            GerarTestesAutomatico(casa, date(2019,i+1,1))
                  
        excluirCoeficientes(casa)
    return redirect('/gerar-testes/gerar/?id={}'.format(id))

def GerarTestesAutomatico(casa, inicio):
    final = inicio    

    mes = getMes(inicio.month-1)
    consumoMes = ConsumoMes.objects.filter(casa = casa,mes = mes,ano = 2019).first()

    if consumoMes is None:
        ConsumoMes.objects.create(
            casa=casa,
            mes=mes,
            ano = inicio.year
        )
        consumoMes = ConsumoMes.objects.get(casa = casa,mes = mes,ano = inicio.year)
    
    #gambiarra reduz acesso ao banco de ddos
    casa.comodos = Comodo.objects.filter(casa=casa)
    for comodo in casa.comodos:
        comodo.comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)

    for comodo in casa.comodos:
        for comodo_saida in comodo.comodoSaidas:
            ConsumoHora.objects.filter(mes = consumoMes,comodo_saida=comodo_saida).delete()

    energia = energia_semana = energia_feriado = 0
    agua = agua_semana = agua_feriado = 0
    while inicio.month == final.month:
        semana = inicio.weekday()

        for comodo in casa.comodos:
            registradas = [] #Caso um equipamento esteja em duas listas
            dados = [] # Evita gambiarra de comparacao
            for terminal in comodo.comodoSaidas:
                if terminal.comodo_equipamento and terminal.comodo_equipamento.equipamento:
                    if terminal.comodo_equipamento not in registradas:
                        # 0 segunda e 6 domingo
                        if semana < 5:
                            min =  math.ceil(terminal.tempo_min_semana / 5)
                            max =  math.ceil(terminal.tempo_max_semana / 5)
                        else:
                            min =  math.ceil(terminal.tempo_min_feriado / 2)
                            max =  math.ceil(terminal.tempo_max_feriado / 2)

                        qtde = math.ceil(((min+max)/2) / 60)
                        if qtde == 0:
                            qtde = 1
                        min = math.ceil(min / qtde)
                        max = math.ceil(max / qtde)

                        probabilidade = ((qtde * 100) / 24)
                        hora = 0
                        while hora < 24 and qtde > 0:
                            x = random.randint(0, 100)
                            if terminal.comodo_equipamento.equipamento.tipo_equipamento.id == 4: #Valor direto (Iluminação)
                                #luz acessa ate 0 horas depois as 6 da manha
                                if hora > 0 and hora < 6:
                                    probabilidade = 5
                                elif hora > 6 and hora < 19:
                                    probabilidade = 2
                                else:
                                    probabilidade = 93
                            else:
                                #Restante
                                if hora > 0 and hora < 6:
                                    probabilidade = probabilidade / 2
                                else:
                                    probabilidade = probabilidade * 2
                           
                            if x <= probabilidade:
                                tempo = abs(random.randint(min, max))

                                qtde = qtde - 1
                                consumoAgua = consumoEnergia = 0
                                if terminal.comodo_equipamento.equipamento.tipo_consumo.id == 1:
                                    consumoAgua = calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, tempo)
                                elif terminal.comodo_equipamento.equipamento.tipo_consumo.id == 2:
                                    consumoEnergia = calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, tempo)
                                else:
                                    consumoAgua = calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, tempo)
                                    consumoEnergia = calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, tempo)
                                
                                energia = energia + consumoEnergia
                                agua = agua + consumoAgua
                                if semana < 5:
                                    energia_semana = energia_semana + consumoEnergia
                                    agua_semana = agua_semana + consumoAgua
                                else:
                                    energia_feriado = energia_feriado + consumoEnergia
                                    agua_feriado = agua_feriado + consumoAgua
                                
                                if terminal.comodo_equipamento.equipamento.tipo_consumo.id == 3: #Valor direto 
                                    registradas.append(terminal.comodo_equipamento)
                                    dados.append({'tempo': tempo, 'hora': hora})

                                ConsumoHora.objects.create(
                                    mes = consumoMes,
                                    data = inicio,
                                    hora = hora,
                                    tempo = tempo,
                                    comodo_saida = terminal
                                )

                            hora = hora + 1
                    elif terminal.comodo_equipamento in registradas:
                        pos = registradas.index(terminal.comodo_equipamento)  
                        item = dados[pos]

                        

                        registradas.pop(pos)
                        dados.pop(pos)
        inicio = inicio + timedelta(days=1)
    
        ConsumoMes.objects.filter(casa = casa,mes = mes,
                    ano = 2019).update(
                    agua=agua, 
                    energia=energia,
                    energia_semana=energia_semana,
                    agua_semana=agua_semana,
                    energia_feriado=energia_feriado,
                    agua_feriado=agua_feriado,
                    )

#Metodos
def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]

def calcularConsumo(consumoHora, tempo):
    return (consumoHora / 60) * tempo 

def excluirCoeficientes(casa):
    grupos = GrupoCoeficiente.objects.filter(casa = casa)     
    for grupo in grupos:
        Coeficiente.objects.filter(grupo=grupo).delete()
    GrupoCoeficiente.objects.filter(casa = casa).delete()
    comodos = Comodo.objects.filter(casa=casa)
    for comodo in comodos:
        ComodoValorY.objects.filter(comodo=comodo).delete()
