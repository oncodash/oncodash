from django.views.generic import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .serializers import UploadSerializer


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


class UploadViewSet(ViewSet):
    serializer_class = UploadSerializer

    def list(self, request):
        return Response("GET API")

    def create(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        content_type = file_uploaded.content_type
        response = "POST API and you have uploaded a {} file".format(content_type)
        return Response(response)