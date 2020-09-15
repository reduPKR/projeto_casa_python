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
        categorias = ComodoCategoria.objects.filter(mes=mes).first()

    dados = {
        'titulo':'Selecionar coeficiente', 
        'casa': casa,
        'coeficientes': None,
        'categorias': categorias,
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
        energia_semana = energia_semana / 120
        agua_semana = agua_semana /120
        energia_final = energia_final / 48
        agua_final = agua_final / 48

        #Aqui embaixo vou colocar vetor de categorias
        PreencherCategorias(energia_semana, agua_semana, energia_final, agua_final)        
        
        #faz as conversoes para saber o que cada comodo usa por hora
        consumos = gerarPesos(energia_semana, agua_semana, energia_final, agua_final)
        for item in consumos:
            item['media_energia_semana'] = round(item['percent_energia'] * energia_semana / 100,2)
            item['media_energia_final'] = round(item['percent_energia'] * energia_final / 100,2)

            item['media_agua_semana'] = round(item['percent_agua'] * agua_semana / 100,2)
            item['media_agua_final'] = round(item['percent_agua'] * agua_final / 100,2)
        
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
        
def PreencherCategorias(energia_semana, agua_semana, energia_final, agua_final):
    global casa
    global mes
    if casa and mes:
        comodos = Comodo.objects.filter(casa=casa)
        
        #Elimina dados para n ficar dados que nao vao ser usados
        for comodo in comodos:
            ComodoCategoria.objects.filter(comodo=comodo).delete()

        month = getPosMes(mes.mes) + 1
        dia = date(mes.ano,month,1)

        #Estou tentando evitar ficar fazendo requisicoes ao banco
        for comodo in comodos:
            comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)
            comodo.comodoSaidas = comodoSaidas

            for terminal in comodo.comodoSaidas:
                if terminal.comodo_equipamento:
                    horas = ConsumoHora.objects.filter(comodo_saida=terminal,mes= mes)
                    terminal.horas = horas
        
        while dia.month == month:
            semana = dia.weekday()
            for hora in range(24):
                for comodo in comodos:
                    #comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)
                    energia = 0
                    agua = 0
                    for terminal in comodo.comodoSaidas:
                        if terminal.comodo_equipamento and terminal.comodo_equipamento.equipamento:
                            # horas = ConsumoHora.objects.filter(comodo_saida=terminal,mes= mes)
                            for item in terminal.horas:
                                if item.data == dia and item.hora == hora:
                                    if terminal.saida.tipo_consumo.id == 1: #Id diretamente
                                        agua = agua + calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, item.tempo)
                                    elif terminal.saida.tipo_consumo.id == 2: 
                                        energia = energia + calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, item.tempo)
                    
                    if energia > 0 or agua > 0:
                        if semana < 5:
                            categoria = Indice(energia,agua, energia_semana, agua_semana)
                        else:
                            categoria = Indice(energia,agua, energia_final, agua_final)
                        ComodoCategoria.objects.create(
                            comodo=comodo,
                            categoria=categoria,
                            data=dia,
                            hora=hora
                        )        

            dia = dia + timedelta(days=1)

def Indice(energia, agua, meta_energia, meta_agua):
    catEnergia = catAgua = 0
    if energia > 0:
        percEnergia = (meta_energia * 100) / energia
    else:
        percEnergia = 0

    if agua > 0:
        percAgua = (meta_agua * 100) / agua
    else:
        percAgua = 0

    if percEnergia < 35:
        catEnergia = 1
    elif percEnergia < 70:
        catEnergia = 2
    elif percEnergia < 105:
        catEnergia = 3
    elif percEnergia < 140:
        catEnergia = 4
    else:
        catEnergia = 5

    if percAgua < 35:
        catAgua = 1
    elif percAgua < 70:
        catAgua = 2
    elif percAgua < 105:
        catEnergia = 3
    elif percAgua < 140:
        catAgua = 4
    else:
        catAgua = 5
    
    id = round((catEnergia + catAgua)/2)
    
    return Categoria.objects.get(id=id)
                
#------------------------------------------------------------------------------------------------
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
