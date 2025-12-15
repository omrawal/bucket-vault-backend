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

class BalanceSnapshot(models.Model):
    """
    Point-in-time balance snapshot for analytics and historical tracking.
    Allows balance growth analysis by month/year without recalculating from transactions.
    """
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
    Main transaction categories: Income, Expense, Transfer, Investment.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Transaction Categories"

    def __str__(self):
        return self.name


class TransactionSubcategory(models.Model):
    """
    Subcategories linked to main categories.
    E.g., Income: Salary, Stock Profit; Expense: Household, Travel
    """
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("category", "name")
        verbose_name_plural = "Transaction Subcategories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    date = models.DateField()
    type = models.CharField(max_length=10)  # "Credit", "Debit"
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(TransactionCategory, on_delete=models.PROTECT, related_name="transactions")
    subcategory = models.ForeignKey(TransactionSubcategory, on_delete=models.PROTECT, related_name="transactions")
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['account', 'date']),
            models.Index(fields=['date', 'category']),
        ]

    def __str__(self):
        return f"{self.date} {self.type} {self.amount} ({self.account.name})"



@receiver(post_save, sender=Portfolio)
def create_default_account_types(sender, instance, created, **kwargs):
    """
    Create default account types when a new portfolio is created.
    """
    if created:
        default_types = ["Bank", "DMAT", "Physical Asset"]
        for account_type_name in default_types:
            AccountType.objects.create(
                portfolio=instance,
                name=account_type_name
            )

@receiver(post_save, sender=Portfolio)
def create_default_buckets(sender, instance, created, **kwargs):
    """
    Create default buckets when a new portfolio is created.
    """
    if created:
        default_buckets = ["Growth", "Safety"]
        for bucket_name in default_buckets:
            Bucket.objects.create(
                portfolio=instance,
                name=bucket_name
            )

@receiver(post_save, sender=Portfolio)
def create_default_account_categories(sender, instance, created, **kwargs):
    """
    Create default account categories when a new portfolio is created.
    """
    if created:
        default_categories = {
            "Bank": ["Savings", "FD"],
            "DMAT": ["Equity", "MF", "SGB", ],
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
    Create default transaction categories and subcategories on portfolio creation.
    """
    if created:
        default_categories = {
            "Income": ["Salary", "Stock Profit", "Bonus"],
            "Expense": ["Household", "Travel", "Medical", "Entertainment"],
            "Transfer": ["Account Transfer"],
            "Investment": ["Stock Purchase", "MF Investment", "SGB Purchase"]
        }
        for category_name, subcategories in default_categories.items():
            category, _ = TransactionCategory.objects.get_or_create(name=category_name)
            for subcategory_name in subcategories:
                TransactionSubcategory.objects.get_or_create(
                    category=category,
                    name=subcategory_name
                )


@receiver(post_save, sender=Transaction)
def update_account_balance_on_transaction(sender, instance, created, **kwargs):
    """
    Update account balance when a transaction is created or modified.
    """
    if created:
        account = instance.account
        if instance.type == "Credit":
            account.balance += instance.amount
        elif instance.type == "Debit":
            account.balance -= instance.amount
        account.save(update_fields=['balance'])


@receiver(post_save, sender=Transaction)
def create_daily_balance_snapshot(sender, instance, created, **kwargs):
    """
    Create a balance snapshot at end of each day for analytics.
    """
    if created:
        account = instance.account
        BalanceSnapshot.objects.update_or_create(
            account=account,
            snapshot_date=instance.date,
            defaults={'balance': account.balance}
        )