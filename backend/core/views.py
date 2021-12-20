from django.views.generic import View
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


class FrontendRenderView(View):
    """Render view for rendering the front-end content"""
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """GET method to render front-end view

        :param request: request object
        :param type: class: `HttpRequest`
        :return: page rendering to be displayed
        :rtype: HttpResponse
        """
        return render(request, "index.html")
