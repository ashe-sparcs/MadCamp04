"""MadCamp04 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from LiberalOverflow import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^register/', views.register),
    url(r'^register_complete/', views.register_complete),
    url(r'^authenticate/.+/.+', views.my_authenticate),
    url(r'^ajax/login/', views.my_login_ajax),
    url(r'^ajax/duplicate/', views.check_duplicate_ajax),
    url(r'^login/', views.my_login),
    url(r'^logout/', views.my_logout),
    url(r'^timetable/', views.timetable),
    url(r'^ajax/add_taken', views.add_taken_ajax),
    url(r'^ajax/delete_taken', views.delete_taken_ajax),
    url(r'^ajax/add_wish', views.add_wish_ajax),
    url(r'^ajax/delete_wish', views.delete_wish_ajax),
]
