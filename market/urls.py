from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('test/', views.test_analysis, name='test'),

    # Mercado Livre OAuth
    path('mercadolivre/authorize/', views.ml_authorize, name='ml_authorize'),
    path('mercadolivre/callback/', views.ml_callback, name='ml_callback'),
    path('mercadolivre/status/', views.ml_status, name='ml_status'),
]
