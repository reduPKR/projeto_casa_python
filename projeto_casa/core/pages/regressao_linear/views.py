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
        mes.energia_semana = round(mes.energia_semana/1000) #converto para Kwh
        mes.energia_feriado = round(mes.energia_feriado/1000)

        comodos = Comodo.objects.filter(casa=casa)
        meta_agua_semana = meta_agua_feriado = meta_energia_semana = meta_energia_feriado = 0       
        if comodos is not None:
            for item in comodos:
                meta_agua_semana = item.meta_agua_semana + meta_agua_semana
                meta_agua_feriado = item.meta_agua_feriado + meta_agua_feriado
                meta_energia_semana = item.meta_energia_semana + meta_energia_semana
                meta_energia_feriado = item.meta_energia_feriado + meta_energia_feriado
        else:
            meta_agua_semana = mes.agua_semana
            meta_agua_feriado = mes.agua_feriado
            meta_energia_semana = round(mes.energia_semana/1000)
            meta_energia_feriado = round(mes.energia_feriado/1000)
        
        
        reduzir = {
            'agua_semana': round(meta_agua_semana * 120,1),  
            'agua_feriado': round(meta_agua_feriado * 48,1), 
            'energia_semana': round(meta_energia_semana * 12 / 100,1), #120/1000
            'energia_feriado': round(meta_energia_feriado * 48 / 1000,1)
        }

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'coeficientes': None,
        'mes': mes,
        'reduzir':reduzir,
        "agua_semana": math.ceil(mes.agua_semana/2),
        "agua_feriado": math.ceil(mes.agua_feriado/2),
        "energia_semana": math.ceil(mes.energia_semana/2), # energia kWh /2
        "energia_feriado": math.ceil(mes.energia_feriado/2)
    }

    return render(request, 'simulacao/regressao_linear/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def GerarCategorias(request):
    global casa
    global mes
    
    if casa and mes:
        energia_semana = float(request.GET.get('energia_semana')) * 1000 #faz a conversao kW para w
        energia_final =float(request.GET.get('energia_final')) * 1000
        agua_semana = float(request.GET.get('agua_semana'))
        agua_final = float(request.GET.get('agua_final'))

        #converte para hora porem de todos comodos
        energia_semana = energia_semana / 120
        agua_semana = agua_semana / 120
        energia_final = energia_final / 48
        agua_final = agua_final / 48

        #faz as conversoes para saber o que cada comodo usa por hora
        comodos = gerarPesos()
        for item in comodos:
            item['media_energia_semana'] = round(item['percent_energia'] * energia_semana / 100,2)
            item['media_energia_final'] = round(item['percent_energia'] * energia_final / 100,2)

            item['media_agua_semana'] = round(item['percent_agua'] * agua_semana / 100,2)
            item['media_agua_final'] = round(item['percent_agua'] * agua_final / 100,2)

        for comodo in comodos:
            Comodo.objects.filter(id=comodo['id']).update(
                meta_agua_semana = comodo['media_agua_semana'], 
                meta_agua_feriado = comodo['media_agua_final'],         
                meta_energia_semana = comodo['media_energia_semana'],              
                meta_energia_feriado = comodo['media_energia_final']
            )
        
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
