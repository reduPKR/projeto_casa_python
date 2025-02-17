from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta
import math
import random

casa = None
tempo = None
comodos = None
grupo = None
meta = None
historico = []
dia = 1
hora = 0

def voltar(request):
    global historico
    global dia
    global hora

    historico.clear()
    dia = 1
    hora = 0
    return redirect("/simular/selecionar/meta?casa_id={}".format(casa.id))

def iniciarDados(request):
    casa_id = request.GET.get('casa_id')
    grupo_id = request.GET.get('grupo_id')
    meta_id = request.GET.get('meta_id')
    minutos = request.GET.get('tempo')

    if casa_id and minutos and grupo_id and meta_id:
        global casa
        global tempo
        global grupo
        global comodos
        global meta
        global historico

        casa = Casa.objects.filter(id=casa_id).first()
        grupo = GrupoCoeficiente.objects.filter(id=grupo_id).first()
        comodos = preencherComodos(casa, grupo)
        meta = MetaTreino.objects.filter(id=meta_id).first()
        tempo = minutos

        # historico.append(gerarConsumo())

def reload(request):
    global casa
    global tempo
    global meta

    if casa is None or tempo is None or grupo is None or meta is None:
        return True

    return casa.id == request.GET.get('casa_id') and meta.id == request.GET.get('meta_id') and tempo == request.GET.get('tempo')

def Executar(request):
    global historico

    # if len(historico) == 0 or reload(request):
    iniciarDados(request)

    consumos = {
        'titulos': tituloComodos(comodos),
        'subtitulo': subTitulos(comodos),
        'gastos': historico
    }

    dados = {
        'titulo': 'Simular com teporizador',
        'casa': casa,
        'tempo': tempo,
        'consumos': consumos
    }

    return render(request, 'simulacao/execucao/temporizador.html', dados)

def preencherComodos(casa, grupo):
    comodos = Comodo.objects.filter(casa=casa)
    getComodos(comodos, grupo)
    getTerminais(comodos)
    getCoeficientes(comodos, grupo)
    return comodos

def getComodos(comodos, grupo):
    for comodo in comodos:
        comodo.energia_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=True).first()
        comodo.agua_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=True).first()
        comodo.energia_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=True, semana=False).first()
        comodo.agua_fim_semana = Coeficiente.objects.filter(grupo=grupo,comodo=comodo,energia=False, semana=False).first()

def getTerminais(comodos):
    for comodo in comodos:
        comodo.comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)

def getSemana():
    data = convert_data()
    semana = data.weekday()

    return semana < 5

def getCoeficientes(comodos, grupo):
    for comodo in comodos:
        comodo.coeficientes = Coeficiente.objects.filter(
            comodo=comodo,
            grupo=grupo
        ).first()

def tituloComodos(comodos):
    lista = []
    for item in comodos:
        lista.append(item.nome)
    return lista

def subTitulos(comodos):
    lista = []
    lista.append("-")
    lista.append("-")
    for item in comodos:
        lista.append("Energia")
        lista.append("Agua")
    return lista

def convert_data():
    global dia
    #nao achei nada pronto, fiz da maneira raiz
    data = date(2019,1,1)

    aux = dia-1
    while aux > 0:
        data = data + timedelta(days=1)
        aux = aux - 1
    return data

def ler_dados(request):
    #Fiz essa gambiarra que retornar no Json tava dando erro
    global historico
    global comodos
    global tempo

    getHora()
    historico.insert(0,gerarConsumo())

    consumos = {
        'titulos': tituloComodos(comodos),
        'subtitulo': subTitulos(comodos),
        'gastos': historico
    }

    dados = {
        'titulo': 'Simular com teporizador',
        'casa': casa,
        'tempo': tempo,
        'consumos': consumos
    }

    return redirect("/simular/selecionar/executar/tempo?casa_id=1&meta_id=8&tempo=1&grupo_id=18")

def getHora():
    global hora
    global dia

    if len(historico) == 0:
        hora = 0
        dia = 1
    else:
        hora = hora + 1

        if hora == 24:
            hora = 0
            dia = dia + 1

def gerarConsumo():
    semana = getSemana()
    data = convert_data()

    consumos = []
    consumos.append({"gasto":data, "cor": "#FFFFFF"})
    consumos.append({ "gasto": "{}:00".format(hora), "cor": "#FFFFFF"})



    for comodo in comodos:
        registradas = []

        consumoAgua = consumoEnergia = 0
        for terminal in comodo.comodoSaidas:
            if terminal.comodo_equipamento and terminal.comodo_equipamento.equipamento:
                if terminal.status:
                    if terminal.comodo_equipamento not in registradas:
                        if semana < 5:
                            min = math.ceil(terminal.tempo_min_semana / 5)
                            max = math.ceil(terminal.tempo_max_semana / 5)
                        else:
                            min = math.ceil(terminal.tempo_min_feriado / 2)
                            max = math.ceil(terminal.tempo_max_feriado / 2)

                        qtde = math.ceil(((min + max) / 2) / 60)
                        if qtde == 0:
                            qtde = 1
                        min = math.ceil(min / qtde)
                        max = math.ceil(max / qtde)

                        x = random.randint(0, 100)
                        if terminal.comodo_equipamento.equipamento.tipo_equipamento.id == 4:  # Valor direto (Iluminação)
                            # luz acessa ate 0 horas depois as 6 da manha
                            if hora > 0 and hora < 6:
                                probabilidade = 5
                            elif hora > 6 and hora < 19:
                                probabilidade = 2
                            else:
                                probabilidade = 93
                        else:
                            probabilidade = ((qtde * 100) / 24)
                            if probabilidade < 100:
                                if hora > 0 and hora < 6:
                                    probabilidade = probabilidade / 2
                                else:
                                    probabilidade = probabilidade * 2

                        if x <= probabilidade:
                            tempo = abs(random.randint(min, max))

                            qtde = qtde - 1

                            if terminal.comodo_equipamento.equipamento.tipo_consumo.id == 1:
                                consumoAgua += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, tempo)
                            elif terminal.comodo_equipamento.equipamento.tipo_consumo.id == 2:
                                consumoEnergia += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, tempo)
                            else:
                                consumoAgua += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_agua, tempo)
                                consumoEnergia += calcularConsumo(terminal.comodo_equipamento.equipamento.consumo_energia, tempo)
                else:
                    terminal.status = True

        energia = index(consumoEnergia,semana,True)
        agua = index(consumoAgua, semana, False)

        #tenho que pegar o quanto consumiu, comparar com o previsto
        previsto = calcularPrevisao(comodo, data)

        if validarCategoria(energia) or validarCategoria(agua):
            for terminal in comodo.comodoSaidas:
                if terminal.comodo_equipamento and terminal.comodo_equipamento.equipamento:
                    if terminal.essencial == False:
                        terminal.status = False

        consumos.append({"gasto":energia, "cor": pegarCor(energia)})
        consumos.append({"gasto":agua, "cor": pegarCor(agua)})

    return consumos

def calcularConsumo(consumoHora, tempo):
    return (consumoHora / 60) * tempo

def index(consumo, semana, energia):
    global meta

    if energia:
        if semana:
            energia = (meta.reduzir_energia_semana/(24*5*4.3))
        else:
            energia = (meta.reduzir_energia_feriado/(24*2*4.3))

        return categorias((consumo*100)/energia)
    else:
        if semana:
            agua = (meta.reduzir_agua_semana / (24*5*4.3))
        else:
            agua = (meta.reduzir_agua_feriado / (24*2*4.3))
        return categorias((consumo * 100) / agua)

def categorias(valor):
    if valor == 0:
        return "N/A"
    if valor < 35:
        return "MB"
    elif valor < 70:
        return "B"
    elif valor < 105:
        return "M"
    elif valor < 140:
        return "A"
    else:
        return "MA"

def validarCategoria(dado):
    return dado == "A" or dado == "MA"

def pegarCor(consumo):
    if consumo == "N/A":
        return "#DDDDDD"
    if consumo == "MB":
        return "#00FF00"
    elif consumo == "B":
        return "#00DD00"
    elif consumo == "M":
        return "#FFA500"
    elif consumo == "A":
        return "#FF4500"
    else:
        return "#FF0000"

def calcularPrevisao(comodo, data):
    clima = Clima.objects.filter(
        data=data,
        hora=hora
    ).first()

    return comodo.coeficientes.temperatura * clima.temperatura + comodo.coeficientes.umidade * clima.umidade + comodo.coeficientes.vento * clima.vento + comodo.coeficientes.pressao * clima.pressao + comodo.coeficientes.chuva * clima.chuva