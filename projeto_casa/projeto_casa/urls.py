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
from core.pages.gerador_testes import views as gt
from core.pages.casa import views as Cadastro

urlpatterns = [
    path('admin/', admin.site.urls),

    #Pagina inicial
    path('', RedirectView.as_view(url='/home/')),
    path('home/', views.Home),
    path('login/', views.Login),
    path('login/submit',views.SubmitLogin),
    path('logout/',views.Logout),

    #configurar
    path('configurar/menu', gt.MenuConfigurar),
    path('configurar/', gt.Configurar),
    path('configurar/saida/', gt.Saidas),
    path('configurar/saida/excluir/<int:id>/', gt.DeleteSaida),
    path('configurar/nova/saida', gt.AdicionarSaida),
    path('configurar/categorias/submit', gt.SaveCategorias),
    path('configurar/recursos/submit', gt.SaveRecursos),
    path('configurar/categoria/equipamento/submit', gt.SaveCategoriaEquipamento),
    path('configurar/categorias/excluir/<int:id>/', gt.DeleteCategorias),
    path('configurar/recursos/excluir/<int:id>/', gt.DeleteRecursos),
    path('configurar/categoria/equipamento/excluir/<int:id>/', gt.DeleteCategoriaEquipamento),
    path('equipamentos/', gt.Equipamentos),
    path('equipamentos/submit', gt.SaveEquipamentos),
    path('equipamentos/excluir/<int:id>/', gt.DeleteEquipamentos),

    #Casa
    path('listar/', Cadastro.ListarCasas),  
    path('cadastrar/', Cadastro.Cadastrar),
    path('cadastrar/add/casa', Cadastro.AdicionarCasa),
    path('cadastrar/excluir/casa/<int:id>/', Cadastro.DeleteCasa),
    path('visualizar/casa/', Cadastro.VisualizarCasa),
    path('cadastrar/voltar/', Cadastro.VoltarEtapa),
    path('cadastrar/novo/comodo/', Cadastro.NovoComodo),
    path('cadastrar/add/comodo', Cadastro.AdicionarComodo),
    path('cadastrar/excluir/comodo/<int:id>/<int:casa_id>/', Cadastro.DeleteComodo),
    path('cadastrar/vincular/saida', Cadastro.ComodoSaida),#exibe a tela
    path('cadastrar/vincular/comodo/saida', Cadastro.VincularSaida),#tela que executa acao
    path('cadastrar/vincular/equipamento/', Cadastro.VincularEquipamento),
]
