from django.http import HttpResponse

def index(request):
    import logging
    logger = logging.getLogger("django.oncodash.clinical")
    logging.debug("Serving clinical/index view")
    return HttpResponse("Hello")
