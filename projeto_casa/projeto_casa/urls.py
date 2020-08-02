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

urlpatterns = [
    path('admin/', admin.site.urls),

    #Pagina inicial
    path('', RedirectView.as_view(url='/home/')),
    path('home/', views.Home),
    path('login/', views.Login),
    path('login/submit',views.SubmitLogin),
    path('logout/',views.Logout),

    #Gerador de teste
    path('listar/', gt.ListarCasas),  
    path('configurar/', gt.Configurar),
    path('configurar/categorias/submit', gt.SaveCategorias),
    path('equipamentos/', gt.Equipamentos),
    path('cadastrar/', gt.Cadastrar),
]
