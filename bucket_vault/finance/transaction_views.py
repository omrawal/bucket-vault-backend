from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from finance.models import Transaction, TransactionCategory, Account
from finance.serializers import TransactionSerializer


@api_view(['GET'])
def transactions_list(request):
    """Recent transactions"""
    portfolio_id = request.query_params.get('portfolio_id', None)
    transaction_queryset = Transaction.objects.filter(
        account__portfolio_id=portfolio_id
    ).select_related('category', 'account')
    transactions_list = TransactionSerializer(transaction_queryset, many=True).data
    return Response(transactions_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    """Create Income or Expense transaction"""
    try:
        portfolio_id = request.data.get('portfolio_id')
        account_id = request.data.get('account_id')
        date = request.data.get('date')
        transaction_type = request.data.get('type')  # 'Credit' or 'Debit'
        category_id = request.data.get('category')
        amount = request.data.get('amount')
        note = request.data.get('note', '')

        # Validate account belongs to portfolio
        account = Account.objects.get(id=account_id, portfolio_id=portfolio_id)
        category = TransactionCategory.objects.get(id=category_id, portfolio_id=portfolio_id)

        # Validate category type matches transaction type
        if transaction_type == 'Credit' and category.type != 'Income':
            return Response(
                {'error': 'Credit transactions must use Income categories'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif transaction_type == 'Debit' and category.type not in ['Expense', 'Transfer']:
            return Response(
                {'error': 'Debit transactions must use Expense or Transfer categories'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction = Transaction.objects.create(
            account=account,
            date=date,
            type=transaction_type,
            amount=Decimal(amount),
            category=category,
            note=note
        )

        return Response({
            'id': transaction.id,
            'message': 'Transaction created successfully'
        }, status=status.HTTP_201_CREATED)

    except Account.DoesNotExist:
        return Response({'error': 'Invalid account'}, status=status.HTTP_400_BAD_REQUEST)
    except TransactionCategory.DoesNotExist:
        return Response({'error': 'Invalid category'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transfer(request):
    """Create Transfer between two accounts"""
    try:
        portfolio_id = request.data.get('portfolio_id')
        from_account_id = request.data.get('from_account_id')
        to_account_id = request.data.get('to_account_id')
        date = request.data.get('date')
        amount = request.data.get('amount')
        note = request.data.get('note', '')

        # Validate both accounts belong to portfolio
        from_account = Account.objects.get(id=from_account_id, portfolio_id=portfolio_id)
        to_account = Account.objects.get(id=to_account_id, portfolio_id=portfolio_id)

        if from_account_id == to_account_id:
            return Response(
                {'error': 'Cannot transfer to the same account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get "Account Transfer" category
        transfer_category = TransactionCategory.objects.get(
            portfolio_id=portfolio_id,
            type='Transfer',
            name='Account Transfer'
        )

        # Create debit transaction (from account)
        Transaction.objects.create(
            account=from_account,
            date=date,
            type='Debit',
            amount=Decimal(amount),
            category=transfer_category,
            note=f'Transfer to {to_account.name}: {note}'
        )

        # Create credit transaction (to account)
        Transaction.objects.create(
            account=to_account,
            date=date,
            type='Credit',
            amount=Decimal(amount),
            category=transfer_category,
            note=f'Transfer from {from_account.name}: {note}'
        )

        return Response({
            'message': 'Transfer created successfully'
        }, status=status.HTTP_201_CREATED)

    except Account.DoesNotExist:
        return Response({'error': 'Invalid account'}, status=status.HTTP_400_BAD_REQUEST)
    except TransactionCategory.DoesNotExist:
        return Response({'error': 'Transfer category not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_transaction_categories(request):
    """Get transaction categories filtered by type (Income/Expense/Transfer)"""
    portfolio_id = request.query_params.get('portfolio_id', None)
    category_type = request.query_params.get('type', None)  # Income, Expense, Transfer

    filters = {'portfolio_id': portfolio_id}
    if category_type:
        filters['type'] = category_type

    categories = TransactionCategory.objects.filter(**filters).values('id', 'name', 'type').order_by('name')
    return Response(categories)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction_category(request):
    """Allow users to create custom categories"""
    try:
        portfolio_id = request.data.get('portfolio_id')
        name = request.data.get('name')
        category_type = request.data.get('type')  # Income, Expense, Transfer
        description = request.data.get('description', '')

        if category_type not in ['Income', 'Expense', 'Transfer']:
            return Response(
                {'error': 'Type must be Income, Expense, or Transfer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        category = TransactionCategory.objects.create(
            portfolio_id=portfolio_id,
            name=name,
            type=category_type,
            description=description,
            is_default=False
        )

        return Response({
            'id': category.id,
            'name': category.name,
            'type': category.type,
            'message': 'Category created successfully'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
