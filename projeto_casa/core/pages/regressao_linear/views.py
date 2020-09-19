from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import time
import math

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
        mes.energia_semana = round(mes.energia_semana /1000) #converto para Kwh
        mes.energia_feriado = round(mes.energia_feriado /1000)     

        reduzir = {
            'agua_semana': mes.reduzir_agua_semana,
            'agua_feriado': mes.reduzir_agua_feriado,
            'energia_semana': mes.reduzir_energia_semana,
            'energia_feriado': mes.reduzir_energia_feriado
        }   

        data = date.today()
        data = data.replace(day=1)
        data = data.replace(year=2019)
        comodo = Comodo.objects.filter(casa=casa).first();
        comodoY = ComodoValorY.objects.filter(comodo=comodo,data=data).first()
        if comodoY == None:
            executar = True
        else:
            executar = False

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'coeficientes': None,
        'mes': mes,
        'reduzir':reduzir,
        'executar': executar
    }

    return render(request, 'simulacao/regressao_linear/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def GerarCategorias(request):
    global casa
    global mes
    
    if casa and mes:
        energia_semana = float(request.GET.get('energia_semana'))
        energia_final =float(request.GET.get('energia_final'))
        agua_semana = float(request.GET.get('agua_semana'))
        agua_final = float(request.GET.get('agua_final'))

        if energia_semana  > 0 and energia_final  > 0 and agua_semana  > 0 and agua_final > 0:
            ConsumoMes.objects.filter(id=mes.id).update(
                reduzir_agua_semana = agua_semana,
                reduzir_agua_feriado = agua_final,
                reduzir_energia_semana = energia_semana,
                reduzir_energia_feriado = energia_final,
            )

            gerarPadrao(energia_semana, energia_final, agua_semana, agua_final)

        return redirect('/regressao-linear-multipla/coeficiente?casa_id={}&mes_id={}'.format(casa.id,mes.id))
    return redirect('/simular/casas/')
       
#Gerar os Gerar coeficientes
def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]

def getPosMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses.index(mes)

def calcularConsumo(consumoHora, tempo):
    return (consumoHora / 60) * tempo 
               
def gerarPesos():
    #Retorna o percentual de cada comodo consome
    global casa

    consumos = []
    if casa:
        comodos = Comodo.objects.filter(casa=casa)
        agua_total = energia_total = 0
        for comodo in comodos:
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            agua = energia = 0
            for terminal in terminais:
                if terminal.saida and terminal.comodo_equipamento:
                    if terminal.saida.tipo_consumo.id == 1: #Valor Direto
                        agua = agua + terminal.comodo_equipamento.equipamento.consumo_agua
                    else:
                        energia = energia + terminal.comodo_equipamento.equipamento.consumo_energia
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

#Aqui vou pegar o padrao de consumo e gerar a saida Y reduzida, para que as previsoes gerem
#os valores de comparacao.
def gerarPadrao(energia_semana, energia_final, agua_semana, agua_final):
    global casa
    global mes
    
    if casa and mes:
        #elimina ficar buscando posteriormente
        comodos = Comodo.objects.filter(casa=casa)
        for comodo in comodos:
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            comodo.terminais = terminais
            for terminal in comodo.terminais:
                consumos = ConsumoHora.objects.filter(comodo_saida = terminal, mes = mes)
                terminal.consumos = consumos

        for comodo in comodos:
            ComodoValorY.objects.filter(comodo=comodo).delete()

        month = getPosMes(mes.mes) + 1
        data = date(2019,month, 1)
        while data.day <= 7:
            for hora in range(24):
                for comodo in comodos:
                    energia = agua = 0
                    for terminal in comodo.terminais:
                        for consumo in terminal.consumos:
                            if data == consumo.data and hora == consumo.hora:
                                agua = agua + calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, consumo.tempo)
                                energia = energia + calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, consumo.tempo)                              
                    
                    #Se nao tem nada vai atrapalhar
                    if agua > 0 or energia > 0:
                        ComodoValorY.objects.create(
                            comodo = comodo,
                            data = data,
                            hora = hora,
                            meta_agua = agua,
                            meta_energia = energia
                        )
            data = data + timedelta(days=1)


