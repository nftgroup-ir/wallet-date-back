from django.db import models




# Create your models here.


class CSV(models.Model):
    address = models.CharField(max_length=120,unique = True)
    total_nfts = models.BigIntegerField(null=True)
    total_Txs = models.BigIntegerField(null=True)
    balance = models.TextField(null=True)
    def __str__ (self):
        return self.address


class BalanceData(models.Model):
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)
    contract_decimals = models.BigIntegerField(null=True) 
    contract_name =  models.TextField(null=True)
    contract_ticker_symbol = models.TextField(null=True)
    contract_address = models.CharField(null=True,max_length=120, unique = True)
    logo_url = models.TextField(null=True)
    last_transferred_at = models.DateTimeField(null=True)
    type = models.TextField(null=True) 
    balance = models.TextField(null=True)
    balance_24h = models.TextField(null= True)
    quote_rate = models.TextField(null=True)
    quote_rate_24h = models.TextField(null=True)
    quote = models.TextField(null=True)
    quote_24h = models.TextField(null=True)


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
    synced_at = models.DateTimeField(null = True)
    is_valid = models.IntegerField(null =True)
    syncing = models.TextField(null = True)
    frozen = models.TextField(null = True)
    field_unique = models.TextField(null = True)


class Transaction(models.Model):
    parent = models.ForeignKey(CSV, on_delete=models.CASCADE)
    hash = models.CharField(null=True,max_length=120, unique = True)
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
    block_timestamp = models.DateTimeField(null=True)
    block_number = models.IntegerField(null=True)
    block_hash = models.CharField(max_length=120, null=True)


class Lottery(models.Model):
    firstname = models.CharField(max_length=120)
    lastname = models.CharField(max_length=120)
    email = models.CharField(max_length=120, unique=True)
    walletaddress = models.CharField(max_length=120, unique=True)

