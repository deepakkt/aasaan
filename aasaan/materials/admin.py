from django.contrib import admin
from .models import LoanTransaction, ItemMaster, Transaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(ItemMaster)
admin.site.register(LoanTransaction)
