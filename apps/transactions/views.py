import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category, Budget
from .forms import TransactionForm, BudgetForm
from django.db.models import Sum
from datetime import datetime


@login_required
def dashboard_view(request):
    transactions = Transaction.objects.filter(user=request.user)
    income_total = transactions.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense_total = transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    savings = income_total - expense_total

    income_by_cat = transactions.filter(transaction_type='income').values('category__name').annotate(total=Sum('amount'))
    expense_by_cat = transactions.filter(transaction_type='expense').values('category__name').annotate(total=Sum('amount'))

    # Convert lists to JSON strings
    income_labels = json.dumps([item['category__name'] if item['category__name'] else 'Uncategorized' for item in income_by_cat])
    income_values = json.dumps([float(item['total']) for item in income_by_cat])
    expense_labels = json.dumps([item['category__name'] if item['category__name'] else 'Uncategorized' for item in expense_by_cat])
    expense_values = json.dumps([float(item['total']) for item in expense_by_cat])

    context = {
        'income_total': income_total,
        'expense_total': expense_total,
        'savings': savings,
        'income_labels': income_labels,
        'income_values': income_values,
        'expense_labels': expense_labels,
        'expense_values': expense_values,
    }
    return render(request, 'transactions/dashboard.html', context)


@login_required
def transaction_list_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transactions:transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/transaction_form.html', {'form': form})

@login_required
def transaction_edit_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transactions:transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'transactions/transaction_form.html', {'form': form})

@login_required
def transaction_delete_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transactions:transaction_list')
    return render(request, 'transactions/transaction_delete.html', {'transaction': transaction})


@login_required
def report_view(request):
    # Get an optional 'month' value from the GET parameters (expected format: YYYY-MM)
    month_str = request.GET.get('month')
    if month_str:
        try:
            selected_date = datetime.strptime(month_str, '%Y-%m')
            year, month = selected_date.year, selected_date.month
        except ValueError:
            # If parsing fails, fallback to the current month
            now = datetime.now()
            year, month = now.year, now.month
    else:
        now = datetime.now()
        year, month = now.year, now.month

    # Filter transactions based on the selected year and month
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).order_by('-date')

    # Calculate totals
    income_total = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'transactions': transactions,
        'income_total': income_total,
        'expense_total': expense_total,
        # Include the selected year and month to pre-populate the form field
        'selected_year': year,
        'selected_month': month,
    }
    return render(request, 'transactions/report.html', context)


@login_required
def budgeting_view(request):
    # Read the selected month from GET parameters; expected format: YYYY-MM.
    month_str = request.GET.get('month')
    if month_str:
        try:
            # Parse using only year and month.
            selected_date = datetime.strptime(month_str, '%Y-%m')
        except ValueError:
            selected_date = datetime.now()
    else:
        selected_date = datetime.now()
    
    selected_year = selected_date.year
    selected_month = selected_date.month

    # Process the budget creation form (new budget entry)
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            # Use the selected month from the GET parameter (or default to current)
            budget.month = selected_date
            budget.save()
            # Redirect to maintain the selected month in the URL
            return HttpResponseRedirect(f"{reverse('transactions:budgeting')}?month={selected_year}-{selected_month:02d}")
    else:
        form = BudgetForm()
    
    # Filter budgets for the current user by the selected month and year
    budgets = Budget.objects.filter(user=request.user, month__year=selected_year, month__month=selected_month)
    # For each budget, calculate the total expense and difference (target - expense)
    for budget in budgets:
        total_expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            category=budget.category,
            date__year=selected_year,
            date__month=selected_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        # Attach these values to the budget object for template use
        budget.total_expense = total_expense
        budget.difference = budget.target_amount - total_expense

    context = {
        'budgets': budgets,
        'form': form,
        'selected_year': selected_year,
        'selected_month': selected_month,
    }
    return render(request, 'transactions/budgeting.html', context)
