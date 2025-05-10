from django.urls import path

from . import views

app_name = "helloaustin"

urlpatterns = [
    path('', views.helloaustin) ,
]