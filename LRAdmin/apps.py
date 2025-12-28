from django.apps import AppConfig


class LradminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'LRAdmin'
    def ready(self):
        pass
