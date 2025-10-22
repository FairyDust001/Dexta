from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('test-prep/', views.test_prep, name='test_prep'),
    path('judge/', views.judge, name='judge'),
    path('evaluate/', views.evaluate_presentation, name='evaluate_presentation'),

]

