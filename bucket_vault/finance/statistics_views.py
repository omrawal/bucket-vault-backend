from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from .models import BalanceSnapshot, Transaction, Account

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_metrics(request):
    portfolio_id = request.GET.get('portfolio_id')
    
    # Calculate key metrics
    accounts = Account.objects.filter(portfolio_id=portfolio_id)
    current_networth = sum(acc.balance for acc in accounts)
    
    # Get last month's networth for comparison
    # ... calculation logic
    
    return Response({
        'netWorth': float(current_networth),
        'monthlyChange': 5.2,  # Calculate from BalanceSnapshot
        'avgSavings': 25000,   # Calculate from transactions
        'topCategory': 'Household',  # Most spent category
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_networth_history(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '6months')
    
    # Query BalanceSnapshot grouped by month
    # Return monthly networth data
    
    return Response([
        {'month': 'Jan', 'total_networth': 500000, 'growth_total': 300000, 'safety_total': 200000},
        {'month': 'Feb', 'total_networth': 520000, 'growth_total': 310000, 'safety_total': 210000},
        # ... more months
    ])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_income_expense_trend(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '6months')
    
    # Query Transactions grouped by month for income and expenses
    # Return monthly income and expense data
    
    return Response([
        {'month': 'Jan', 'income': 8000, 'expense': 5000},
        {'month': 'Feb', 'income': 8500, 'expense': 6000},
        # ... more months
    ])

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def get_category_spending(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '3months')
    
    # Query Transactions grouped by category
    # Return spending per category
    
    return Response([
        {'category': 'Food', 'total_spent': 1500},
        {'category': 'Transport', 'total_spent': 800},
        # ... more categories
    ])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_category_trends(request):
    portfolio_id = request.GET.get('portfolio_id')
    category = request.GET.get('category')
    period = request.GET.get('period', '6months')
    
    # Query Transactions for the specified category grouped by month
    # Return monthly spending trend for the category
    
    return Response([
        {'month': 'Jan', 'total_spent': 300},
        {'month': 'Feb', 'total_spent': 250},
        # ... more months
    ])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_balances(request):
    portfolio_id = request.GET.get('portfolio_id')
    
    # Query Accounts and return their balances
    accounts = Account.objects.filter(portfolio_id=portfolio_id)
    
    return Response([
        {'account_name': acc.name, 'balance': float(acc.balance)} for acc in accounts
    ])
