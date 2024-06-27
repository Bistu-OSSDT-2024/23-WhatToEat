from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('run_python_code/', views.run_python_code, name='run_python_code'),
    path('display_result/', views.display_result, name='display_result'),
]
