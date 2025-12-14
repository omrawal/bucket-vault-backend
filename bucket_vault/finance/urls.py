from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.summary, name='summary'),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('create-account/', views.create_new_account, name='create_new_account'),
    path('get-portfolio-list/', views.get_portfolio_list, name='get_portfolio_list'),
    path('create-portfolio/', views.create_new_portfolio, name='create_new_portfolio'),
]
