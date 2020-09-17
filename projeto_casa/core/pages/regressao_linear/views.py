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

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'coeficientes': None,
        'categorias': None,
        'mes': mes,
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
        energia_semana = energia_semana / 5
        agua_semana = agua_semana /5
        energia_final = energia_final / 2
        agua_final = agua_final / 2

        #faz as conversoes para saber o que cada comodo usa por hora
        comodos = gerarPesos()
        for item in comodos:
            item['media_energia_semana'] = round(item['percent_energia'] * energia_semana / 100,2)
            item['media_energia_final'] = round(item['percent_energia'] * energia_final / 100,2)

            item['media_agua_semana'] = round(item['percent_agua'] * agua_semana / 100,2)
            item['media_agua_final'] = round(item['percent_agua'] * agua_final / 100,2)

        #Aqui embaixo vou colocar vetor de categorias
        PreencherCategorias(comodos)        
        
        
        
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
        
def PreencherCategorias(consumos):
    global casa
    global mes
    if casa and mes:
        comodos = Comodo.objects.filter(casa=casa)
        #Elimina dados para n ficar dados que nao vao ser usados
        for item in comodos:
            ComodoCategoria.objects.filter(comodo=item).delete()

        month = getPosMes(mes.mes) + 1
        dia = date(mes.ano,month,1)
        
        while dia.month == month:
            semana = dia.weekday()
            data = DiaMes.objects.get(data=dia)
            
            pos = 0
            for comodo in comodos:
                if semana < 5:
                    ComodoCategoria.objects.create(
                        comodo=comodo,
                        meta_energia= consumos[pos]['media_energia_semana'],
                        meta_agua= consumos[pos]['media_agua_semana'],
                        dia_mes=data
                    )
                else:
                    ComodoCategoria.objects.create(
                        comodo=comodo,
                        meta_energia= consumos[pos]['media_energia_final'],
                        meta_agua= consumos[pos]['media_agua_final'],
                        dia_mes=data
                    )   
                pos = pos + 1     

            dia = dia + timedelta(days=1)
                
#------------------------------------------------------------------------------------------------
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
