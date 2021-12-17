from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/oncoviz/', include('oncoviz.urls')),
    path('', views.home)
] + staticfiles_urlpatterns()
