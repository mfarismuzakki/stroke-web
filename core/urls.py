# -*- encoding: utf-8 -*-
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include  # add this

urlpatterns = [
    # Leave `Home.Urls` as last the last line
    path("", include("apps.home.urls"))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)