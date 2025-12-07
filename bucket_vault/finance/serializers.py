from rest_framework import serializers
from .models import Account, Transaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'category', 'bucket', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'date', 'type', 'amount', 'note']

class SummarySerializer(serializers.Serializer):
    total_networth = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    safety_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth_pct = serializers.FloatField()
    safety_pct = serializers.FloatField()
