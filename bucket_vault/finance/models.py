from django.db import models

class AccountType(models.Model):
    name = models.CharField(max_length=50)

class AccountCategory(models.Model):
    name = models.CharField(max_length=50)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)

class Bucket(models.Model):
    name = models.CharField(max_length=20)  # Growth, Safety

class Account(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE)
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=10)  # Credit, Debit
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=200)
