from django.db import models
from django.db import models




# Create your models here.
class CSV(models.Model):
    address = models.CharField(max_length=120,blank=True, unique=True)
    email = models.CharField(max_length=120,blank=True)
    points = models.CharField(max_length=120,blank=True)
    transactions = models.IntegerField(null=True)
    nft = models.IntegerField(null=True)
    balance = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__ (self):
        return self.address

