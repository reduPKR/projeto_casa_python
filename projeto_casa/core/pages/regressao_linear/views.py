from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import time

casa = None
mes = None
def ListaCoeficientes(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        global casa
        global mes

        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)
        mes.energia = round(mes.energia/1000,2)
        mes.energia_semana = round(mes.energia_semana/1000) #converto para Kwh
        mes.energia_feriado = round(mes.energia_feriado/1000)

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'mes': mes,
        'coeficientes': None,
        "agua_semana": round(mes.agua_semana/2,2),
        "agua_feriado": round(mes.agua_feriado/2,2),
        "energia_semana": round(mes.energia_semana/2), # energia kWh /2
        "energia_feriado": round(mes.energia_feriado/2)
    }

    return render(request, 'simulacao/regressao_linear/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def GerarCoeficientes(request):
    global casa
    global mes

    if casa and mes:
        energia_semana = float(request.GET.get('energia_semana')) * 1000 #faz a conversao w para kW
        energia_final =float(request.GET.get('energia_final')) * 1000
        agua_semana = float(request.GET.get('agua_semana'))
        agua_final = float(request.GET.get('agua_final'))

        #converte para hora porem de todos comodos
        energia_semana = energia_semana / 120
        agua_semana = agua_semana /120
        energia_final = energia_final / 48
        agua_final = agua_final / 48

        #faz as conversoes para saber o que cada comodo usa por hora
        consumos = gerarPesos(energia_semana, agua_semana, energia_final, agua_final)
        for item in consumos:
            item['media_energia_semana'] = round(item['percent_energia'] * energia_semana / 100,2)
            item['media_energia_final'] = round(item['percent_energia'] * energia_final / 100,2)

            item['media_agua_semana'] = round(item['percent_agua'] * agua_semana / 100,2)
            item['media_agua_final'] = round(item['percent_agua'] * agua_final / 100,2)
        
        #Aqui embaixo vou colocar vetor de categorias
        categorias = PreencherCategorias()
        
    return redirect('/regressao-linear-multipla/coeficiente?casa_id=3&mes_id=319')
       
#Gerar os Gerar coeficientes
def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]

def getPosMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses.index(mes)

def calcularConsumo(consumoHora, tempo):
    percent = tempo * 10 / 6 #100 / 60
    return (consumoHora * percent)/100

def gerarPesos(energia_semana, agua_semana, energia_final, agua_final):
    global casa

    consumos = []
    if casa:
        comodos = Comodo.objects.filter(casa=casa)
        agua_total = energia_total = 0
        for comodo in comodos:
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            agua = energia = 0
            for terminal in terminais:
                if terminal.saida is not None and terminal.equipamento is not None:
                    if terminal.saida.tipo_consumo.id == 1: #Valor Direto
                        agua = agua + terminal.equipamento.consumo_agua
                    else:
                        energia = energia + terminal.equipamento.consumo_energia
            energia_total = energia_total + energia
            agua_total = agua_total + agua
            consumos.append({'id': comodo.id, 'nome': comodo.nome,'agua': agua, 'energia': energia})
        
        for item in consumos:
            if item['agua'] == 0:
                item['percent_agua'] = 0
            else:
                item['percent_agua'] = round((item['agua']*100)/agua_total,2)
            
            if item['energia'] == 0:
                item['percent_energia'] = 0
            else:
                item['percent_energia'] = round((item['energia']*100)/energia_total,2)

    return consumos
        
def PreencherCategorias():
    global casa
    global mes
    if casa and mes:
        comodos = Comodo.objects.filter(casa=casa)

        month = getPosMes(mes.mes) + 1
        dia = date(mes.ano,month,1)

        #Estou tentando evitar ficar fazendo requisicoes ao banco
        for comodo in comodos:
            comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)
            comodo.comodoSaidas = comodoSaidas

            for terminal in comodo.comodoSaidas:
                if terminal.equipamento:
                    horas = ConsumoHora.objects.filter(comodo_saida=terminal,mes= mes)
                    terminal.horas = horas

        ini = time.time()
        while dia.day != 11:
            for hora in range(24):
                for comodo in comodos:
                    #comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)
                    energia = 0
                    agua = 0
                    for terminal in comodo.comodoSaidas:
                        if terminal.equipamento:
                            # horas = ConsumoHora.objects.filter(comodo_saida=terminal,mes= mes)
                            for item in terminal.horas:
                                if item.data == dia and item.hora == hora:
                                    print(" {} {} {} {}".format(item.data,dia, item.hora, hora))

            dia = dia + timedelta(days=1)
        fim = time.time()
        print("\n")
        print("Tempo {}".format(fim-ini))
        print("\n")

                

