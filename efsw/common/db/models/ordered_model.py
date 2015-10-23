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

    order_domain_field = ''

    def _get_order_domain_value(self):
        return getattr(self, self.order_domain_field)

    def _get_order_domain_qs(self, qs=None):
        qs = qs if qs is not None else type(self).objects.all()
        if self.order_domain_field:
            qs = qs.filter((self.order_domain_field, self._get_order_domain_value()))
        return qs

    def _get_max_order(self):
        return self._get_order_domain_qs().aggregate(Max('order')).get('order__max')

    def _insert_new(self):
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
                self._get_order_domain_qs(type(self).objects.select_for_update().filter(
                    order__gte=self.order
                )).update(order=F('order') + 1)

    def save(self, skip_reorder=False, *args, **kwargs):
        if not skip_reorder:
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
                    self._insert_new()
                else:
                    # Значит - обновление существующего
                    if self.order is None:
                        # Нужно сунуть в конец
                        max_order = self._get_max_order()
                        if old_order < max_order:
                            # нужно двигать назад всё, что справа от старого места
                            self._get_order_domain_qs(type(self).objects.select_for_update().filter(
                                order__gt=old_order
                            )).update(order=F('order') - 1)
                        self.order = max_order
                    else:
                        # Нужно разобраться - куда кого девать
                        if self.order > old_order:
                            # если сдвиг вправо
                            max_order = self._get_max_order()
                            if self.order > max_order:
                                # выехал за пределы порядка
                                self.order = max_order
                            # двигаем всё, что находится между старым и новым местом влево
                            self._get_order_domain_qs(type(self).objects.select_for_update().filter(
                                order__gt=old_order,
                                order__lte=self.order
                            )).update(order=F('order') - 1)
                        elif self.order < old_order:
                            # если сдвиг влево - двигаем всё, что находится между старым и новым местом вправо
                            self._get_order_domain_qs(type(self).objects.select_for_update().filter(
                                order__gte=self.order,
                                order__lt=old_order
                            )).update(order=F('order') + 1)
            else:
                # Это добавление нового объекта
                self._insert_new()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._get_order_domain_qs(type(self).objects.filter(order__gt=self.order)).update(order=F('order') - 1)
        super().delete(*args, **kwargs)

    def order_swap(self, swap_with):
        if type(swap_with) != type(self):
            raise ValueError(
                'Можно менять местами только объекты одного класса, предоставлены: {0}, {1}.'.format(
                    type(self),
                    type(swap_with)
                )
            )
        if self.pk is None or swap_with.pk is None:
            raise ValueError('Перед тем, как менять объекты местами, их необходимо сохранить.')
        if self._get_order_domain_qs(
                type(self).objects.select_for_update().filter(pk__in=[self.pk, swap_with.pk])
        ).count() != 2:
            raise ValueError('Перед тем, как менять объекты местами, их необходимо сохранить.')
        self.order, swap_with.order = swap_with.order, self.order
        self.save(skip_reorder=True)
        swap_with.save(skip_reorder=True)

    @classmethod
    def order_check(cls, order_domain_field=None):
        if order_domain_field is None:
            order_list = list(cls.objects.order_by('order', '-id').values_list('id', 'order'))
            if not order_list or len(order_list) == 1:
                return
            for k, v in enumerate(order_list):
                if k + cls.MIN_ORDER_VALUE != v[1]:
                    cls.objects.filter(pk=v[0]).update(order=k + cls.MIN_ORDER_VALUE)
        else:
            order_domain_values = list(
                cls.objects.order_by(order_domain_field).distinct(order_domain_field).values_list('order', flat=True)
            )
            for odv in order_domain_values:
                order_list = list(
                    cls.objects.filter((order_domain_field, odv)).order_by('order', '-id').values_list('id', 'order')
                )
                if not order_list or len(order_list) == 1:
                    continue
                for k, v in enumerate(order_list):
                    if k + cls.MIN_ORDER_VALUE != v[1]:
                        cls.objects.filter(pk=v[0]).update(order=k + cls.MIN_ORDER_VALUE)
