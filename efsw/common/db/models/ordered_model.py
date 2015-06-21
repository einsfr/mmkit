# Некоторые идеи взяты отсюда: https://github.com/bfirsh/django-ordered-model/blob/master/ordered_model/models.py

from django.db import models
from django.db.models import Max, F


class OrderedModel(models.Model):

    class Meta:
        ordering = ['order']
        abstract = True

    MIN_ORDER_VALUE = 0

    order = models.PositiveIntegerField(
        db_index=True,
        editable=False,
        verbose_name='порядок'
    )

    def _get_max_order(self):
        return type(self).objects.aggregate(Max('order')).get('order__max')

    def save(self, *args, **kwargs):
        if self.order is not None and self.order < self.MIN_ORDER_VALUE:
            self.order = self.MIN_ORDER_VALUE
        if self.pk is not None:
            # Если уже установлен первичный ключ, то, возможно - это редактирование существующего объекта
            try:
                old_order = type(self).objects.filter(pk=self.pk).values_list('order', flat=True)[0]
            except IndexError:
                old_order = None
            if old_order is None:
                # Значит - это всё-таки добавление нового, а pk взялся непонятно откуда
                if self.order is None:
                    # Нужно сунуть в конец
                    max_order = self._get_max_order()
                    self.order = self.MIN_ORDER_VALUE if max_order is None else max_order + 1
                else:
                    # Нужно посмотреть внимательней - куда ставить
                    max_order = self._get_max_order()
                    if self.order > max_order + 1:
                        # слишком большое значение порядка, но зато двигать не нужно
                        self.order = max_order + 1
                    elif self.order < max_order + 1:
                        # ну а здесь нужно подвигать вперёд всё, что справа от нового места
                        type(self).objects.select_for_update().filter(
                            order__gte=self.order
                        ).update(order=F('order') + 1)
            else:
                # Значит - обновление существующего
                if self.order is None:
                    # Нужно сунуть в конец
                    if old_order < self._get_max_order():
                        # нужно двигать назад всё, что справа от старого места
                        type(self).objects.select_for_update().filter(
                            order__gt=old_order
                        ).update(order=F('order') - 1)
                    self.order = self._get_max_order()
                else:
                    # Нужно разобраться - куда кого девать
                    if self.order > old_order:
                        # если сдвиг вправо
                        max_order = self._get_max_order()
                        if self.order > max_order + 1:
                            # выехал за пределы порядка - ничего двигать не надо
                            self.order = max_order + 1
                        else:
                            # иначе - двигаем всё, что находится между старым и новым местом влево
                            type(self).objects.select_for_update().filter(
                                order__gt=old_order,
                                order__lte=self.order
                            ).update(order=F('order') - 1)
                    elif self.order < old_order:
                        # если сдвиг влево - двигаем всё, что находится между старым и новым местом вправо
                        type(self).objects.select_for_update().filter(
                            order__gte=self.order,
                            order__lt=old_order
                        ).update(oder=F('order') + 1)
        else:
            # Это добавление нового объекта
            max_order = self._get_max_order()
            if self.order is None:
                # Нужно сунуть в конец
                self.order = self.MIN_ORDER_VALUE if max_order is None else max_order + 1
            else:
                if max_order is None:
                    # если ещё нет ни одного объекта
                    self.order = self.MIN_ORDER_VALUE
                elif self.order > max_order + 1:
                    # выехал за пределы порядка - ничего двигать не надо
                    self.order = max_order + 1
                else:
                    # нужно подвинуть вправо, что справа от нового места
                    type(self).objects.select_for_update().filter(
                        order__gte=self.order
                    ).update(order=F('order') + 1)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        type(self).objects.select_for_update().filter(order__gt=self.order).update(order=F('order') - 1)
        super().delete(*args, **kwargs)
