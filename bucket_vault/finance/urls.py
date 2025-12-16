from django.urls import path
from .portfolio_views import (
    portfolios_list, get_portfolio_list, create_new_portfolio, delete_portfolio
)
from .account_views import create_new_account, get_account_types, get_all_accounts, get_bucket_types, \
    get_account_categories
from .transaction_views import transactions_list, create_transaction, get_transaction_types, get_transaction_categories, \
    get_transaction_subcategories
from .dashboard_views import summary

urlpatterns = [
    # Dashboard
    path('summary/', summary, name='summary'),
    
    # Portfolios
    path('portfolios/', portfolios_list, name='portfolios_list'),
    path('get-portfolio-list/', get_portfolio_list, name='get_portfolio_list'),
    path('create-portfolio/', create_new_portfolio, name='create_new_portfolio'),
    path('delete-portfolio/<int:portfolio_id>/', delete_portfolio, name='delete_portfolio'),
    
    # Accounts
    path('get-all-accounts/', get_all_accounts, name='get_all_accounts'),
    path('create-account/', create_new_account, name='create_new_account'),
    path('get-account-types/', get_account_types, name='get_account_types'),
    path('get-bucket-types/', get_bucket_types, name='get_bucket_types'),
    path('get-account-categories/', get_account_categories, name='get_account_categories'),


    # Transactions
    path('get-all-transactions/', transactions_list, name='get-all-transactions'),
    path('create-transaction/', create_transaction, name='create_transaction'),
    path('get-transaction-types/', get_transaction_types, name='get_transaction_types'),
    path('get-transaction-categories/', get_transaction_categories, name='get_transaction_categories'),
    path('get-transaction-subcategories/', get_transaction_subcategories, name='get_transaction_subcategories'),
]
