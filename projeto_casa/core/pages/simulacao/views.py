from django.shortcuts import render, redirect
from core.models import *
import math
from datetime import date

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }

    return render(request, 'simulacao/listarCasas.html', dados)

def ListarMeses(request):
    id = request.GET.get('id')
    if id:
        casa = Casa.objects.get(id=id)
        meses = ConsumoMes.objects.filter(casa=casa)

        for mes in meses:
            mes.energia = round((mes.energia/1000), 1)

    dados = {
        'titulo':'Meses cadastrados', 
        'casa':casa,
        'meses': meses
    }

    return render(request, 'simulacao/listarMeses.html',dados)

def Algoritmos(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)

    dados = {
        'titulo':'Seleção de algoritmo', 
        'casa': casa,
        'mes': mes
    }

    return render(request, 'simulacao/algoritmos.html',dados)

def ListaCoeficientes(request):
    casa_id = request.GET.get('casa_id')
    mes_id = request.GET.get('mes_id')

    if casa_id and mes_id:
        data = date.today()
        data = data.replace(day=1)
        data = data.replace(year=2019)

        casa = Casa.objects.get(id=casa_id)
        mes = ConsumoMes.objects.get(id=mes_id)
        mes.energia = round(mes.energia/1000,2)
        
        comodo = Comodo.objects.filter(casa=casa).first();
        comodoY = ComodoValorY.objects.filter(comodo=comodo,data=data).first()
        if comodoY == None:
            executar = True
        else:
            executar = False

        grupos = GrupoCoeficiente.objects.filter(casa=casa)
        for grupo in grupos:
            grupo.reduzir_energia_semana = round(grupo.reduzir_energia_semana/1000,2)
            grupo.reduzir_energia_feriado = round(grupo.reduzir_energia_feriado /1000,2)

    dados = {
        'titulo':'Realizar testes', 
        'casa': casa,
        'grupos': grupos,
        'mes': mes,
        'executar': executar
    }

    return render(request, 'simulacao/testar.html',dados)

def Executar(request):
    casa_id = request.GET.get('casa_id')
    meta_id = request.GET.get('meta_id')

    if casa_id:
        casa = Casa.objects.get(id=casa_id)
        estrutura = MontarEstrutura(casa)

        for horario in estrutura:
            print("Data {} {}".format(horario.data, horario.hora))
            print("{} {} {} {} {}".format(horario.clima.temperatura, horario.clima.umidade, horario.clima.vento, horario.clima.pressao, horario.clima.chuva))
            for comodo in horario.comodos:
                print(comodo.nome)
            print("*"*40)

    return redirect('/simular/selecionar/meta?casa_id=1')
    
def MontarEstrutura(casa):
    comodos = Comodo.objects.filter(casa=casa)
    
    listaHorarios = []
    for comodo in comodos: 
        terminais = ComodoSaida.objects.filter(comodo=comodo).exclude(comodo_equipamento__isnull=True)
        comodo.terminais = terminais

        for terminal in terminais:
            horarios = ConsumoHora.objects.filter(comodo_saida=terminal)
            terminal.horarios = horarios

            for hora in horarios:
                #Preferi fazer meu proprio filtro
                if verificarLista(listaHorarios, hora):
                    listaHorarios.append(hora)
    
    listaHorarios.sort(key=lambda item: (item.data, item.hora))
    listaClimas = []
    climas = Clima.objects.all()
    for horario in listaHorarios:
        for clima in climas:
            if clima.data == horario.data and clima.hora == horario.hora:
                horario.clima = clima 

                itens = []
                for comodo in comodos:
                    for terminal in comodo.terminais:
                        for hora in terminal.horarios:
                            if hora.data == horario.data and hora.hora == horario.hora:
                                itens.append(comodo)
                
                horario.comodos = itens

    return listaHorarios


    
def verificarLista(lista, hora):
    flag = True

    i = 0
    while i < len(lista) and flag:
        if lista[i].hora == hora.hora and lista[i].data == hora.data:
            flag = False
        i += 1
    return flag


