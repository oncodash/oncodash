from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic import TemplateView
from django.urls import path
from core.views import HelloView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path("hello/", HelloView.as_view(), name='hello'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("", TemplateView.as_view(template_name="index.html")),
    path("admin/", admin.site.urls),
    path("api/explainer/", include("explainer.api.urls")),
    path("api/clinical-overview/", include("clin_overview.api.urls")),
] + staticfiles_urlpatterns()


# django does not handle http errors, front-end needs to do this
urlpatterns += [
    re_path(
        r"(?P<path>.*)$", TemplateView.as_view(template_name="index.html"), name="home"
    )
]
