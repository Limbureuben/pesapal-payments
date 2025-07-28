from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['phone', 'reference', 'pesapal_transaction_id', 'status', 'created_at']
    search_fields = ['phone', 'reference', 'pesapal_transaction_id']
