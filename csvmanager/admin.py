from django.contrib import admin
from .models import *
from django.contrib import admin


mymodels=[CSV, BalanceData, NFT, Transaction, Lottery]
# Register your models here.
admin.site.register(mymodels)


