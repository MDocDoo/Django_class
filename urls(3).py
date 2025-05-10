from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from example.core import views as core_views



urlpatterns = [
    path('', views.HomeView.as_view()),
    path('', views.HomeView.as_view(), name='home'),


]



