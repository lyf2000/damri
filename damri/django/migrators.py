"""Migrate raw data to DB services"""
from contextlib import nullcontext

# TODO: add celery caller
from django.db.transaction import atomic


class BaseMigrator:
    ATOMIC = True

    def __call__(self):
        with atomic() if self.ATOMIC else nullcontext():
            self.migrate()

    def migrate(self):
        raise NotImplementedError
