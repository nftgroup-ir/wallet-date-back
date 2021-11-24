from django.db import models




# Create your models here.


class CSV(models.Model):
    address = models.CharField(max_length=120,blank=True)
    email = models.CharField(max_length=120,blank=True)
    points = models.CharField(max_length=120,blank=True)
    transactions = models.IntegerField(null=True)
    balance = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__ (self):
        return self.address


class BalanceData(models.Model):
    balance = models.JSONField()
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)


class NFT(models.Model):
    nft = models.JSONField()
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)


class Transaction(models.Model):
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)
    transaction = models.JSONField()


class Lottery(models.Model):
    firstname = models.CharField(max_length=120)
    lastname = models.CharField(max_length=120)
    email = models.CharField(max_length=120, unique=True)
    walletaddress = models.CharField(max_length=120, unique=True)

