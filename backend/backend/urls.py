from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/explainer/', include('explainer.api.urls')),
] + staticfiles_urlpatterns()


# django does not handle http errors, front-end needs to do this 
urlpatterns += [
    re_path(r'(?P<path>.*)$', views.FrontendRenderView.as_view(), name='home')
]
