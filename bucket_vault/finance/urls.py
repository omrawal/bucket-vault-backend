from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.summary, name='summary'),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('transactions/', views.transactions_list, name='transactions_list'),
]
