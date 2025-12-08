from django.contrib import admin
from django.urls import path,include
from . import views

app_name = "predictor"
urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('input_form/',views.input_form_view,name='input_form'),
    path('results/',views.prediction_results_view,name='prediction_results'),
]