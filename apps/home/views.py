# -*- encoding: utf-8 -*-
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.home.apis.dashboard import DashboardApis


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]        
        context['segment'] = load_template
                
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('defaults/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('defaults/page-500.html')
        return HttpResponse(html_template.render(context, request))
