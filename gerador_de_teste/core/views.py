from django.shortcuts import render

# Create your views here.

def Cadastrar(request):
    return render(request, 'cadastrar.html')