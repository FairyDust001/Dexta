from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")

def test_prep(request):
    return render(request, "core/test_prep.html")

def judge(request):
    return render(request, "core/judge.html")
# Create your views here.
