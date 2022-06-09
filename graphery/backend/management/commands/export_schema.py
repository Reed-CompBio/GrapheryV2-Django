from django.core.management import BaseCommand
from strawberry.printer import print_schema

from ...schema import schema  # import your schema here


class Command(BaseCommand):
    help = "Exports the strawberry graphql schema"

    def handle(self, *args, **options):
        print(print_schema(schema))
