from rest_framework import serializers
from .models import Account, Transaction, Portfolio, AccountCategory, Bucket

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'user', 'created_at']

class AccountSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    bucket = serializers.CharField(source='bucket.name', read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'category', 'bucket', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)
    type = serializers.CharField(source='transaction.transaction_type', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'date', 'type', 'amount', 'note']

class SummarySerializer(serializers.Serializer):
    total_networth = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    safety_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth_pct = serializers.FloatField()
    safety_pct = serializers.FloatField()
