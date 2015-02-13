from django.dispatch import receiver
from django.db.models import signals


@receiver(signals.post_save)
def model_saved(sender, instance, created, raw, *args, **kwargs):
    pass  #  Здесь должна быть передача управления конкретной функции в elastic.py после проверки на то, что класс является потомком индексируемой модели и определения что это - создание или изменение модели


@receiver(signals.post_delete)
def model_deleted(sender, instance, *args, **kwargs):
    pass  #  Здесь тоже передача управления в elastic.py