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
        energia_semana = float(request.GET.get('energia_semana')) / 100
        energia_final = float(request.GET.get('energia_final')) / 100
        agua_semana = float(request.GET.get('agua_semana')) / 100
        agua_final = float(request.GET.get('agua_final')) / 100

        if energia_semana  > 0 and energia_final  > 0 and agua_semana  > 0 and agua_final > 0:
            # ConsumoMes.objects.filter(id=mes.id).update(
            #     reduzir_agua_semana = agua_semana,
            #     reduzir_agua_feriado = agua_final,
            #     reduzir_energia_semana = energia_semana,
            #     reduzir_energia_feriado = energia_final,
            # )

            # gerarPadrao(energia_semana, energia_final, agua_semana, agua_final)
            gerarConstantes()

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
        #Elimina ficar buscando posteriormente
        comodos = Comodo.objects.filter(casa=casa)
        for comodo in comodos:
            terminais = ComodoSaida.objects.filter(comodo=comodo)
            comodo.terminais = terminais
            for terminal in comodo.terminais:
                consumos = ConsumoHora.objects.filter(comodo_saida = terminal, mes = mes)
                terminal.consumos = consumos

        for comodo in comodos:
            ComodoValorY.objects.filter(comodo=comodo).delete()

        #Vou cadastrar o mes todo
        #Pois quando for verificar a presicao vou ter que usar valores
        # Diferentes dos usados para treinar 
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
                            energia = energia - (energia * energia_semana)
                            agua = agua - (agua * agua_semana)
                        else:
                            energia = energia - (energia * energia_final)
                            agua = agua - (agua * agua_final)                            
                            
                        ComodoValorY.objects.create(
                            comodo = comodo,
                            data = data,
                            hora = hora,
                            meta_agua = agua,
                            meta_energia = energia
                        )
            data = data + timedelta(days=1)

def gerarConstantes():
    #teste()
    month = getPosMes(mes.mes) + 1
    clima = Clima.objects.filter(data__month=month)
    comodos = Comodo.objects.filter(casa=casa)
    
    listaVetor = []
    listaMatriz = []
    listaMatrizT = [] #Transposta da matriz

    intervalo = ["2019-{}-01".format(month), "2019-{}-10".format(month)]
    for comodo in comodos:
        Y = ComodoValorY.objects.filter(comodo=comodo,data__range=intervalo)
        matClima = []
        matClimaT = []
        matY = []
        for itemY in Y:
            for itemC in clima:
                if itemY.data == itemC.data and itemY.hora == itemC.hora:
                    matY.append([itemY.meta_agua,itemY.meta_energia])
                    matClima.append([
                        itemC.temperatura,
                        itemC.umidade,
                        itemC.vento,
                        itemC.pressao,
                        itemC.chuva
                    ])
        listaMatriz.append(matClima)
        listaMatrizT.append(transpor(matClima))
        listaVetor.append(matY)
    
    
def teste():
    matx = [[1,5,118],[1,13,132],[1,20,119],[1,28,153],
            [1,41,91],[1,49,118],[1,61,132],[1,62,105]]
    vet = [8.1,6.8,7,7.4,7.7,7.5,7.6,8]
    matt = transpor(matx)
    matxt = multiplicar(matx,matt)
    matxti = inversao(matxt)
    matxty = multiplicarVetor(vet,matt)
    coef = multiplicarVetor(matxty,matxti)
    print(coef)
    
def transpor(matriz):
    transposta = []

    for i in range(len(matriz[0])):
        transposta.append([0] * len(matriz))
        
    for i in range(len(matriz)):
        for j in range(len(matriz[i])):
            transposta[j][i] = matriz[i][j]
    
    return transposta

def multiplicar(mat1, mat2):
    resp = []
    #colunas
    for i in range(len(mat2)):
        resp.append([0] * len(mat2))

    for i in range(len(mat2)):
        for j in range(len(mat2)):
            for k in range(len(mat1)):
                resp[i][j] = resp[i][j] + mat1[k][i] * mat2[j][k]
    return resp

def inversao(mat):
    identidade = []
    for i in range(len(mat)):
        identidade.append([0] * len(mat))

    for linha in range(len(mat)):
        for coluna in range(len(mat)):
            if linha == coluna:
                identidade[linha][coluna] = 1
            else:
                identidade[linha][coluna] = 0

    for coluna in range(len(mat)):
        pivo = mat[coluna][coluna]
        for k in range(len(mat)):
            mat[coluna][k] = (mat[coluna][k])/(pivo)
            identidade[coluna][k] = (identidade[coluna][k])/(pivo)
    
        for linha in range(len(mat)):
            if linha != coluna:
                coef = mat[linha][coluna]
                for k in range(len(mat)):
                    mat[linha][k] = (mat[linha][k]) - (coef*mat[coluna][k]); 
                    identidade[linha][k] = (identidade[linha][k]) - (coef*identidade[coluna][k]);  
    #nome esta invertido, mas a mat é a idendidade e a identidade é a resposta		
    return identidade

def multiplicarVetor(vet, mat):
    resp = []

    for i in range(len(mat)):
        val = 0
        for j in range(len(mat[i])):
            val = val + mat[i][j] * vet[j]
        resp.append(val)
    return resp