from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from .models import Transaction, Budget

def _notify_overrun(user, budget, total_expense):
    """Helper to send the overrun email."""
    difference = total_expense - budget.target_amount
    subject = f"Budget Overrun: {budget.category.name} in {budget.month.strftime('%B %Y')}"
    message = (
        f"Hello {user.username},\n\n"
        f"Your expenses for category \"{budget.category.name}\" in {budget.month.strftime('%B %Y')} have exceeded the budget.\n"
        f"Budget limit: {budget.target_amount}\n"
        f"Total expenses: {total_expense}\n"
        f"Exceeded by: {difference}\n\n"
        "Please review your spending."
    )
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False
    )

def _check_budget_and_notify(user, category, year, month):
    """
    If a budget exists for (user, category, year, month) and is overrun,
    send a notification.
    """
    try:
        budget = Budget.objects.get(
            user=user,
            category=category,
            month__year=year,
            month__month=month
        )
    except Budget.DoesNotExist:
        return

    total_expense = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        category=category,
        date__year=year,
        date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    if total_expense > budget.target_amount:
        _notify_overrun(user, budget, total_expense)

@receiver(post_save, sender=Budget)
def on_budget_created_or_updated(sender, instance, created, **kwargs):
    """
    When a budget is created or updated, check existing transactions
    for that category/month and notify if already overrun.
    """
    year = instance.month.year
    month = instance.month.month
    _check_budget_and_notify(instance.user, instance.category, year, month)

@receiver(post_save, sender=Transaction)
def on_transaction_created(sender, instance, created, **kwargs):
    """
    When a new expense transaction is added, check the corresponding
    budget and notify if it becomes overrun.
    """
    if not created or instance.transaction_type != 'expense':
        return

    year = instance.date.year
    month = instance.date.month
    if instance.category:
        _check_budget_and_notify(instance.user, instance.category, year, month)
