from django.shortcuts import render


# place holder view
def home(request):
    return render(request, 'index.html')
