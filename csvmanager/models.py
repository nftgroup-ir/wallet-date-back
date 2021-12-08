from django.db import models




# Create your models here.


class CSV(models.Model):
    address = models.CharField(max_length=120,blank=True)
    email = models.CharField(max_length=120,blank=True)
    points = models.CharField(max_length=120,blank=True)
    transactions = models.IntegerField(null=True)
    balance = models.FloatField(null=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    def __str__ (self):
        return self.address


class BalanceData(models.Model):
    balance = models.CharField(null=True,max_length=120)
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)


class NFT(models.Model):
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)
    token_address = models.TextField(null = True)
    token_id = models.TextField(null = True)
    block_number_minted = models.TextField(null = True)
    owner_of = models.TextField(null = True)
    block_number = models.TextField(null = True)
    amount = models.IntegerField(null = True)
    contract_type = models.TextField(null = True)
    name = models.TextField(null = True)
    symbol = models.TextField(null = True)
    token_uri = models.TextField(null = True)
    metadata = models.TextField(null = True)
    synced_at = models.DateTimeField(null = True, auto_now_add=True)
    is_valid = models.IntegerField(null =True)
    syncing = models.TextField()
    frozen = models.TextField()

class Transaction(models.Model):
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)
    hash = models.CharField(null=True,max_length=120)
    nonc = models.IntegerField(null=True)
    transaction_index = models.IntegerField(null=True)
    from_address = models.CharField(max_length=120, null=True)
    to_address = models.CharField(max_length=120, null=True)
    value = models.CharField(null=True, max_length=120)
    gas = models.IntegerField(null=True)
    gas_price = models.BigIntegerField(null=True)
    input = models.CharField(max_length=120, null=True)
    receipt_cumulative_gas_used = models.IntegerField(null=True)
    receipt_gas_used = models.IntegerField(null=True)
    receipt_contract_address = models.CharField(max_length=120, null=True)
    receipt_root = models.CharField(max_length=120, null=True)
    receipt_status = models.IntegerField(null=True)
    block_timestamp = models.DateTimeField(auto_now_add=True)
    block_number = models.IntegerField(null=True)
    block_hash = models.CharField(max_length=120, null=True)


class Lottery(models.Model):
    firstname = models.CharField(max_length=120)
    lastname = models.CharField(max_length=120)
    email = models.CharField(max_length=120, unique=True)
    walletaddress = models.CharField(max_length=120, unique=True)

