from django.shortcuts import render, redirect
from core.models import *

def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas', 
        'casas':casas
        }
    return render(request, 'casas/listar.html', dados)

def Cadastrar(request):
    casas = Casa.objects.all().order_by('nome')
    
    id = request.GET.get('id')
    casa = None
    if id:
        casa = Casa.objects.get(id=id)
    dados = {
        'titulo':'Cadastrar nova casa',
        'casas':casas,
        'casa': casa
    }

    return render(request, 'casas/cadastrar.html', dados)

def AdicionarCasa(request):
    if request.POST:
        nome = request.POST.get('nome')
        
        if nome:
            id = request.POST.get('id')
            if id:
                Casa.objects.filter(id = id).update(nome = nome)
            else:
                Casa.objects.create(nome = nome)
        
    return redirect('/cadastrar/')

def DeleteCasa(request,id):
    if id:
        item = Casa.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/cadastrar/')

def VisualizarCasa(request):
    id = request.GET.get('id')
    casa = None
    if id:
        casa = Casa.objects.get(id=id)

    dados  = {
        'titulo':'Visualizar casa',
        'casa': casa,
    }

    return render(request, 'casas/visualizar.html', dados)

def VoltarEtapa(request):
    return redirect('/visualizar/casa/?id='+request.GET.get('id'))

def NovoComodo(request):
    id = request.GET.get('id')
    comodo_id = request.GET.get('comodo_id')

    casa = None
    comodo = None

    if id:
        casa = Casa.objects.get(id=id)
    if comodo_id:
        comodo = Comodo.objects.get(id=comodo_id)
    
    
    comodos = Comodo.objects.filter(casa=casa).order_by('nome')
    dados  = {
        'titulo':'Cadastro de comodo',
        'casa': casa,
        'comodos': comodos,
        'comodo': comodo
    }

    return render(request, 'casas/comodo.html',dados)

def AdicionarComodo(request):
    if request.POST:
        casa_id = request.POST.get('casa_id')
        casa = Casa.objects.filter(id=casa_id).first()

        comodo_id = request.POST.get('comodo_id')
        nome = request.POST.get('nome')
    
        if nome:
            if comodo_id:
                Comodo.objects.filter(id = comodo_id).update(nome = nome)
            else:
                Comodo.objects.create(
                    nome = nome,
                    casa = casa
                )

    return redirect('/cadastrar/novo/comodo/?id='+casa_id)

def DeleteComodo(request,id, casa_id):
    if id:
        item = Comodo.objects.get(id=id)
        if item:
            item.delete()
    return redirect('/cadastrar/novo/comodo/?id={}'.format(casa_id))

def ListarComodoSaida(request):
    id = request.GET.get('id')

    if id:
        casa = Casa.objects.get(id=id)
    
    comodos = Comodo.objects.filter(casa=casa).order_by('nome')
    dados = {
        'titulo': 'Vincular comodo com terminais',
        'casa' : casa,
        'comodos': comodos
    }

    return render(request, 'casas/comodoSaida.html', dados)

def VincularSaida(request):
    comodo_id = request.GET.get('comodo_id')
    if comodo_id:
        comodo = Comodo.objects.get(id=comodo_id)
        terminais = ComodoSaida.objects.filter(comodo=comodo)
    
    lista = Saida.objects.all()#lista sao os terminais cadastrados
    dados = {
        'titulo': 'Vincular comodo com terminais',
        'comodo': comodo,
        'lista': lista,
        'terminais': terminais
    }
    return render(request, 'casas/vincularSaida.html', dados)

def AdicionarSaidaComodo(request):
    if request.POST:
        comodo_id = request.POST.get('comodo_id')
        saida_id = request.POST.get('terminal')
        qtde = request.POST.get('qtde')
        
        if comodo_id and saida_id and qtde:
            comodo = Comodo.objects.get(id = comodo_id)
            saida = Saida.objects.get(id = saida_id)

            comodoSaida = ComodoSaida.objects.filter(
                comodo=comodo,
                saida=saida
                )

            maior = 0
            if comodoSaida is not None:
                for item in comodoSaida:
                    if item.apelido > maior:
                        maior = item.apelido
            
            for i in range(int(qtde)):
                apelido = (i+1) + maior
                ComodoSaida.objects.create(
                    apelido = apelido,
                    comodo = comodo,
                    saida = saida
                )

    return redirect('/cadastrar/vincular/comodo/saida/?comodo_id={}'.format(comodo_id))

def DeleteSaidaComodo(request,id):
    comodo_id = None
    if id:
        item = ComodoSaida.objects.get(id=id)

        if item:
            comodo_id = item.comodo.id
            saida_id = item.saida.id
            apelido = item.apelido

            item.delete()

            #Fecha a lacuna caso exista
            comodo = Comodo.objects.get(id = comodo_id)
            saida = Saida.objects.get(id = saida_id)
            comodoSaida = ComodoSaida.objects.filter(
                comodo=comodo,
                saida=saida
                )

            maior = 0
            if comodoSaida is not None:
                for item in comodoSaida:
                    if item.apelido > maior:
                        maior = item.apelido
            
            if maior > apelido:
                ComodoSaida.objects.filter(
                    comodo=comodo,
                    saida=saida,
                    apelido=maior
                    ).update(apelido=apelido)


    return redirect('/cadastrar/vincular/comodo/saida/?comodo_id={}'.format(comodo_id))

def ListarComodoEquipamento(request):
    id = request.GET.get('id')

    if id:
        casa = Casa.objects.get(id=id)
    
    comodos = Comodo.objects.filter(casa=casa).order_by('nome')

    consumo = {'agua_min': 0, 'agua_max': 0, 'energia_min': 0, 'energia_max': 0 }
    for item in comodos:
        aux = CalcularConsumo(item)
        consumo['agua_min'] = consumo['agua_min'] + aux['agua_min']
        consumo['agua_max'] = consumo['agua_max'] + aux['agua_max']
        consumo['energia_min'] = consumo['energia_min'] + aux['energia_min']
        consumo['energia_max'] = consumo['energia_max'] + aux['energia_max']

    dados = {
        'titulo': 'Vincular comodo com terminais',
        'casa' : casa,
        'comodos': comodos,
        'consumo': consumo
    }

    return render(request, 'casas/comodoEquipamento.html', dados)

def VincularEquipamento(request):
    comodo_id = request.GET.get('id')
    if comodo_id:
        comodo = Comodo.objects.get(id=comodo_id)
        equipamentos = Equipamento.objects.all()
        terminais = ComodoSaida.objects.filter(comodo=comodo)

        #1 esta sendo id da agua e 2 da energia
        consumo = CalcularConsumo(comodo)
        
        vinculados = []
        for item in terminais:
            if item.saida is not None and item.equipamento is not None:
                if item.equipamento not in vinculados:
                    vinculados.append(item.equipamento)
 
    dados = {
        'titulo': 'Vincular terminal com equipamento',
        'comodo': comodo,
        'equipamentos': equipamentos,
        'vinculados': vinculados,
        'terminais': terminais,
        'consumo': consumo
    }

    return render(request, 'casas/vincularEquipamento.html', dados)

def ComodoEquipamento(request):
    comodo_id = request.GET.get('comodo_id')
    equipamento_id = request.GET.get('equipamento_id')
    saidas = Saida.objects.all()

    terminais = []
    if comodo_id and equipamento_id:
        comodo = Comodo.objects.get(id=comodo_id)
        equipamento = Equipamento.objects.get(id=equipamento_id)
        ambos = TipoConsumo.objects.get(nome="Água e energia")

        for saida in saidas:
            cs = ComodoSaida.objects.filter(
                comodo=comodo,
                saida=saida
            )
            
            vinculados = ComodoSaida.objects.filter(
                comodo=comodo,
                equipamento=equipamento
            )
            
            flag = True
            for vinc in vinculados:
                if vinc.saida.tipo_consumo == saida.tipo_consumo:
                    flag = False

            if flag:
                for item in cs:
                    if item.equipamento is None:
                        if saida.tipo_consumo == equipamento.tipo_consumo: 
                            aux = {'id': item.id, 'apelido': item.apelido, 'nome': saida.nome}
                            terminais.append(aux)
                        elif equipamento.tipo_consumo == ambos:
                            aux = {'id': item.id, 'apelido': item.apelido, 'nome': saida.nome, 'tipo_consumo': saida.tipo_consumo}
                            terminais.append(aux)
    
    tempo = None
    if vinculados:
        tempo = {
            'tempo_min_semana': vinculados[0].tempo_min_semana,
            'tempo_max_semana': vinculados[0].tempo_max_semana,
            'tempo_min_feriado': vinculados[0].tempo_min_feriado,
            'tempo_max_feriado': vinculados[0].tempo_max_feriado
        }

    dados = {
        'titulo': 'Vincular terminal com equipamento',
        'comodo': comodo,
        'equipamento': equipamento,
        'terminais': terminais,
        'vinculados': vinculados,
        'tempo': tempo
    }

    return render(request, 'casas/terminalEquipamento.html', dados)

def AdicionarSaidaEquipamento(request):
    if request.POST:
        terminal_id = request.POST.get('terminal_id')
        comodo_id = request.POST.get('comodo_id')
        equipamento_id = request.POST.get('equipamento_id')

        if comodo_id and terminal_id and equipamento_id:
            equipamento = Equipamento.objects.get(id=equipamento_id)

            semana_min = request.POST.get('semana_min')
            semana_max = request.POST.get('semana_max')
            feriado_min = request.POST.get('feriado_min')
            feriado_max = request.POST.get('feriado_max')

            essencial = request.POST.get('essencial')
            if essencial is None:
                essencial = False

            if equipamento:
                ComodoSaida.objects.filter(id=terminal_id).update(
                    equipamento=equipamento,
                    tempo_min_semana=semana_min,
                    tempo_max_semana=semana_max,
                    tempo_min_feriado=feriado_min,
                    tempo_max_feriado=feriado_max,
                    essencial=essencial
                    )

    return redirect('/cadastrar/vincular/equipamento/comodo/selecionar/?comodo_id={}&equipamento_id={}'.format(comodo_id,equipamento_id))

def DesvincularSaidaEquipamento(request,id):
    item = ComodoSaida.objects.get(id = id)
    comodo_id = item.comodo.id
    equipamento_id = item.equipamento.id

    ComodoSaida.objects.filter(id = id).update(
        equipamento=None,
        essencial=False
    )

    return redirect('/cadastrar/vincular/equipamento/comodo/selecionar/?comodo_id={}&equipamento_id={}'.format(comodo_id,equipamento_id))

def CalcularConsumo(comodo):
    terminais = ComodoSaida.objects.filter(comodo=comodo)

    consumo = {'agua_min': 0, 'agua_max': 0, 'energia_min': 0, 'energia_max': 0 }
    for item in terminais:
        if item.saida is not None and item.equipamento is not None:
            if item.saida.tipo_consumo.id == 1:
                # agua_hora/60 * tempo_min_semana * 5 dias semana + final de semana
                consumo['agua_min'] = consumo['agua_min'] + ((item.equipamento.consumo_agua/60)  * item.tempo_min_semana * 5)
                consumo['agua_min'] = consumo['agua_min'] + ((item.equipamento.consumo_agua/60)  * item.tempo_min_feriado * 2)

                consumo['agua_max'] = consumo['agua_max'] + ((item.equipamento.consumo_agua/60)  * item.tempo_max_semana * 5)
                consumo['agua_max'] = consumo['agua_max'] + ((item.equipamento.consumo_agua/60)  * item.tempo_max_feriado * 2)
            else:
                consumo['energia_min'] = consumo['energia_min'] + ((item.equipamento.consumo_energia/60)  * item.tempo_min_semana * 5)
                consumo['energia_min'] = consumo['energia_min'] + ((item.equipamento.consumo_energia/60)  * item.tempo_min_feriado * 2)

                consumo['energia_max'] = consumo['energia_max'] + ((item.equipamento.consumo_energia/60)  * item.tempo_max_semana * 5)
                consumo['energia_max'] = consumo['energia_max'] + ((item.equipamento.consumo_energia/60)  * item.tempo_max_feriado * 2)

    if consumo is not None:
        consumo['agua_min'] = consumo['agua_min'] * 4
        consumo['agua_max'] = consumo['agua_max'] * 4
        consumo['energia_min'] = (consumo['energia_min'] * 4) / 1000
        consumo['energia_max'] = (consumo['energia_max'] * 4) / 1000
    
    return consumo