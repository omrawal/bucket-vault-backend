from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer, SummarySerializer


@api_view(['GET'])
def summary(request):
    """Dashboard summary: net worth + bucket totals"""

    # Dummy data - replace with real queries later
    total_networth = 1250345.00
    growth_total = 750000.00
    safety_total = 500345.00

    growth_pct = round((growth_total / total_networth) * 100, 1)
    safety_pct = round((safety_total / total_networth) * 100, 1)

    data = {
        'total_networth': total_networth,
        'growth_total': growth_total,
        'safety_total': safety_total,
        'growth_pct': growth_pct,
        'safety_pct': safety_pct
    }

    serializer = SummarySerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
def accounts_list(request):
    """List all accounts with balances"""
    # Dummy data
    accounts = [
        {'id': 1, 'name': 'HDFC Savings', 'category': 'Bank', 'bucket': 'Safety', 'balance': 250000},
        {'id': 2, 'name': 'Zerodha Equity', 'category': 'DMAT', 'bucket': 'Growth', 'balance': 400000},
        {'id': 3, 'name': 'ICICI FD', 'category': 'Bank', 'bucket': 'Safety', 'balance': 150000},
    ]
    return Response(accounts)


@api_view(['GET'])
def transactions_list(request):
    """Recent transactions"""
    # Dummy data
    transactions = [
        {'id': 1, 'account': 'HDFC Savings', 'date': '2025-12-01', 'type': 'Credit', 'amount': 50000, 'note': 'Salary'},
        {'id': 2, 'account': 'Zerodha Equity', 'date': '2025-12-02', 'type': 'Debit', 'amount': 15000,
         'note': 'Stock Purchase'},
        {'id': 3, 'account': 'HDFC Savings', 'date': '2025-12-03', 'type': 'Debit', 'amount': 2000,
         'note': 'Groceries'},
    ]
    return Response(transactions)

@api_view(['POST'])
def create_new_account(request):
    """Create a new account"""
    print(request.data)
    # Dummy data
    transactions = [
        {'id': 1, 'account': 'HDFC Savings', 'date': '2025-12-01', 'type': 'Credit', 'amount': 50000, 'note': 'Salary'},
        {'id': 2, 'account': 'Zerodha Equity', 'date': '2025-12-02', 'type': 'Debit', 'amount': 15000,
         'note': 'Stock Purchase'},
        {'id': 3, 'account': 'HDFC Savings', 'date': '2025-12-03', 'type': 'Debit', 'amount': 2000,
         'note': 'Groceries'},
    ]
    return Response(HTTP_201_CREATED)
