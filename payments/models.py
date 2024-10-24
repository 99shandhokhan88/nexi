from django.db import models

class Transaction(models.Model):
    transaction_code = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default='EUR')
    authorization_code = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_code
