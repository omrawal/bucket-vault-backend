from collections import defaultdict
from decimal import Decimal

from rest_framework import status
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

    if not portfolio_id:
        return Response({'error': 'portfolio_id is required'}, status=400)

    # 1. Calculate current net worth
    accounts = Account.objects.filter(portfolio_id=portfolio_id)
    current_networth = accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0')

    # 2. Get previous month's net worth for comparison
    # Get the first day of current month and previous month
    today = datetime.now().date()
    first_of_current_month = today.replace(day=1)
    first_of_previous_month = (first_of_current_month - timedelta(days=1)).replace(day=1)

    # Get latest snapshot for each account in the previous month
    previous_month_balances = BalanceSnapshot.objects.filter(
        account__portfolio_id=portfolio_id,
        snapshot_date__gte=first_of_previous_month,
        snapshot_date__lt=first_of_current_month
    ).values('account').annotate(
        latest_balance=Sum('balance')
    ).aggregate(total=Sum('latest_balance'))['total'] or Decimal('0')

    # Calculate monthly change percentage
    if previous_month_balances > 0:
        monthly_change = float((current_networth - previous_month_balances) / previous_month_balances * 100)
    else:
        monthly_change = 0.0

    # 3. Calculate average monthly savings (Income - Expenses for current month)
    current_month_start = first_of_current_month

    transactions_this_month = Transaction.objects.filter(
        account__portfolio_id=portfolio_id,
        date__gte=current_month_start,
        date__lte=today
    )

    total_income = transactions_this_month.filter(
        type='Credit'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_expenses = transactions_this_month.filter(
        type='Debit'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    avg_savings = float(total_income - total_expenses)

    # 4. Find top spending category this month
    category_spending = Transaction.objects.filter(
        account__portfolio_id=portfolio_id,
        type='Debit',
        date__gte=current_month_start,
        date__lte=today
    ).values('category__name').annotate(
        total_spent=Sum('amount')
    ).order_by('-total_spent')

    top_category = category_spending[0]['category__name'] if category_spending else 'N/A'

    return Response({
        'netWorth': float(current_networth),
        'monthlyChange': round(monthly_change, 2),
        'avgSavings': round(avg_savings, 2),
        'topCategory': top_category,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_networth_history(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '6months')
    if not portfolio_id:
        return Response({'error': 'portfolio_id is required'}, status=400)

     # Calculate date range based on period
    today = datetime.now().date()

    period_map = {
        '3months': timedelta(days=90),
        '6months': timedelta(days=180),
        '1year': timedelta(days=365),
        'all': None,  # No limit
    }
    if period in period_map and period_map[period]:
        start_date = today - period_map[period]
    else:
        earliest = BalanceSnapshot.objects.filter(
            account__portfolio_id=portfolio_id,
        ).order_by('snapshot_date').first()
        start_date = earliest.snapshot_date if earliest else today

    account = Account.objects.filter(portfolio_id=portfolio_id).select_related('bucket')
    account_bucket_map = {acc.id: acc.bucket.name for acc in account}

    snapshots = BalanceSnapshot.objects.filter(
        account__portfolio_id=portfolio_id,
        snapshot_date__gte=start_date,
        snapshot_date__lte=today
    ).annotate(
        month=TruncMonth('snapshot_date')
    ).values('month', 'account__id').annotate(
        total_balance=Sum('balance')
    ).order_by('month')

    monthly_data = defaultdict( lambda :{
        'total_networth': Decimal('0'),
        'growth_total': Decimal('0'),
        'safety_total': Decimal('0')
    } )

    for snapshot in snapshots:
        month_key = snapshot['month'].strftime('%Y-%m')
        balance = snapshot['total_balance']
        bucket = account_bucket_map.get(snapshot['account__id'], 'Unknown')
        monthly_data[month_key]['total_networth'] += balance
        if bucket == 'Growth':
            monthly_data[month_key]['growth_total'] += balance
        elif bucket == 'Safety':
            monthly_data[month_key]['safety_total'] += balance
    # Format response
    response_data = []
    for month, data in sorted(monthly_data.items()):
        response_data.append({
            'month': month,
            'total_networth': float(data['total_networth']),
            'growth_total': float(data['growth_total']),
            'safety_total': float(data['safety_total']),
        })
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_income_expense_trend(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '6months')
    
    # Query Transactions grouped by month for income and expenses
    # Return monthly income and expense data
    income_transactions = Transaction.objects.filter(
        account__portfolio_id=portfolio_id,
        type='Credit'
    )
    expense_transactions = Transaction.objects.filter(
        account__portfolio_id=portfolio_id,
        type='Debit'
    )
    today = datetime.now().date()

    period_map = {
        '3months': timedelta(days=90),
        '6months': timedelta(days=180),
        '1year': timedelta(days=365),
        'all': None,  # No limit
    }
    if period in period_map and period_map[period]:
        start_date = today - period_map[period]
    else:
        earliest = Transaction.objects.filter(
            account__portfolio_id=portfolio_id,
        ).order_by('date').first()
        start_date = earliest.date if earliest else today
    income_data = income_transactions.filter(
        date__gte=start_date,
        date__lte=today
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_income=Sum('amount')
    ).order_by('month')

    expense_data = expense_transactions.filter(
        date__gte=start_date,
        date__lte=today
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_expense=Sum('amount')
    ).order_by('month')

    # Combine income and expense data
    trend_data = {}
    for item in income_data:
        month_key = item['month'].strftime('%Y-%m')
        trend_data[month_key] = {
            'income': float(item['total_income']),
            'expense': 0.0
        }
    for item in expense_data:
        month_key = item['month'].strftime('%Y-%m')
        if month_key in trend_data:
            trend_data[month_key]['expense'] = float(item['total_expense'])
        else:
            trend_data[month_key] = {
                'income': 0.0,
                'expense': float(item['total_expense'])
            }
    # Format response
    response_data = []
    for month in sorted(trend_data.keys()):
        response_data.append({
            'month': month,
            'income': trend_data[month]['income'],
            'expense': trend_data[month]['expense']
        })
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def get_category_spending(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '3months')
    
    # Query Transactions grouped by category
    # Return spending per category
    today = datetime.now().date()

    period_map = {
        '3months': timedelta(days=90),
        '6months': timedelta(days=180),
        '1year': timedelta(days=365),
        'all': None,  # No limit
    }
    if period in period_map and period_map[period]:
        start_date = today - period_map[period]
    else:
        earliest = Transaction.objects.filter(
            account__portfolio_id=portfolio_id,
        ).order_by('date').first()
        start_date = earliest.date if earliest else today
    category_spending = Transaction.objects.filter(
        account__portfolio_id=portfolio_id,
        type='Debit',
        date__gte=start_date,
        date__lte=today
    ).values('category__name').annotate(
        total_spent=Sum('amount')
    ).order_by('-total_spent')

    trend_data = []
    for item in category_spending:
        trend_data.append({
            'category': item['category__name'],
            'amount': float(item['total_spent'])
        })
    return Response(trend_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_category_trends(request):
    portfolio_id = request.GET.get('portfolio_id')
    period = request.GET.get('period', '6months')

    if not portfolio_id:
        return Response({'error': 'portfolio_id is required'}, status=400)

    today = datetime.now().date()

    period_map = {
        '3months': timedelta(days=90),
        '6months': timedelta(days=180),
        '1year': timedelta(days=365),
        'all': None,
    }

    if period in period_map and period_map[period]:
        start_date = today - period_map[period]
    else:
        earliest = Transaction.objects.filter(
            account__portfolio_id=portfolio_id,
        ).order_by('date').first()
        start_date = earliest.date if earliest else today

    monthly_category_spending = Transaction.objects.filter(
        account__portfolio_id=portfolio_id,
        type='Debit',
        date__gte=start_date,
        date__lte=today
    ).annotate(
        month=TruncMonth('date')
    ).values('month', 'category__name').annotate(
        total_spent=Sum('amount')
    ).order_by('month')

    trend_data = defaultdict(dict)
    all_categories = set()

    for item in monthly_category_spending:
        month_key = item['month'].strftime('%b %Y')  # "Jan 2024"
        category = item['category__name']
        amount = float(item['total_spent'] or 0)

        trend_data[month_key][category] = amount
        all_categories.add(category)

    response_data = []
    for month in sorted(trend_data.keys()):
        row = {'month': month}
        for category in all_categories:
            row[category] = trend_data[month].get(category, 0)
        response_data.append(row)

    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_balances(request):
    portfolio_id = request.GET.get('portfolio_id')
    
    # Query Accounts and return their balances
    accounts = Account.objects.filter(portfolio_id=portfolio_id).select_related('bucket')
    
    return Response([
        {
            'account': acc.name,
            'balance': float(acc.balance),
            'bucket': acc.bucket.name,
        }
        for acc in accounts
    ])
