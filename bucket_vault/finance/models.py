# finance/models.py
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

NULLABILITY = {'null': True, 'blank': True}


class Portfolio(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.CharField(default="demo_user", max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Bucket(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="buckets", **NULLABILITY)
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = ("portfolio", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class AccountType(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="account_types", **NULLABILITY)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("portfolio", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class AccountCategory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="account_categories", **NULLABILITY)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("portfolio", "account_type", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.account_type.name} - {self.name}"


class Account(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="accounts", **NULLABILITY)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE, related_name="accounts")
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name="accounts")
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("portfolio", "name")

    def __str__(self):
        return f"{self.portfolio.name} - {self.name}"


class BalanceSnapshot(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="balance_snapshots")
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    snapshot_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("account", "snapshot_date")
        indexes = [
            models.Index(fields=['account', 'snapshot_date']),
            models.Index(fields=['snapshot_date']),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.snapshot_date}: {self.balance}"


class TransactionCategory(models.Model):
    """
    Transaction categories: Salary, Bonus, Food, Transport, etc.
    """
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="transaction_categories",
                                  **NULLABILITY)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)  # Track if it's a system default category

    class Meta:
        verbose_name_plural = "Transaction Categories"
        unique_together = ("portfolio", "name", "type")  # Same name can exist for different types
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.portfolio.name} - {self.type} - {self.name}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  # Credit or Debit
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, related_name="transactions")
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['account', 'date']),
            models.Index(fields=['date', 'category']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} {self.type} {self.amount} - {self.category.name} ({self.account.name})"


# ============ SIGNALS ============

@receiver(post_save, sender=Portfolio)
def create_default_account_types(sender, instance, created, **kwargs):
    if created:
        default_types = ["Bank", "DMAT", "Physical Asset"]
        for account_type_name in default_types:
            AccountType.objects.create(
                portfolio=instance,
                name=account_type_name
            )


@receiver(post_save, sender=Portfolio)
def create_default_buckets(sender, instance, created, **kwargs):
    if created:
        default_buckets = ["Growth", "Safety"]
        for bucket_name in default_buckets:
            Bucket.objects.create(
                portfolio=instance,
                name=bucket_name
            )


@receiver(post_save, sender=Portfolio)
def create_default_account_categories(sender, instance, created, **kwargs):
    if created:
        default_categories = {
            "Bank": ["Savings", "FD"],
            "DMAT": ["Equity", "MF", "SGB"],
            "Physical Asset": ["Real Estate", "Gold"]
        }
        for account_type_name, categories in default_categories.items():
            account_type = AccountType.objects.get(portfolio=instance, name=account_type_name)
            for category_name in categories:
                AccountCategory.objects.create(
                    portfolio=instance,
                    account_type=account_type,
                    name=category_name
                )


@receiver(post_save, sender=Portfolio)
def create_default_transaction_categories(sender, instance, created, **kwargs):
    """
    Create default transaction categories on portfolio creation.
    """
    if created:
        # Income categories
        income_categories = [
            "Salary",
            "Allowance",
            "Bonus",
            "Stock Dividend",
            "MF Dividend",
            "Interest Income",
            "Rental Income",
            "Business Income",
            "Freelance Income",
            "Gift Received",
            "Refund",
            "Other Income"
        ]

        # Expense categories
        expense_categories = [
            "Food & Dining",
            "Groceries",
            "Transportation",
            "Fuel",
            "Household",
            "Utilities",
            "Rent",
            "EMI",
            "Apparel",
            "Beauty & Personal Care",
            "Health & Medical",
            "Education",
            "Self Development",
            "Entertainment",
            "Travel",
            "Shopping",
            "Gifts & Donations",
            "Insurance",
            "Taxes",
            "Investment",
            "Savings",
            "Other Expense"
        ]

        # Transfer category
        transfer_categories = ["Account Transfer", "Wallet Transfer"]

        # Create Income categories
        for cat_name in income_categories:
            TransactionCategory.objects.create(
                portfolio=instance,
                name=cat_name,
                type='Income',
                is_default=True
            )

        # Create Expense categories
        for cat_name in expense_categories:
            TransactionCategory.objects.create(
                portfolio=instance,
                name=cat_name,
                type='Expense',
                is_default=True
            )

        # Create Transfer categories
        for cat_name in transfer_categories:
            TransactionCategory.objects.create(
                portfolio=instance,
                name=cat_name,
                type='Transfer',
                is_default=True
            )


@receiver(post_save, sender=Transaction)
def update_account_balance_on_transaction(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        if instance.type == "Credit":
            account.balance += Decimal(instance.amount)
        elif instance.type == "Debit":
            account.balance -= Decimal(instance.amount)
        account.save(update_fields=['balance'])


@receiver(post_save, sender=Transaction)
def create_daily_balance_snapshot(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        BalanceSnapshot.objects.update_or_create(
            account=account,
            snapshot_date=instance.date,
            defaults={'balance': account.balance}
        )
