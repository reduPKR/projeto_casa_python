from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import time
import math

casa = None
mes = None
def Exibir(request):
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

        mes.energia_semana_min = round(mes.energia_semana * .7)
        mes.energia_feriado_min = round(mes.energia_feriado * .7)
        mes.agua_semana_min = round(mes.agua_semana * .7)
        mes.agua_feriado_min = round(mes.agua_feriado * .7)

        metas = meta = MetaTreino.objects.filter(
            casa = casa
        )

        for item in metas:
            item.reduzir_energia_semana = round(item.reduzir_energia_semana /1000) #converto para Kwh
            item.reduzir_energia_feriado = round(item.reduzir_energia_feriado /1000)

    dados = {
        'titulo':'Gerador de ponto medio', 
        'casa': casa,
        'mes': mes,
        'metas': metas
    }

    return render(request, 'simulacao/categorias/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def GerarCategorias(request):
    global casa
    global mes
    
    if casa and mes:
        energia_semana = float(request.GET.get('energia_semana')) * 1000
        energia_final = float(request.GET.get('energia_final')) * 1000
        agua_semana = float(request.GET.get('agua_semana')) 
        agua_final = float(request.GET.get('agua_final')) 

        if energia_semana  > 0 and energia_final  > 0 and agua_semana  > 0 and agua_final > 0:
            meta = MetaTreino.objects.filter(
                casa = casa,
                mes = mes.mes,
                reduzir_agua_semana = agua_semana,
                reduzir_agua_feriado = agua_final,
                reduzir_energia_semana = energia_semana,
                reduzir_energia_feriado = energia_final
            )
            
            if meta.count() == 0:
                gerarPadrao(energia_semana, energia_final, agua_semana, agua_final)

                MetaTreino.objects.create(
                    casa = casa,
                    mes = mes.mes,
                    reduzir_agua_semana = agua_semana,
                    reduzir_agua_feriado = agua_final,
                    reduzir_energia_semana = energia_semana,
                    reduzir_energia_feriado = energia_final
                )

        return redirect('/simular/gerar/categoria?casa_id={}&mes_id={}'.format(casa.id,mes.id))
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

    dados = []
    if casa:
        comodos = Comodo.objects.filter(casa=casa)
        for comodo in comodos:
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            comodo.terminais = terminais
            for terminal in comodo.terminais:
                consumos = ConsumoHora.objects.filter(comodo_saida = terminal, mes = mes)
                terminal.consumos = consumos

        agua_total = energia_total = 0
        month = getPosMes(mes.mes) + 1
        for comodo in comodos:
            energia = agua = 0
            data = date(2019,month, 1)
            while data.month == month:
                for hora in range(24):
                    for terminal in comodo.terminais:
                        for consumo in terminal.consumos:
                            if data == consumo.data and hora == consumo.hora:
                                agua = agua + calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, consumo.tempo)
                                energia = energia + calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, consumo.tempo)
                data = data + timedelta(days=1)

            dados.append({'id': comodo.id, 'nome': comodo.nome,'agua': agua, 'energia': energia})
            energia_total = energia_total + energia
            agua_total = agua_total + agua

        for item in dados:
            if item['agua'] == 0:
                item['percent_agua'] = 0
            else:
                item['percent_agua'] = round((item['agua']*100)/agua_total,2)
            
            if item['energia'] == 0:
                item['percent_energia'] = 0
            else:
                item['percent_energia'] = round((item['energia']*100)/energia_total,2)
    return dados

def gerarPadrao(energia_semana, energia_final, agua_semana, agua_final):
    global casa
    global mes
    
    if casa and mes:
        #cada comodo consome diferente
        energia_semana = energia_semana/360 #seria 720 porem a tendencia é mmetade do dia ter consumo
        energia_final = energia_final/360
        agua_semana = agua_semana/360
        agua_final = agua_final/360

        pesos = gerarPesos()
        for item in pesos:
            item['media_energia_semana'] = round(item['percent_energia'] * energia_semana / 100,2)
            item['media_energia_final'] = round(item['percent_energia'] * energia_final / 100,2)
            item['media_agua_semana'] = round(item['percent_agua'] * energia_semana / 100,2)
            item['media_agua_final'] = round(item['percent_agua'] * energia_final / 100,2)

        #Elimina ficar buscando posteriormente
        comodos = Comodo.objects.filter(casa=casa)
        pos = 0
        for comodo in comodos:
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            comodo.terminais = terminais
            for terminal in comodo.terminais:
                consumos = ConsumoHora.objects.filter(comodo_saida = terminal, mes = mes)
                terminal.consumos = consumos

            #consumo segue a mesma orde dos comodos
            comodo.media_energia_semana = pesos[pos]['media_energia_semana']
            comodo.media_energia_final = pesos[pos]['media_energia_final']
            comodo.media_agua_semana = pesos[pos]['media_agua_semana']
            comodo.media_agua_final = pesos[pos]['media_agua_final']
            pos =pos+1

        for comodo in comodos:
            ComodoValorY.objects.filter(comodo=comodo).delete()

        #Vou cadastrar o mes todo
        #Pois quando for verificar a presicao vou ter que usar valores
        #Diferentes dos usados para treinar 
        month = getPosMes(mes.mes) + 1
        data = date(2019,month, 1)
        while data.month == month:
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
                        semana = data.weekday()

                        if semana < 5:
                            energia = index(energia*100/comodo.media_energia_semana)
                            if comodo.media_agua_semana > 0:
                                agua = index(agua*100/comodo.media_agua_semana)
                        else:
                            energia = index(energia*100/comodo.media_energia_final)
                            if comodo.media_agua_semana > 0:
                                agua = index(agua*100/comodo.media_agua_final)
                        
                        ComodoValorY.objects.create(
                            comodo = comodo,
                            data = data,
                            hora = hora,
                            meta_agua = agua,
                            meta_energia = energia
                        )
            data = data + timedelta(days=1)

def index(valor):
    if valor == 0:
        return 0
    if valor < 35:
        return 1
    elif valor < 70:
        return 2
    elif valor < 105:
        return 3
    elif valor < 140:
        return 4
    else:
        return 5