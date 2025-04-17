from django.apps import AppConfig

class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.transactions'

    def ready(self):
        # Import the signals module so its @receiver handlers are registered
        from . import signals
