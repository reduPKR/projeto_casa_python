from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import random 
import math

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

        GerarTestes(casa, 0)
    return redirect('/gerar-testes/gerar/?id={}'.format(id))

def GerarAno(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        ConsumoMes.objects.filter(casa=casa).delete()

        for i in range(12):
            GerarTestes(casa, i)
        
    return redirect('/gerar-testes/gerar/?id={}'.format(id))

def GerarTestes(casa, inicial):
    inicio = fim = date.today()
    inicio = inicio.replace(day=1)
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
    
    comodos = Comodo.objects.filter(casa=casa)
    consumoMes = ConsumoMes.objects.get(casa = casa,mes = mes,ano = inicio.year)

    energia = 0
    agua = 0
    while inicio.month == fim.month:
        #pega todos os comodos
        for comodo in comodos:
            comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)
            #gera um valor aleatorio de tempo de uso
            for terminal in comodoSaidas:
                if terminal.equipamento:
                    # 0 segunda e 6 domingo
                    semana = inicio.weekday()
                    if semana < 5:
                        min =  math.ceil(terminal.tempo_min_semana / 5)
                        max =  math.ceil(terminal.tempo_max_semana / 5)
                    else:
                        min =  math.ceil(terminal.tempo_min_feriado / 2)
                        max =  math.ceil(terminal.tempo_max_feriado / 2)

                    qtde = math.ceil(((min+max)/2) / 60)
                    tempo = random.randint(min, max)
                    probabilidade = ((qtde * 100) / 24)

                    for hora in range(24):
                        x = random.randint(0, 100)

                        if terminal.equipamento.tipo_equipamento.nome == "Iluminação": #Valor direto
                            #luz acessa ate 0 horas depois as 6 da manha
                            if hora > 0 and hora < 6:
                                probabilidade = 5
                            elif hora > 6 and hora < 19:
                                probabilidade = 1
                            else:
                                probabilidade = 95

                        if x <= probabilidade:
                            if qtde == 1:
                                uso = abs(tempo) #evita caso dire 60 de algum valor menor
                                tempo = qtde = 0 
                            else:
                                uso = 60
                                tempo = tempo - 60
                                qtde = qtde - 1

                            energia = energia + calcularConsumo(terminal.equipamento.consumo_energia, uso)
                            agua = agua + calcularConsumo(terminal.equipamento.consumo_agua, uso)
                    
                            ConsumoHora.objects.create(
                                mes = consumoMes,
                                comodo_saida = terminal,
                                tempo = uso,
                                data = inicio,
                                hora = hora
                            )            
        inicio = inicio + timedelta(days=1)
    ConsumoMes.objects.filter(casa = casa,
                    mes = mes,
                    ano = inicio.year).update(agua=agua, energia=energia)

#Metodos
def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]

def calcularConsumo(consumoHora, tempo):
    percent = tempo * 10 / 6 #100 / 60
    return (consumoHora * percent)/100