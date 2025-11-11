from django.shortcuts import render

# Create your views here.

def history(request):
    return render(request, 'history.html')

def about(request):
    return render(request, 'about.html')

def predictor(request):
    return render(request, 'predictor.html')

