from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import random 
import math
import time

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

def GerarMes(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        ConsumoMes.objects.filter(casa=casa).delete()
        ini = time.time()
        GerarTestes(casa, 0)          
        fim = time.time()
        print("Tempo {}".format(fim-ini))
    return redirect('/gerar-testes/gerar/?id={}'.format(id))

def GerarAno(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        ConsumoMes.objects.filter(casa=casa).delete()

        for i in range(12):
            #ini = time.time()
            GerarTestes(casa, i)
            #fim = time.time()
            mes = getMes(i)
        
    return redirect('/gerar-testes/gerar/?id={}'.format(id))

def GerarTestes(casa, inicial):
    inicio = fim = date.today()
    inicio = inicio.replace(day=1)
    fim = fim.replace(day=1)
    
    #se nao for mes atual
    if inicial != 0:
        aux = inicio.month + inicial
        if aux > 12:
            aux = aux - 12
            
            year = inicio.year + 1
            inicio = inicio.replace(year=year)
            fim = fim.replace(year=year)

        inicio = inicio.replace(month=aux)
        fim = fim.replace(month=aux)
    
    mes = getMes(inicio.month-1)
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

    energia = energia_semana = energia_feriado = 0
    agua = agua_semana = agua_feriado = 0
    semanas = feriados = 0
    med_temp = med_vento = med_umi = 0
    while inicio.month == fim.month:
        semana = inicio.weekday()
        if semana < 5:
            semanas = semanas + 1
        else:
            feriados = feriados + 1

        temperatura = getTemperatura(inicio)
        umidade = getUmidade(inicio)
        vento = getVento(inicio)

        med_temp =  med_temp + temperatura
        med_vento = med_vento + vento
        med_umi =  med_umi + umidade

        dia_mes = DiaMes.objects.create(
            mes=consumoMes,
            data=inicio,
            temperatura=temperatura,
            umidade=umidade,
            vento=vento 
        )

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
                                    dia_mes = dia_mes,
                                    comodo_saida = terminal,
                                    tempo = tempo,
                                    hora = hora
                                )

                            hora = hora + 1
                    elif terminal.comodo_equipamento in registradas:
                        while terminal.comodo_equipamento in registradas:
                            pos = registradas.index(terminal.comodo_equipamento)  
                            item = dados[pos]

                            ConsumoHora.objects.create(
                                dia_mes = dia_mes,
                                comodo_saida = terminal,
                                tempo = item['tempo'],
                                hora = item['hora']
                            )

                            registradas.pop(pos)
                            dados.pop(pos)
        inicio = inicio + timedelta(days=1)
    semanas = semanas / 5
    feriados = feriados / 2

    energia_semana = energia_semana / semanas
    agua_semana = agua_semana / semanas
    energia_feriado = energia_feriado / feriados
    agua_feriado = agua_feriado / feriados

    inicio = inicio - timedelta(days=1)
    med_temp = med_temp / inicio.day
    med_vento = med_vento / inicio.day
    med_umi = med_umi / inicio.day

    ConsumoMes.objects.filter(casa = casa,mes = mes,
                    ano = fim.year).update(agua=agua, 
                    energia=energia,
                    energia_semana=energia_semana,
                    agua_semana=agua_semana,
                    energia_feriado=energia_feriado,
                    agua_feriado=agua_feriado,
                    temperatura = med_temp,
                    umidade = med_umi,
                    vento = med_vento
                    )

#Metodos
def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]

def calcularConsumo(consumoHora, tempo):
    return (consumoHora / 60) * tempo 

def getTemperatura(data):
    return 25
def getUmidade(data):
    return 36
def getVento(data):
    return 10 