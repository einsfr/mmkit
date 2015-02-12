from django.core.management import base


class Command(base.BaseCommand):

    def handle(self, *args, **options):
        # А совсем сначала надо будет удалить то, что уже создано
        # Сначала нужно будет создать индекс в указанном в конфигурации подключении
        # Потом - пробежаться по всем установленным приложениям в поисках файла, определяющего mapping'и и создать их
        pass