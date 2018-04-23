from django.urls import path

from . import views

app_name = 'bitcoin'
urlpatterns = [
    path('30/', views.bitcoin_chart),
]
