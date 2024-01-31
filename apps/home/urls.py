from django.urls import path, re_path
from apps.home import views
from apps.home.apis.dashboard import DashboardApis

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # Apis
    path('apis/dashboard', DashboardApis.as_view(), 
        name='apis-dashboard'),

    # Matches any html file
    re_path('^(?!.*\bapis\b).*$', views.pages, name='pages'),
]

