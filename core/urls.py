from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('test-prep/', views.test_prep, name='test_prep'),
    path('judge/', views.judge, name='judge'),
    # path('roleplay/', views.roleplay_chat, name='roleplay_chat'),  # <-- new view
    path("roleplay_chat/", views.roleplay_chat, name="roleplay_chat"),  # ✅ this must exist
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),

]

