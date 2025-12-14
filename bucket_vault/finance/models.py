from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

NULLABILITY = {'null': True, 'blank': True}

class Portfolio(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    #TODO link to User model
    user = models.CharField(default="demo_user", max_length=100)  # Placeholder for User model
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Bucket(models.Model):
    """
    Growth / Safety bucket.
    Linked to specific portfolio.
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="buckets", **NULLABILITY)
    name = models.CharField(max_length=20)  # "Growth", "Safety"

    class Meta:
        unique_together = ("portfolio", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class AccountType(models.Model):
    """
    Bank, DMAT, Physical Asset.
    Linked to specific portfolio.
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="account_types", **NULLABILITY)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("portfolio", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class AccountCategory(models.Model):
    """
    Sub-category: Savings, FD, Equity, MF, SGB, Gold.
    Linked to specific portfolio and account type.
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="account_categories", **NULLABILITY)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("portfolio", "account_type", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.account_type.name} - {self.name}"


class Account(models.Model):
    """
    Concrete account inside a specific portfolio.
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="accounts", **NULLABILITY)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AccountCategory, on_delete=models.PROTECT, related_name="accounts")
    bucket = models.ForeignKey(Bucket, on_delete=models.PROTECT, related_name="accounts")
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("portfolio", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class Transaction(models.Model):
    """
    Transaction linked to account and portfolio.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    date = models.DateField()
    type = models.CharField(max_length=10)  # "Credit", "Debit"
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.date} {self.type} {self.amount} ({self.account.name})"