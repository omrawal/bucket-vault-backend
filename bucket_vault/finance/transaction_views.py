from rest_framework.decorators import api_view
from rest_framework.response import Response


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
