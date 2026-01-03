from ..models import Account


def calculate_total_networth(portfolio_id):
    """Calculate total networth of a given portfolio"""
    total_networth = 0
    accounts = portfolio_id.accounts.all()
    for account in accounts:
        account_balance = account.balance
        total_networth += account_balance
    
    growth_accounts = Account.objects.filter(portfolio=portfolio_id, bucket__name="Growth")
    safety_accounts = Account.objects.filter(portfolio=portfolio_id, bucket__name="Safety")
    growth_total = sum([acc.balance for acc in growth_accounts])
    safety_total = sum([acc.balance for acc in safety_accounts])

    return {
        'total_networth': total_networth,
        'growth_total': growth_total,
        'safety_total': safety_total
        }
