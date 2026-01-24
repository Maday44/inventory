from django.apps import AppConfig

# from .signals import *


class StorageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "storage"

    def ready(self):
        import storage.signals
