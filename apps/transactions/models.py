from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Choices for transaction type
TRANSACTION_TYPES = (
    ('income', 'Income'),
    ('expense', 'Expense'),
)

class Category(models.Model):
    name = models.CharField(max_length=100)
    # 'type' distinguishes between income and expense categories
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    
    def __str__(self):
        return f"{self.name} ({self.type})"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    # Allow the category to be empty if not required
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    # Receipt upload 
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} on {self.date}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # This field represents a date within the month the budget applies
    month = models.DateField(help_text="Choose a date in the month for which this budget applies")
    
    def __str__(self):
        return f"Budget for {self.category.name}: {self.target_amount}"

# Automatically create default categories for income and expenses after migrations run
@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    # Only run for the transactions app
    if sender.name == 'apps.transactions':
        default_income = ["Salary", "Stock yields", "Rental income", "Passive income"]
        default_expense = ["Food", "Household items", "School and college fees", "Personal use", "Extra expenses"]
        for cat in default_income:
            Category.objects.get_or_create(name=cat, type='income')
        for cat in default_expense:
            Category.objects.get_or_create(name=cat, type='expense')
