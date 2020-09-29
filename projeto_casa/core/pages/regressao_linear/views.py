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
        
        metas = MetaTreino.objects.filter(
            casa = casa,
            mes = mes.mes
        )

        for item in metas:
            item.reduzir_energia_semana = round(item.reduzir_energia_semana /1000) #converto para Kwh
            item.reduzir_energia_feriado = round(item.reduzir_energia_feriado /1000)
            
            grupo = GrupoCoeficiente.objects.filter(meta_treino = item, gerador = "Regresão linear").first()
            
            if grupo is None:
                item.treino = True
            else:
                item.precisao = grupo.precisao
                item.treino = False

    dados = {
        'titulo':'Regressão linear multipla', 
        'casa': casa,
        'mes': mes,
        'metas': metas,
    }

    return render(request, 'simulacao/regressao_linear/menu.html',dados)

# Daqui para baixo é a geracao dos coeficientes
def Treinar(request):
    global casa
    global mes
    
    if casa and mes:
        meta_id = request.GET.get('meta_id')
        meta = MetaTreino.objects.get(id = meta_id)

        grupo = GrupoCoeficiente.objects.filter(
            meta_treino = meta,
            gerador = "Regresão linear"
        )
            
        if grupo.count() == 0:
            ini = time.time()
            gerarConstantes(meta)       
            fim = time.time()

            analisarPrecisao(meta, (fim-ini)) 

        return redirect('/regressao-linear-multipla/coeficiente?casa_id={}&mes_id={}'.format(casa.id,mes.id))
    return redirect('/simular/casas/')
       

def gerarConstantes(meta):
    #teste()

    GrupoCoeficiente.objects.create(
        meta_treino = meta,
        gerador = "Regresão linear",
    )

    grupo = GrupoCoeficiente.objects.filter(
        meta_treino = meta,
        gerador = "Regresão linear"
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

def analisarPrecisao(meta, tempo):
    grupo = GrupoCoeficiente.objects.filter(
        meta_treino = meta,
        gerador = "Regresão linear",
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
    GrupoCoeficiente.objects.filter(id=grupo.id).update(precisao = perc, tempo_treino= tempo)

def getPosMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses.index(mes)
