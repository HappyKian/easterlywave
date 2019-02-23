"""windygram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from viewer.views import *
from sate.views import SatelliteImageView
from django.views.decorators.csrf import ensure_csrf_cookie

urlpatterns = [
    path('admintown/', admin.site.urls),
    path('windygram', ensure_csrf_cookie(HomepageView.as_view()), name='home'),
    path('satellite', SatelliteImageView.as_view(), name='sate'),
    path('', RedirectView.as_view(pattern_name='home', permanent=True)),
    path('ajax/search', SearchSuggestionView.as_view(), name='search'),
    path('ajax/plot', MakingPlotView.as_view(), name='plot'),
]
