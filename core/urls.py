from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("", views.home, name="home"),
    path("test-prep/", views.test_prep, name="test_prep"),
    path("judge/", views.judge, name="judge"),
    path("grader/", views.grader, name="grader"),
    path("overview/", views.overview, name="overview"),
    path("founder/", views.founder, name="founder"),


    # Roleplay Chat (DECA scenarios)
    path("roleplay_chat/", views.roleplay_chat, name="roleplay_chat"),

    # PDF upload for grading
    path("upload_pdf/", views.upload_pdf, name="upload_pdf"),

    # AI Grader follow-up chat
    path("chat_with_grader/", views.chat_with_grader, name="chat_with_grader"),

    path("realtime_token/", views.realtime_token),

]
