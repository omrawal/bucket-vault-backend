# This file has been refactored into separate view modules:
# - portfolio_views.py: Portfolio management views
# - account_views.py: Account management views
# - transaction_views.py: Transaction views
# - dashboard_views.py: Dashboard summary views

# For backwards compatibility, import all views here
from .portfolio_views import (
    portfolios_list,
    get_portfolio_list,
    create_new_portfolio,
    delete_portfolio,
)
from .account_views import accounts_list, create_new_account
from .transaction_views import transactions_list
from .dashboard_views import summary

__all__ = [
    'portfolios_list',
    'get_portfolio_list',
    'create_new_portfolio',
    'delete_portfolio',
    'accounts_list',
    'create_new_account',
    'transactions_list',
    'summary',
]
    
