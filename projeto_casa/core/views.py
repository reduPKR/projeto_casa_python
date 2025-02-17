from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
from core.models import Casa


def Login(request):
    return render(request, 'login.html', {'titulo':'Login'})

def SubmitLogin(request):
    if request.POST:
        user = request.POST.get('user')
        password = request.POST.get('pass')
        usuario = authenticate(username=user, password=password)
    
        if usuario is not None:
            login(request, usuario)
            return redirect('/home/')
        else:
            messages.error(request,'Usuario ou senha invalido')

    return redirect('/login/')

def Logout(request):
    logout(request) 
    return redirect('/')

@login_required(login_url = '/login/')
def Home(request):
    return render(request, 'home.html', {'titulo':'Home'})


def ListarCasas(request):
    casas = Casa.objects.all().order_by('nome')
    dados = {
        'titulo':'Lista de casas',
        'casas':casas
        }
    return render(request, 'listar.html', dados)


def Menu(request):
    id = request.GET.get('id')
    casa = None
    if id:
        casa = Casa.objects.get(id=id)

    dados = {
        'titulo': 'Visualizar casa',
        'casa': casa,
    }

    return render(request, 'menu.html', dados)