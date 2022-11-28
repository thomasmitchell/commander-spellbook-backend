from django.apps import AppConfig
try:
    import psycopg2
except ImportError:
    # Fall back to psycopg2cffi
    from psycopg2cffi import compat
    compat.register()


class SpellbookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spellbook'

    def ready(self):
        from . import signals
