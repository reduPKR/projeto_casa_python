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

        grupos = GrupoCoeficiente.objects.filter(casa=casa).first()
        if grupos:
            reduzir = {
                'agua_semana': math.ceil(grupos.reduzir_agua_semana),
                'agua_feriado': math.ceil(grupos.reduzir_agua_feriado),     
                'energia_semana': math.ceil(grupos.reduzir_energia_semana / 1000),
                'energia_feriado': math.ceil(grupos.reduzir_energia_feriado / 1000),
                'agua_semana_min': math.ceil(mes.agua_semana - (mes.agua_semana * 0.3)),
                'agua_feriado_min': math.ceil(mes.agua_feriado - (mes.agua_feriado * 0.3)),
                'energia_semana_min': math.ceil(mes.energia_semana - (mes.energia_semana * 0.3)),
                'energia_feriado_min': math.ceil(mes.energia_feriado - (mes.energia_feriado * 0.3))
            } 
        else:
            reduzir = {
                'agua_semana': math.ceil(mes.agua_semana),
                'agua_feriado': math.ceil(mes.agua_feriado),
                'energia_semana': math.ceil(mes.energia_semana),
                'energia_feriado': math.ceil(mes.energia_feriado),
                'agua_semana_min': math.ceil(mes.agua_semana - (mes.agua_semana * 0.3)),
                'agua_feriado_min': math.ceil(mes.agua_feriado - (mes.agua_feriado * 0.3)),
                'energia_semana_min': math.ceil(mes.energia_semana - (mes.energia_semana * 0.3)),
                'energia_feriado_min': math.ceil(mes.energia_feriado - (mes.energia_feriado * 0.3))
            } 

        data = date.today()
        data = data.replace(day=1)
        data = data.replace(year=2019)
        comodo = Comodo.objects.filter(casa=casa).first();
        #Se houver 1 mes cadastrado nao precisa mais
        comodoY = ComodoValorY.objects.filter(comodo=comodo).first()
        if comodoY == None:
            executar = True
        else:
            executar = False

    dados = {
        'titulo':'Regressão linear multipla', 
        'casa': casa,
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
        energia_semana = float(request.GET.get('energia_semana')) * 1000
        energia_final = float(request.GET.get('energia_final')) * 1000
        agua_semana = float(request.GET.get('agua_semana')) 
        agua_final = float(request.GET.get('agua_final')) 

        if energia_semana  > 0 and energia_final  > 0 and agua_semana  > 0 and agua_final > 0:
            grupo = GrupoCoeficiente.objects.filter(
                casa = casa,
                gerador = "Regresão linear",
                reduzir_agua_semana = agua_semana,
                reduzir_agua_feriado = agua_final,
                reduzir_energia_semana = energia_semana,
                reduzir_energia_feriado = energia_final
            )
            
            if grupo.count() == 0:
                ini = time.time()
                gerarPadrao(energia_semana, energia_final, agua_semana, agua_final)
                fim = time.time()
                print("Tempo estabelecer entrada x saida {}".format(fim-ini))

                ini = time.time()
                gerarConstantes(energia_semana, energia_final, agua_semana, agua_final)       
                fim = time.time()
                print("Tempo treino dos neuronios{}".format(fim-ini))

                ini = time.time()
                analisarPrecisao(energia_semana, energia_final, agua_semana, agua_final) 
                fim = time.time()
                print("Tempo analise {}".format(fim-ini))


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

#Aqui vou pegar o padrao de consumo e gerar a saida Y reduzida, para que as previsoes gerem
#os valores de comparacao.
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

def gerarConstantes(energia_semana, energia_final, agua_semana, agua_final):
    #teste()

    GrupoCoeficiente.objects.create(
        casa = casa,
        gerador = "Regresão linear",
        reduzir_agua_semana = agua_semana,
        reduzir_agua_feriado = agua_final,
        reduzir_energia_semana = energia_semana,
        reduzir_energia_feriado = energia_final
    )

    grupo = GrupoCoeficiente.objects.filter(
        casa = casa,
        gerador = "Regresão linear",
        reduzir_agua_semana = agua_semana,
        reduzir_agua_feriado = agua_final,
        reduzir_energia_semana = energia_semana,
        reduzir_energia_feriado = energia_final
    ).first()

    month = getPosMes(mes.mes) + 1
    clima = Clima.objects.filter(data__month=month)
    comodos = Comodo.objects.filter(casa=casa)
    
    #intervalo = ["2019-{}-01".format(month), "2019-{}-10".format(month)]
    for comodo in comodos:
        Y = ComodoValorY.objects.filter(comodo=comodo,data__month=month)
        vetYenergia = []
        vetYagua = []
        matClima = []

        #Cria as constantes da semana
        for itemY in Y:
            if itemY.data.weekday() < 5:
                for itemC in clima:
                    if itemY.data == itemC.data and itemY.hora == itemC.hora:
                        vetYenergia.append(itemY.meta_energia) 
                        vetYagua.append(itemY.meta_agua)
                        #Esse 1 gera a constante do calculo
                        matClima.append([
                            itemC.temperatura,
                            itemC.umidade,
                            itemC.vento,
                            itemC.pressao,
                            itemC.chuva
                        ])
        matTranspX = transposta(matClima)
        matXTranspX = multiplicar(matClima,matTranspX)
        matXTranspXInver = inversao(matXTranspX)
        matXTranspEnergia = multiplicarVetor(vetYenergia,matTranspX)
        matXTranspAgua = multiplicarVetor(vetYagua,matTranspX)

        #coeficiantes
        energiaB = multiplicarVetor(matXTranspEnergia,matXTranspXInver)
        aguaB = multiplicarVetor(matXTranspAgua,matXTranspXInver)

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = grupo,
            energia =True,
            semana = True,
            temperatura = energiaB[0],
            umidade = energiaB[1],
            vento = energiaB[2],
            pressao = energiaB[3],
            chuva = energiaB[4]
        )

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = grupo,
            energia = False,
            semana = True,
            temperatura = aguaB[0],
            umidade = aguaB[1],
            vento = aguaB[2],
            pressao = aguaB[3],
            chuva = aguaB[4]
        )

        #Cria as constantes do final de semana
        for itemY in Y:
            if itemY.data.weekday() >= 5:
                for itemC in clima:
                    if itemY.data == itemC.data and itemY.hora == itemC.hora:
                        vetYenergia.append(itemY.meta_energia) 
                        vetYagua.append(itemY.meta_agua)
                        #Esse 1 gera a constante do calculo
                        matClima.append([
                            itemC.temperatura,
                            itemC.umidade,
                            itemC.vento,
                            itemC.pressao,
                            itemC.chuva
                        ])
        matTranspX = transposta(matClima)
        matXTranspX = multiplicar(matClima,matTranspX)
        matXTranspXInver = inversao(matXTranspX)
        matXTranspEnergia = multiplicarVetor(vetYenergia,matTranspX)
        matXTranspAgua = multiplicarVetor(vetYagua,matTranspX)

        #coeficiantes
        energiaB = multiplicarVetor(matXTranspEnergia,matXTranspXInver)
        aguaB = multiplicarVetor(matXTranspAgua,matXTranspXInver)

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = grupo,
            energia =True,
            semana = False,
            temperatura = energiaB[0],
            umidade = energiaB[1],
            vento = energiaB[2],
            pressao = energiaB[3],
            chuva = energiaB[4]
        )

        Coeficiente.objects.create(
            comodo = comodo,
            grupo = grupo,
            energia = False,
            semana = False,
            temperatura = aguaB[0],
            umidade = aguaB[1],
            vento = aguaB[2],
            pressao = aguaB[3],
            chuva = aguaB[4]
        )
   
def teste():
    matx = [[1,5,118],[1,13,132],[1,20,119],[1,28,153],
            [1,41,91],[1,49,118],[1,61,132],[1,62,105]]
    vet = [8.1,6.8,7,7.4,7.7,7.5,7.6,8]
    matt = transposta(matx)
    matxt = multiplicar(matx,matt)
    matxti = inversao(matxt)
    matxty = multiplicarVetor(vet,matt)
    coef = multiplicarVetor(matxty,matxti)
    print(coef)
    
def transposta(matriz):
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
        if mat[coluna][coluna] != 0:
            pivo = mat[coluna][coluna]
        else:
            pivo = 1

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

def analisarPrecisao(energia_semana, energia_final, agua_semana, agua_final):
    grupo = GrupoCoeficiente.objects.filter(
        casa = casa,
        gerador = "Regresão linear",
        reduzir_agua_semana = agua_semana,
        reduzir_agua_feriado = agua_final,
        reduzir_energia_semana = energia_semana,
        reduzir_energia_feriado = energia_final
    ).first()

    month = getPosMes(mes.mes) + 1
    clima = Clima.objects.filter(data__month=month)
    
    comodos = Comodo.objects.filter(casa=casa)
    total = 0 
    acertos = 0
    for comodo in comodos:
        resultados = ComodoValorY.objects.filter(comodo=comodo,data__month=month)
        coeficientes = Coeficiente.objects.filter(
            comodo = comodo,
            grupo = grupo
        )  

        total_sem_agua = total_sem_ene = total_fin_agua = total_fin_ene = 0
        acerto_sem_agua = acerto_sem_ene = acerto_fin_agua = acerto_fin_ene = 0
        for resultado in resultados:                
            for item in clima:
                if resultado.data == item.data and resultado.hora == item.hora:
                    if resultado.data.weekday() < 5:
                        for coeficiente in coeficientes:
                            if coeficiente.semana and coeficiente.energia:
                                total_sem_ene = total_sem_ene + 1
                                energia = coeficiente.constante + (item.temperatura * coeficiente.temperatura) + (item.umidade * coeficiente.umidade) + (item.vento * coeficiente.vento) + (item.pressao * coeficiente.pressao) + (item.chuva * coeficiente.chuva)

                                if resultado.meta_energia == round(energia):
                                    acerto_sem_ene = acerto_sem_ene + 1
                            elif coeficiente.semana and coeficiente.energia is False:
                                total_sem_agua = total_sem_agua + 1
                                agua = coeficiente.constante + (item.temperatura * coeficiente.temperatura) + (item.umidade * coeficiente.umidade) + (item.vento * coeficiente.vento) + (item.pressao * coeficiente.pressao) + (item.chuva * coeficiente.chuva)
                                
                                if resultado.meta_agua == round(agua):
                                    acerto_sem_agua = acerto_sem_agua + 1
                    else:
                        for coeficiente in coeficientes:
                            if coeficiente.semana is False and coeficiente.energia:
                                total_fin_ene = total_fin_ene + 1
                                energia = coeficiente.constante + (item.temperatura * coeficiente.temperatura) + (item.umidade * coeficiente.umidade) + (item.vento * coeficiente.vento) + (item.pressao * coeficiente.pressao) + (item.chuva * coeficiente.chuva)
                            
                                if resultado.meta_energia == round(energia):
                                    acerto_fin_ene = acerto_fin_ene + 1
                            elif coeficiente.semana  is False and coeficiente.energia is False:
                                total_fin_agua = total_fin_agua + 1
                                agua = coeficiente.constante + (item.temperatura * coeficiente.temperatura) + (item.umidade * coeficiente.umidade) + (item.vento * coeficiente.vento) + (item.pressao * coeficiente.pressao) + (item.chuva * coeficiente.chuva)

                                if resultado.meta_agua == round(agua):
                                    acerto_fin_agua = acerto_fin_agua + 1

        perc = (acerto_sem_ene * 100) / total_sem_ene
        Coeficiente.objects.filter(
            comodo = comodo,
            grupo = grupo,
            energia = True,
            semana = True
        ).update(precisao = perc)

        perc = (acerto_sem_agua * 100) / total_sem_agua
        Coeficiente.objects.filter(
            comodo = comodo,
            grupo = grupo,
            energia = False,
            semana = True
        ).update(precisao = perc)

        perc = (acerto_fin_ene * 100) / total_fin_ene
        Coeficiente.objects.filter(
            comodo = comodo,
            grupo = grupo,
            energia = True,
            semana = False
        ).update(precisao = perc)

        perc = (acerto_fin_agua * 100) / total_fin_agua
        Coeficiente.objects.filter(
            comodo = comodo,
            grupo = grupo,
            energia = False,
            semana = False
        ).update(precisao = perc)

        acertos = acertos + acerto_sem_agua + acerto_sem_ene + acerto_fin_agua + acerto_fin_ene
        total = total + total_sem_agua + total_sem_ene + total_fin_agua + total_fin_ene           
    
    perc = (acertos * 100) / total
    GrupoCoeficiente.objects.filter(id=grupo.id).update(precisao = perc)

