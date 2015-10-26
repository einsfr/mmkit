from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Updates properties of an existing storage.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        pass
