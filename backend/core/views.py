from django.shortcuts import render


def home(request):
    """ 
    Place holder view

    :param request: request object
    :return: page rendering to be displayed
    """
    return render(request, 'index.html')
