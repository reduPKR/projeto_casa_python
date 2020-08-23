from django.shortcuts import render, redirect
from core.models import *
from datetime import date, timedelta 
import random 
import math

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }

    return render(request, 'gerador_testes/listar.html', dados)

def Gerar(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        meses = ConsumoMes.objects.filter(casa=casa)
    
    dados = {
        'titulo':'Gerar teste', 
        'casa':casa,
        'meses': meses
    }

    return render(request, 'gerador_testes/gerar.html',dados)

def GerarTestes(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        # ConsumoMes.objects.filter(casa=casa).delete()
        # print("\n\n\n")
        # inicio = date.today()
        # for i in range(13):
        #     aux = inicio
        #     mes = getMes(inicio.month-1)

        #     ConsumoMes.objects.create(
        #         casa=casa,
        #         mes=mes,
        #         ano = aux.year
        #     )

        #     #Nao achei nada que adiciona mais 1 mes
        #     while aux.month == inicio.month:
        #         inicio = inicio + timedelta(days=10)

        inicio = date.today()
        today = date.today()
        for dia in range(366):
            flag = False #caso nao seja um ano bissexto
            inicio = inicio + timedelta(days=1)
            if inicio.year == today.year:
                flag = True
            elif inicio.month < today.month:
                flag = True
            elif inicio.day <= today.day:
                flag = True

            if flag:
                consumoMes = ConsumoMes.objects.filter(casa=casa)
                comodos = Comodo.objects.filter(casa=casa)

                #pega todos os comodos
                for comodo in comodos:
                    comodoSaidas = ComodoSaida.objects.filter(comodo=comodo)

                    #gera um valor aleatorio de tempo de uso
                    for terminal in comodoSaidas:
                        # 0 segunda e 6 domingo
                        semana = inicio.weekday()
                        if terminal.equipamento:
                            if semana < 5:
                                min =  math.ceil(terminal.tempo_min_semana / 5)
                                max =  math.ceil(terminal.tempo_max_semana / 5)
                            else:
                                min =  math.ceil(terminal.tempo_min_feriado / 2)
                                max =  math.ceil(terminal.tempo_max_feriado / 2)

                            qtde = math.ceil(((min+max)/2) / 60)
                            tempo = random.randint(min, max)
                            print('\n')
                            print(qtde)
                            print(tempo)
                # for hora in range(24):
                #     print("{}/{}/{} {}:00".format(inicio.day, mes, inicio.year, hora))
        
    return redirect('/gerar-testes/gerar/?id={}'.format(id))


#Metodos
def getMes(mes):
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    return meses[mes]
