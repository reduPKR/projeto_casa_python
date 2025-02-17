"""projeto_casa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from core import views
from core.pages.configuracoes import views as configurar
from core.pages.casa import views as cadastro
from core.pages.gerador_testes import views as gerarTeste
from core.pages.simulacao import views as simular
from core.pages.simulacao.execucao import views as tempo_exec
from core.pages.regressao_linear import views as regressao
from core.pages.genetico import views as genetico
from core.pages.categoria import views as categoria
from core.pages.comparar import views as comparar

urlpatterns = [
    path('admin/', admin.site.urls),

    #Pagina inicial
    path('', RedirectView.as_view(url='/home/')),
    path('home/', views.Home),
    path('login/', views.Login),
    path('login/submit',views.SubmitLogin),
    path('logout/',views.Logout),
    path('listar/', views.ListarCasas),
    path('menu/', views.Menu),

    #Configurar
    path('configurar/menu', configurar.MenuConfigurar),
    path('configurar/', configurar.Configurar),
    path('configurar/saida/', configurar.Saidas),
    path('configurar/saida/excluir/<int:id>/', configurar.DeleteSaida),
    path('configurar/nova/saida', configurar.AdicionarSaida),
    path('configurar/recursos/submit', configurar.SaveRecursos),
    path('configurar/categoria/equipamento/submit', configurar.SaveCategoriaEquipamento),
    path('configurar/recursos/excluir/<int:id>/', configurar.DeleteRecursos),
    path('configurar/categoria/equipamento/excluir/<int:id>/', configurar.DeleteCategoriaEquipamento),
    path('equipamentos/', configurar.Equipamentos),
    path('equipamentos/submit', configurar.SaveEquipamentos),
    path('equipamentos/excluir/<int:id>/', configurar.DeleteEquipamentos),

    #Casa
    #path('listar/', cadastro.ListarCasas),
    path('cadastrar/', cadastro.Cadastrar),
    path('cadastrar/add/casa', cadastro.AdicionarCasa),
    path('cadastrar/excluir/casa/<int:id>/', cadastro.DeleteCasa),
    path('visualizar/casa/', cadastro.VisualizarCasa),
    path('cadastrar/voltar/', cadastro.VoltarEtapa),
    path('cadastrar/novo/comodo/', cadastro.NovoComodo),
    path('cadastrar/add/comodo', cadastro.AdicionarComodo),
    path('cadastrar/excluir/comodo/<int:id>/<int:casa_id>/', cadastro.DeleteComodo),
    path('cadastrar/vincular/saida/', cadastro.ListarComodoSaida),#exibe a tela
    path('cadastrar/vincular/comodo/saida/', cadastro.VincularSaida),#tela que executa acao
    path('cadastrar/vincular/comodo/saida/adicionar', cadastro.AdicionarSaidaComodo),
    path('cadastrar/vincular/comodo/saida/excluir/<int:id>/', cadastro.DeleteSaidaComodo),
    path('cadastrar/vincular/equipamento/', cadastro.ListarComodoEquipamento),
    path('cadastrar/vincular/equipamento/comodo/', cadastro.VincularEquipamento),
    path('cadastrar/vincular/equipamento/comodo/selecionar/', cadastro.ComodoEquipamentos),
    path('cadastrar/vincular/equipamento/comodo/adicionar', cadastro.AdicionarSaidaEquipamento),
    path('cadastrar/desvincular/equipamento/comodo/<int:id>/', cadastro.DesvincularSaidaEquipamento),
    path('cadastrar/vincular/equipamento/comodo/visualizar/', cadastro.ComodoEquipamentoVisualizar),
    path('cadastrar/vincular/equipamento/comodo/alterar', cadastro.ComodoEquipamentoAlterar),

    #Gerar testes
    #path('gerar-testes/casas/', gerarTeste.ListarCasas),
    path('gerar-testes/gerar/', gerarTeste.Gerar),    
    path('gerar-testes/gerar/automatico/', gerarTeste.GerarAutomatico),
    path('gerar-testes/gerar/manual/', gerarTeste.GerarManual),
    path('gerar-testes/gerar/manual/selecionar/', gerarTeste.GerarManualSelecionar),
    path('gerar-testes/gerar/manual/selecionar/cadastar', gerarTeste.GerarManualCadastrar),
    path('gerar-testes/gerar/manual/selecionar/finalizar', gerarTeste.GerarAnoManual),

    #Simulacao
    #path('simular/casas/', simular.ListarCasas),
    path('simular/meses/', simular.ListarMeses),
    path('simular/algoritmos/', simular.Algoritmos),
    path('simular/testar/', simular.ListaCoeficientes),
    path('simular/selecionar/executar', simular.Executar),
    path('simular/selecionar/executar/tempo', tempo_exec.Executar),
    path('simular/selecionar/leitura', tempo_exec.ler_dados),
    path('simular/selecionar/voltar', tempo_exec.voltar),

    #categorias
    path('simular/gerar/categoria', categoria.Exibir),
    path('simular/categorizar', categoria.GerarCategorias),

    #comparacoes
    path('simular/selecionar/meta', comparar.Exibir),
    path('simular/selecionar/coeficientes', comparar.Selecionar),
    path('simular/excecucao/selecionar/coeficientes', comparar.SelecionarExecucao),
    path('simular/selecionar/comparar', comparar.Comparar),

    #regressao linear
    path('regressao-linear-multipla/coeficiente', regressao.Exibir),
    path('regressao-linear-multipla/coeficiente/treinar', regressao.Treinar),

    #Algoritmo genetico
    path('genetico/', genetico.Exibir),
    path('genetico/novos', genetico.genetico),


]
