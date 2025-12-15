from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from finance.models import Account, AccountType, Bucket, AccountCategory
from finance.serializers import AccountSerializer


@api_view(['GET'])
def get_all_accounts(request):
    """List all accounts with balances"""
    
    portfolio_id = request.query_params.get('portfolio_id', None)
    account_queryset = Account.objects.filter(portfolio_id=portfolio_id)
    serialized_accounts = AccountSerializer(account_queryset, many=True).data
    return Response(serialized_accounts)


@api_view(['POST'])
def create_new_account(request):
    """Create a new account"""
    print(request.data)
    account_name = request.data.get('name', None)
    account_category_id = request.data.get('category_id', None)
    account_bucket_id = request.data.get('bucket_id', None)
    account_balance = request.data.get('balance', 0)
    portfolio_id = request.data.get('portfolio_id', None)

    try:
        account = Account.objects.create(
            name=account_name,
            category_id=account_category_id,
            bucket_id=account_bucket_id,
            portfolio_id=portfolio_id,
            balance=account_balance,
        )
        account.save()
    except Exception as e:
        return Response({'error': str(e)}, status=400)

    return Response(HTTP_201_CREATED)

@api_view(['GET'])
def get_account_types(request):
    """List all account types"""
    portfolio_id = request.query_params.get('portfolio_id', None)

    account_types =AccountType.objects.filter(portfolio_id=portfolio_id).values('id', 'name')
    # Alternatively, if you want to use the serializer method:
    account_serialized_types = AccountSerializer(account_types, many=True)

    return Response(account_types)

@api_view(['GET'])
def get_bucket_types(request):
    """List all bucket types"""
    portfolio_id = request.query_params.get('portfolio_id', None)
    buckets = Bucket.objects.filter(portfolio_id=portfolio_id).values('id', 'name')
    return Response(buckets)

@api_view(['GET'])
def get_account_categories(request):
    """List all account categories"""
    portfolio_id = request.query_params.get('portfolio_id', None)
    account_categories = AccountCategory.objects.filter(portfolio_id=portfolio_id).values('id', 'name')
    return Response(account_categories)