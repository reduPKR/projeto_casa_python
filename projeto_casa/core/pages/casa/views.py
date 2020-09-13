from django.shortcuts import render, redirect
from core.models import *
import time

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
        multiplo = [] #evita que um chuveiro que esta conectado a duas saidas se repita
        for item in terminais:
            if item.saida is not None and item.comodo_equipamento is not None:
                if item.comodo_equipamento and item.comodo_equipamento.equipamento:
                    if item.comodo_equipamento not in multiplo:
                        item.comodo_equipamento.equipamento.apelido = item.comodo_equipamento.apelido
                        vinculados.append(item.comodo_equipamento)

                    if item.comodo_equipamento.equipamento.tipo_consumo.id == 3: # diretamente
                        multiplo.append(item.comodo_equipamento)
    
    dados = {
        'titulo': 'Vincular terminal com equipamento',
        'comodo': comodo,
        'equipamentos': equipamentos,
        'vinculados': vinculados,
        'terminais': terminais,
        'consumo': consumo
    }

    return render(request, 'casas/vincularEquipamento.html', dados)

def ComodoEquipamentos(request):
    comodo_id = request.GET.get('comodo_id')
    equipamento_id = request.GET.get('equipamento_id')
    saidas = Saida.objects.all()

    terminais = []
    if comodo_id and equipamento_id:
        comodo = Comodo.objects.get(id=comodo_id)
        equipamento = Equipamento.objects.get(id=equipamento_id)
        ambos = TipoConsumo.objects.get(id=3)# diretamente

        equipamentos = ComodoEquipamento.objects.filter(comodo=comodo, equipamento=equipamento)
        if equipamento.tipo_consumo == ambos:
            terminais = {'agua': [], 'energia': []}      

        vinculados = []
        for item in equipamentos:
            items = ComodoSaida.objects.filter(
                comodo=comodo,
                comodo_equipamento = item
            )
            for aux in items:
                vinculados.append(aux)
        
        lista = []
        for saida in saidas:
            cs = ComodoSaida.objects.filter(
                comodo=comodo,
                saida=saida
            )
            
            flag = True
            for vinculado in vinculados:
                if vinculado.saida.tipo_consumo == saida.tipo_consumo:
                    if saida.tipo_consumo not in lista:
                        lista.append(saida.tipo_consumo)
                        flag = False

            if flag:
                for item in cs:
                    if item.comodo_equipamento is None:
                        if saida.tipo_consumo == equipamento.tipo_consumo: 
                            aux = {'id': item.id, 'apelido': item.apelido, 'nome': saida.nome}
                            terminais.append(aux)
                        elif equipamento.tipo_consumo == ambos:
                            aux = {'id': item.id, 'apelido': item.apelido, 'nome': saida.nome, 'tipo_consumo': saida.tipo_consumo}
                            if saida.tipo_consumo.id == 1: #id direto
                                terminais['agua'].append(aux)
                            else:
                                terminais['energia'].append(aux)
                            #terminais.append(aux)
    dados = {
        'titulo': 'Vincular terminal com equipamento',
        'comodo': comodo,
        'equipamento': equipamento,
        'terminais': terminais,
        'vinculados': vinculados
    }

    return render(request, 'casas/terminalEquipamento.html', dados)

def AdicionarSaidaEquipamento(request):
    if request.POST:
        comodo_id = request.POST.get('comodo_id')
        equipamento_id = request.POST.get('equipamento_id')

        if comodo_id and equipamento_id:
            semana_min = request.POST.get('semana_min')
            semana_max = request.POST.get('semana_max')
            feriado_min = request.POST.get('feriado_min')
            feriado_max = request.POST.get('feriado_max')

            essencial = request.POST.get('essencial')
            if essencial is None:
                essencial = False

            equipamento = Equipamento.objects.get(id=equipamento_id)
            comodo = Comodo.objects.get(id=comodo_id)

            comodoEquipamento = ComodoEquipamento.objects.filter(
                comodo = comodo,
                equipamento = equipamento
            )

            maior = 0
            if comodoEquipamento is not None:
                for item in comodoEquipamento:
                    if item.apelido > maior:
                        maior = item.apelido
            
            apelido = 1 + maior
            comodoEquipamento = ComodoEquipamento.objects.create(
                apelido = apelido,
                comodo = comodo,
                equipamento = equipamento
            )

            terminal_id = request.POST.get('terminal_id')
            if terminal_id is not None:
                ComodoSaida.objects.filter(id=terminal_id).update(
                    comodo_equipamento = comodoEquipamento,
                    tempo_min_semana=semana_min,
                    tempo_max_semana=semana_max,
                    tempo_min_feriado=feriado_min,
                    tempo_max_feriado=feriado_max,
                    essencial=essencial
                )
            else:
                energia_id = request.POST.get('energia_id')
                agua_id = request.POST.get('agua_id')

                if energia_id and agua_id:
                    ComodoSaida.objects.filter(id=energia_id).update(
                        comodo_equipamento = comodoEquipamento,
                        tempo_min_semana=semana_min,
                        tempo_max_semana=semana_max,
                        tempo_min_feriado=feriado_min,
                        tempo_max_feriado=feriado_max,
                        essencial=essencial
                    )

                    ComodoSaida.objects.filter(id=agua_id).update(
                        comodo_equipamento = comodoEquipamento,
                        tempo_min_semana=semana_min,
                        tempo_max_semana=semana_max,
                        tempo_min_feriado=feriado_min,
                        tempo_max_feriado=feriado_max,
                        essencial=essencial
                    )


    return redirect('/cadastrar/vincular/equipamento/comodo/selecionar/?comodo_id={}&equipamento_id={}'.format(comodo_id,equipamento_id))

def DesvincularSaidaEquipamento(request,id):
    item = ComodoSaida.objects.get(id = id)

    if item.comodo_equipamento.equipamento.tipo_consumo.id != 3: #id diretamente
        ComodoSaida.objects.filter(id = id).update(
            comodo_equipamento=None,
            essencial=False
        )
    else:
        ComodoSaida.objects.filter(comodo_equipamento = item.comodo_equipamento).update(
            comodo_equipamento=None,
            essencial=False
        )

    if item.comodo_equipamento:
        comodo = item.comodo
        equipamento = item.comodo_equipamento.equipamento
        comodoEquipamento = item.comodo_equipamento

        apelido = comodoEquipamento.apelido
    #     comodo = item.comodo
    #     equipamento = item.equipamento

        comodoEquipamento.delete()

        lista = ComodoEquipamento.objects.filter(comodo=comodo, equipamento = equipamento)
        maior = 0
        if lista is not None:
            for item in lista:
                if item.apelido > maior:
                    maior = item.apelido
            
        if maior > apelido:
            ComodoEquipamento.objects.filter(
                    comodo=comodo,
                    equipamento=equipamento,
                    apelido=maior
                    ).update(apelido=apelido)


    return redirect('/cadastrar/vincular/equipamento/comodo/selecionar/?comodo_id={}&equipamento_id={}'.format(comodo.id,equipamento.id))

def CalcularConsumo(comodo):
    terminais = ComodoSaida.objects.filter(comodo=comodo)
    
    consumo = {'agua_min': 0, 'agua_max': 0, 'energia_min': 0, 'energia_max': 0 }
    for item in terminais:
        if item.saida is not None and item.comodo_equipamento is not None:
            if item.saida.tipo_consumo.id == 1: #Valor Direto
                consumo['agua_min'] = consumo['agua_min'] + ((item.comodo_equipamento.equipamento.consumo_agua/60)  * item.tempo_min_semana)
                consumo['agua_min'] = consumo['agua_min'] + ((item.comodo_equipamento.equipamento.consumo_agua/60)  * item.tempo_min_feriado)

                consumo['agua_max'] = consumo['agua_max'] + ((item.comodo_equipamento.equipamento.consumo_agua/60)  * item.tempo_max_semana)
                consumo['agua_max'] = consumo['agua_max'] + ((item.comodo_equipamento.equipamento.consumo_agua/60)  * item.tempo_max_feriado)
            else:
                consumo['energia_min'] = consumo['energia_min'] + ((item.comodo_equipamento.equipamento.consumo_energia/60)  * item.tempo_min_semana)
                consumo['energia_min'] = consumo['energia_min'] + ((item.comodo_equipamento.equipamento.consumo_energia/60)  * item.tempo_min_feriado)

                consumo['energia_max'] = consumo['energia_max'] + ((item.comodo_equipamento.equipamento.consumo_energia/60)  * item.tempo_max_semana)
                consumo['energia_max'] = consumo['energia_max'] + ((item.comodo_equipamento.equipamento.consumo_energia/60)  * item.tempo_max_feriado )

    if consumo is not None:
        consumo['agua_min'] = round(consumo['agua_min'] * 4.3,2)
        consumo['agua_max'] = round(consumo['agua_max'] * 4.3,2)
        consumo['energia_min'] = round((consumo['energia_min'] * 4.3) / 1000, 2)
        consumo['energia_max'] = round((consumo['energia_max'] * 4.3) / 1000, 2)
    
    return consumo

def ComodoEquipamentoVisualizar(request):
    id = request.GET.get('id')
    if id:
        comodo_equipamento = ComodoEquipamento.objects.get(id=id)
        
        
        if comodo_equipamento.equipamento.tipo_consumo.id != 3: # id Diretamente
            terminal = ComodoSaida.objects.get(comodo_equipamento=comodo_equipamento)
        else:
            terminal = ComodoSaida.objects.filter(
                comodo_equipamento = comodo_equipamento
            )
            
            print(terminal)
            if terminal.count() > 1:
                saida2 =  terminal[1].saida
                apelido2 = terminal[1].apelido
                terminal = terminal[0]
                terminal.saida2 = saida2
                terminal.apelido2 = apelido2
            elif terminal.count() == 1:
                terminal = terminal[0]
            else:
                terminal = None
        
        dados = {
        'titulo': 'Viualizar equipamento',
        'terminal': terminal
        }

    return render(request, 'casas/equipamentoVisualizar.html',dados)

def ComodoEquipamentoAlterar(request):
    id = request.POST.get('id')

    if id:
        semana_min = request.POST.get('semana_min')
        semana_max = request.POST.get('semana_max')
        feriado_min = request.POST.get('feriado_min')
        feriado_max = request.POST.get('feriado_max')

        essencial = request.POST.get('essencial')
        if essencial is None:
            essencial = False

        ComodoSaida.objects.filter(id=id).update(
            tempo_min_semana=semana_min,
            tempo_max_semana=semana_max,
            tempo_min_feriado=feriado_min,
            tempo_max_feriado=feriado_max,
            essencial=essencial
            )
    terminal = ComodoSaida.objects.get(id=id)
                      
    return redirect('/cadastrar/vincular/equipamento/comodo/visualizar/?id={}'.format(terminal.comodo_equipamento.id))