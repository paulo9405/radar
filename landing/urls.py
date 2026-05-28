from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),
    path('confirmacao/', views.confirmation, name='confirmation'),
    # API endpoints
    path('api/check-limit/', views.check_analysis_limit, name='check_analysis_limit'),
    path('api/submit-contact/', views.submit_contact, name='submit_contact'),
    path('api/submit-feedback/', views.submit_feedback, name='submit_feedback'),
]
