from django.views.generic import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
      
       

class FrontendRenderView(View):
    """Render view for rendering the front-end content"""
    
    def get(self, request, *args, **kwargs):
        """GET method to render front-end view

        :param request: request object
        :param type: class: `HttpRequest`
        :return: page rendering to be displayed
        :rtype: HttpResponse
        """
        return render(request, "index.html")


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response('User Logged out successfully')

