from django import forms
from .models import Transaction, Budget, Category

class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'date', 'amount', 'description','receipt']
    
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        # Order categories by type and then by name for easier selection
        self.fields['category'].queryset = Category.objects.all().order_by('type', 'name')

class BudgetForm(forms.ModelForm):
    # Remove the month field from the form; we assign it automatically from the GET parameter
    class Meta:
        model = Budget
        fields = ['category', 'target_amount']
    
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        # Limit categories to only expense-related categories
        self.fields['category'].queryset = Category.objects.filter(type='expense').order_by('name')
