from django.urls import path

from . import views

import logging
logger = logging.getLogger("django.oncodash.clinical")
logger.debug("Register clinical URLs")

app_name = 'clinical'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.index),
]

