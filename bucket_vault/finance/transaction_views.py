from rest_framework.decorators import api_view
from rest_framework.response import Response

from finance.models import Transaction
from finance.serializers import TransactionSerializer


@api_view(['GET'])
def transactions_list(request):
    """Recent transactions"""
    portfolio_id = request.query_params.get('portfolio_id',None)
    transaction_queryset = Transaction.objects.filter(portfolio_id=portfolio_id)
    transactions_list = TransactionSerializer(transaction_queryset, many=True).data
    return Response(transactions_list)


@api_view(['POST'])
def create_transaction(request):
    """Create a new transaction"""
    print(request.data)
    portfolio_id = request.data.get('portfolio_id', None)
    account_id = request.data.get('account_id', None)
    date = request.data.get('date', None)
    transaction_type = request.data.get('type', None)
    amount = request.data.get('amount', 0)
    category = request.data.get('category', None)
    subcategory = request.data.get('subcategory', None)
    note = request.data.get('note', "")

    try:
        transaction = Transaction.objects.create(
            account_id=account_id,
            category_id=category,
            subcategory_id=subcategory,
            date=date,
            type=transaction_type,
            amount=amount,
            note=note,
            portfolio_id=portfolio_id,
        )
        transaction.save()
    except Exception as e:
        return Response({'error': str(e)}, status=400)

    return Response(status=201)