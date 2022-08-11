from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic import TemplateView


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("clinical/", include("clinical.urls")),
    path("admin/", admin.site.urls),
    path("api/explainer/", include("explainer.api.urls")),
    path("api/clinical/", include("clinical.api.urls")),
] + staticfiles_urlpatterns()


# django does not handle http errors, front-end needs to do this
urlpatterns += [
    re_path(
        r"(?P<path>.*)$", TemplateView.as_view(template_name="index.html"), name="home"
    )
]
