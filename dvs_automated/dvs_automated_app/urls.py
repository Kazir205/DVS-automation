"""
URL configuration for dvs_automated project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from dvs_automated_app.views import index, upload_csv, filter_data, header, visualize_data
#display_csv

urlpatterns = [
    # path('', index, name='index'),
    path('', upload_csv, name='upload_csv'),
    path('header/', header, name='header'),
    path('filter_data/', filter_data, name='filter_data'),
    path('visualize_data/', visualize_data, name='visualize_data')
]
