from rest_framework.decorators import api_view
from rest_framework.response import Response

from finance.models import Transaction, TransactionCategory, TransactionSubcategory
from finance.serializers import TransactionSerializer


@api_view(['GET'])
def transactions_list(request):
    """Recent transactions"""
    portfolio_id = request.query_params.get('portfolio_id',None)
    transaction_queryset = Transaction.objects.filter(account__portfolio_id=portfolio_id)
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
            date=date,
            type=transaction_type,
            amount=amount,
            category_id=category,
            subcategory_id=subcategory,
            note=note,
        )
        transaction.save()
    except Exception as e:
        return Response({'error': str(e)}, status=400)

    return Response(status=201)

@api_view(['GET'])
def get_transaction_types(request):
    """Get all transaction types"""
    transaction_types = [{"name":"Credit", "id": "Credit"}, {"name":"Debit", "id": "Debit"}]

    return Response(transaction_types)

@api_view(['GET'])
def get_transaction_categories(request):
    """Get all transaction categories"""
    portfolio_id = request.query_params.get('portfolio_id', None)
    categories = TransactionCategory.objects.filter(portfolio_id=portfolio_id).values('id', 'name')
    return Response(categories)

@api_view(['GET'])
def get_transaction_subcategories(request):
    """Get all transaction subcategories for a given category"""
    portfolio_id = request.query_params.get('portfolio_id', None)
    subcategories = TransactionSubcategory.objects.filter(portfolio_id=portfolio_id).values('id', 'name')
    return Response(subcategories)
